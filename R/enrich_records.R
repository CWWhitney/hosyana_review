# ============================================================
# Fill missing abstracts + DOIs for INCLUDED records,
# then CHECK every DOI against Crossref.
#
# Run after prisma_pipeline.R:  Rscript R/enrich_records.R
# Test on a random sample:      LIMIT=100 Rscript R/enrich_records.R
#
# Flow:
#   A. OpenAlex by DOI       -> abstracts
#   B. OpenAlex title search -> DOI + abstract for records with no DOI
#   C. Crossref title search -> DOI for records still without one
#   D. Crossref by DOI       -> VERIFY every DOI (+ abstract fallback)
#
# Rules:
#   - never overwrite what we already have
#   - a DOI found by title is accepted only if title, year, author match
#   - every record gets a crossref_status flag (see step 8)
#   - API answers are cached: a re-run only fetches what is missing
# ============================================================

library(dplyr)
library(stringr)
library(readr)
library(purrr)
library(tibble)
library(httr2)
library(stringdist)

# ------------------------------------------------------------
# 0. SETTINGS
# ------------------------------------------------------------

oa_url  <- "https://api.openalex.org/works"
cr_url  <- "https://api.crossref.org/works"
cache_f <- "data/prisma/api_cache.rds"
min_sim <- 0.95   # title similarity to ACCEPT a DOI found by title
ver_sim <- 0.90   # title similarity to call a DOI "verified"
limit   <- suppressWarnings(as.integer(Sys.getenv("LIMIT", NA)))
ua      <- "hosyana-review-enrichment (R httr2)"

# ------------------------------------------------------------
# 1. CACHE (named list on disk)
# keys: D: openalex doi batch | S: openalex search
#       C: crossref doi       | Q: crossref search
# ------------------------------------------------------------

cache <- if (file.exists(cache_f)) readRDS(cache_f) else list()
n_new <- 0

# store one answer; save to disk every 200 answers
cache_put <- function(key, value) {
  cache[[key]] <<- value
  n_new <<- n_new + 1
  if (n_new %% 200 == 0) saveRDS(cache, cache_f)
}

# ------------------------------------------------------------
# 2. HELPERS
# ------------------------------------------------------------

# lowercase letters/digits, single spaces (for comparing titles)
# also removes html tags (<scp>), latex commands (\\textsc) and &amp; so both sides compare clean
norm <- function(x) x |>
  str_replace_all("&amp;", "&") |>                    # crossref double-encodes: &amp;quot;
  str_replace_all("&lt;", "<") |> str_replace_all("&gt;", ">") |>
  str_remove_all("<[^>]+>") |>                        # html tags: <i>, <scp>, <p>
  str_remove_all("&[a-z]+;") |>                       # leftover entities: &quot;
  str_remove_all("\\\\(textsc|textit|textbf|textrm|texttt|text|emph|mathrm|mathit)") |>  # latex, glued to the word
  tolower() |> str_replace_all("[^a-z0-9]+", " ") |> str_squish()

# first-author surname from bib "Last, First and Last2, First2"
first_surname <- function(a) a |> str_split(" and ") |> map_chr(1) |> str_remove(",.*$") |> norm()

# title similarity (0-1). Crossref/OpenAlex often drop the subtitle,
# so if one normalised title is the start of the other (>= 7 chars) = 1
title_sim <- function(a, b) {
  a <- norm(a); b <- norm(b)
  if (is.na(a) || is.na(b) || a == "" || b == "") return(0)
  if (min(nchar(a), nchar(b)) >= 7 && (startsWith(a, b) || startsWith(b, a))) return(1)
  stringsim(a, b, "jw")
}

# OpenAlex abstracts come as {word: [positions]}; rebuild text
rebuild_abstract <- function(inv) {
  if (is.null(inv) || length(inv) == 0) return(NA_character_)
  words <- rep(NA_character_, max(unlist(inv)) + 1)
  for (w in names(inv)) words[unlist(inv[[w]]) + 1] <- w
  paste(words[!is.na(words)], collapse = " ")
}

# Crossref abstracts are JATS xml; strip tags
clean_abstract <- function(ab) {
  if (is.null(ab)) return(NA_character_)
  ab |> str_remove_all("<[^>]+>") |> str_remove("^\\s*Abstract\\s*") |> str_squish()
}

# OpenAlex key (free at openalex.org). Without it the shared daily budget runs out fast.
# One key (OPENALEX_API_KEY) or several, comma-separated (OPENALEX_API_KEYS).
# Keys are never written to disk. When one hits its daily limit we move to the next.
oa_keys <- c(Sys.getenv("OPENALEX_API_KEYS"), Sys.getenv("OPENALEX_API_KEY")) |>
  str_split(",") |> unlist() |> str_squish() |> unique()
oa_keys <- oa_keys[nzchar(oa_keys)]
key_i   <- 1   # index of the key in use

# build one request (used by get_raw and by the parallel step)
build_req <- function(url, query = list(), rate = 8) {
  is_oa <- startsWith(url, oa_url)
  req <- request(url) |>
    req_url_query(!!!query) |>
    req_user_agent(ua) |>
    req_throttle(rate = rate / 1)                          # max requests per second
  if (is_oa && length(oa_keys) > 0) req <- req_auth_bearer_token(req, oa_keys[key_i])
  req |>
    # OpenAlex 429 = daily budget gone (retry-after = hours): do NOT wait. Crossref 429: back off.
    req_retry(max_tries = 4, backoff = ~ 2,
              is_transient = \(r) resp_status(r) %in% c(if (!is_oa) 429, 500, 502, 503, 504)) |>
    req_error(is_error = \(r) FALSE)                       # we read the status ourselves
}

# one GET. Returns list(code, body). code 0 = network error (NOT cached, retried next run)
get_raw <- function(url, query = list(), rate = 8) {
  tryCatch({
    resp <- build_req(url, query, rate) |> req_perform()
    list(code = resp_status(resp),
         body = if (resp_status(resp) == 200) resp_body_json(resp, simplifyVector = FALSE) else NULL)
  }, error = function(e) list(code = 0, body = NULL))
}

# --- OpenAlex work -> flat list
oa_row <- function(w) list(
  doi      = if (is.null(w$doi)) NA_character_ else str_remove(tolower(w$doi), "^https?://doi\\.org/"),
  title    = w$title %||% NA_character_,
  year     = w$publication_year %||% NA_integer_,
  authors  = paste(map_chr(w$authorships, ~ .x$author$display_name %||% ""), collapse = "; "),
  abstract = rebuild_abstract(w$abstract_inverted_index)
)
oa_select <- "doi,title,publication_year,authorships,abstract_inverted_index"

# --- Crossref work -> flat list
cr_row <- function(m) list(
  doi      = tolower(m$DOI %||% NA_character_),
  title    = (m$title %||% list(NA_character_))[[1]] %||% NA_character_,
  year     = (m$issued$`date-parts`[[1]] %||% list(NA))[[1]] %||% NA_integer_,
  authors  = paste(map_chr(m$author %||% list(), ~ .x$family %||% .x$name %||% ""), collapse = "; "),
  abstract = clean_abstract(m$abstract)
)

# score a candidate against our record: title sim, year gap, author found
score_match <- function(cand, r) {
  list(
    sim  = title_sim(cand$title %||% "", r$title_n),
    ygap = if (is.na(r$year) || is.na(cand$year)) NA_real_ else abs(r$year - cand$year),
    auth = r$surname == "" || str_detect(norm(cand$authors), fixed(r$surname))
  )
}

# ------------------------------------------------------------
# 3. LOAD INCLUDED RECORDS
# ------------------------------------------------------------

recs <- readRDS("data/prisma/records_full.rds") |> filter(status == "included")
if (!is.na(limit)) { set.seed(1); recs <- slice_sample(recs, n = limit) }  # test sample

recs <- recs |>
  mutate(
    title_n = norm(title),
    surname = first_surname(coalesce(author, "")),
    # start from what we already have
    abstract_final  = ifelse(has_abstract, abstract, NA_character_),
    abstract_source = ifelse(has_abstract, "original", NA_character_),
    doi_final  = doi_clean,
    doi_source = ifelse(is.na(doi_clean), NA_character_, "original"),
    match_sim  = NA_real_
  )

message(nrow(recs), " included; ", sum(is.na(recs$abstract_final)), " no abstract; ",
        sum(is.na(recs$doi_final)), " no DOI")

# ------------------------------------------------------------
# 4. STEP A: OpenAlex by DOI (have DOI, no abstract), 50 per request
# ------------------------------------------------------------

todo <- recs |> filter(!is.na(doi_clean), is.na(abstract_final)) |> pull(doi_clean) |> unique()
todo <- todo[!paste0("D:", todo) %in% names(cache)]
batches <- split(todo, ceiling(seq_along(todo) / 50))
message("A: ", length(todo), " DOIs, ", length(batches), " requests")

for (b in batches) {
  r <- get_raw(oa_url, list(filter = paste0("doi:", paste(b, collapse = "|")),
                            select = oa_select, `per-page` = 50))
  if (r$code != 200) next                      # not cached: retried next run
  found <- map(r$body$results, oa_row)
  names(found) <- map_chr(found, "doi")
  # every DOI in the batch gets an entry ("none" = not in OpenAlex)
  for (d in b) cache_put(paste0("D:", d), found[[d]] %||% "none")
}

# use OpenAlex abstract only if its title matches ours (guards against wrong DOIs)
for (i in which(!is.na(recs$doi_clean) & is.na(recs$abstract_final))) {
  o <- cache[[paste0("D:", recs$doi_clean[i])]]
  if (is.list(o) && !is.na(o$abstract) && !is.na(recs$title_n[i]) &&
      title_sim(o$title, recs$title_n[i]) >= ver_sim) {
    recs$abstract_final[i]  <- o$abstract
    recs$abstract_source[i] <- "openalex_doi"
  }
}

# ------------------------------------------------------------
# 5. STEP B: OpenAlex title search (no DOI), best of top 5
# ------------------------------------------------------------

# articles first: they are the most likely to match (free budget = ~1,000 searches/day)
todo <- recs |> filter(is.na(doi_final), !is.na(title), nchar(title_n) >= 15) |>
  arrange(match(type, c("article", "incollection", "techreport", "misc", "book"))) |> pull(id)
todo <- todo[!paste0("S:", todo) %in% names(cache)]
# OpenAlex searches cost budget: only run with an API key
if (length(oa_keys) == 0) { message("B: skipped (no OPENALEX_API_KEY)"); todo <- character(0) }
message("B: ", length(todo), " OpenAlex title searches")

for (i in todo) {
  r <- recs[recs$id == i, ]
  a <- get_raw(oa_url, list(search = r$title, select = oa_select, `per-page` = 5))
  # 429 = this key's daily budget is gone: try the next key, stop when none left
  while (a$code == 429 && key_i < length(oa_keys)) {
    key_i <- key_i + 1
    message("B: key ", key_i - 1, " used up, switching to key ", key_i)
    a <- get_raw(oa_url, list(search = r$title, select = oa_select, `per-page` = 5))
  }
  if (a$code == 429) { message("B: all OpenAlex keys used up, stopping"); break }
  if (a$code != 200) next
  hits <- map(a$body$results, oa_row)
  if (length(hits) == 0) { cache_put(paste0("S:", i), "none"); next }
  sc   <- map(hits, score_match, r = r)
  best <- which.max(map_dbl(sc, "sim"))
  cache_put(paste0("S:", i), c(hits[[best]], sc[[best]]))
}

# apply: accept only strong matches (title, year within 1, author)
# weak ones (sim >= 0.90) go to a review file
review <- list()
for (i in which(is.na(recs$doi_final))) {
  s <- cache[[paste0("S:", recs$id[i])]]
  if (!is.list(s)) next
  recs$match_sim[i] <- s$sim
  year_ok <- is.na(s$ygap) || s$ygap <= 1
  if (s$sim >= min_sim && year_ok && s$auth) {
    if (!is.na(s$doi)) { recs$doi_final[i] <- s$doi; recs$doi_source[i] <- "openalex_title_match" }
    if (!is.na(s$abstract) && is.na(recs$abstract_final[i])) {
      recs$abstract_final[i]  <- s$abstract
      recs$abstract_source[i] <- "openalex_title_match"
    }
  } else if (s$sim >= ver_sim) {
    review[[length(review) + 1]] <- tibble(
      id = recs$id[i], key = recs$key[i], source = "openalex",
      our_title = recs$title[i], our_year = recs$year[i], our_author = recs$author[i],
      cand_title = s$title, cand_year = s$year, cand_authors = s$authors, cand_doi = s$doi,
      sim = s$sim, year_ok = year_ok, author_ok = s$auth)
  }
}

# ------------------------------------------------------------
# 6. STEP C: Crossref title search (still no DOI), top 3
# ------------------------------------------------------------

todo <- recs |> filter(is.na(doi_final), !is.na(title), nchar(title_n) >= 15) |> pull(id)
todo <- todo[!paste0("Q:", todo) %in% names(cache)]
message("C: ", length(todo), " Crossref title searches")

# plain loop, 4 requests/s max. (Parallel was tested: Crossref public pool
# answers 429 to concurrent requests, so it does not help.)
# SKIP_CROSSREF_SEARCH=1 skips this slow step (about 0.5 s per record)
if (Sys.getenv("SKIP_CROSSREF_SEARCH") == "1") { message("C: skipped"); todo <- character(0) }

for (i in todo) {
  r <- recs[recs$id == i, ]
  a <- get_raw(cr_url, list(query.bibliographic = paste(r$title, r$surname), rows = 3,
                            select = "DOI,title,issued,author,abstract"), rate = 4)
  if (a$code != 200) next                      # retried next run
  hits <- map(a$body$message$items, cr_row)
  if (length(hits) == 0) { cache_put(paste0("Q:", i), "none"); next }
  sc   <- map(hits, score_match, r = r)
  best <- which.max(map_dbl(sc, "sim"))
  cache_put(paste0("Q:", i), c(hits[[best]], sc[[best]]))
  if (match(i, todo) %% 500 == 0) message("  C: ", match(i, todo), " / ", length(todo))
}
saveRDS(cache, cache_f)

for (i in which(is.na(recs$doi_final))) {
  s <- cache[[paste0("Q:", recs$id[i])]]
  if (!is.list(s)) next
  recs$match_sim[i] <- max(recs$match_sim[i], s$sim, na.rm = TRUE)
  year_ok <- is.na(s$ygap) || s$ygap <= 1
  if (s$sim >= min_sim && year_ok && s$auth && !is.na(s$doi)) {
    recs$doi_final[i]  <- s$doi
    recs$doi_source[i] <- "crossref_title_match"
  } else if (s$sim >= ver_sim) {
    review[[length(review) + 1]] <- tibble(
      id = recs$id[i], key = recs$key[i], source = "crossref",
      our_title = recs$title[i], our_year = recs$year[i], our_author = recs$author[i],
      cand_title = s$title, cand_year = s$year, cand_authors = s$authors, cand_doi = s$doi,
      sim = s$sim, year_ok = year_ok, author_ok = s$auth)
  }
}

# ------------------------------------------------------------
# 6b. APPLY reviewed weak matches (from R/review_weak_matches.R)
# only 'accept' rows. They then go through the Crossref check in step D like any DOI.
#   accept                  title, author and year (<= 3, or <= 1 if title only similar) match
#   accept_title_year_only  candidate has no authors: identical long title, year within 1
# ------------------------------------------------------------

dec_f <- "data/prisma/doi_review_decisions.csv"
if (file.exists(dec_f)) {
  dec <- read_csv(dec_f, show_col_types = FALSE) |>
    filter(decision %in% c("accept", "accept_title_year_only"))
  for (k in seq_len(nrow(dec))) {
    i <- which(recs$id == dec$id[k])
    if (length(i) == 1 && is.na(recs$doi_final[i])) {
      recs$doi_final[i]  <- dec$cand_doi[k]
      recs$doi_source[i] <- paste0("reviewed_", dec$decision[k])
      # abstract from the cached hit with the same DOI (OpenAlex "S:" or Crossref "Q:")
      for (pre in c("S:", "Q:")) {
        h <- cache[[paste0(pre, recs$id[i])]]
        if (is.list(h) && isTRUE(h$doi == dec$cand_doi[k]) && !is.na(h$abstract) && is.na(recs$abstract_final[i])) {
          recs$abstract_final[i]  <- h$abstract
          recs$abstract_source[i] <- "openalex_title_match"
        }
      }
    }
  }
  message("6b: applied ", sum(startsWith(recs$doi_source, "reviewed_"), na.rm = TRUE), " reviewed DOIs")
}

# ------------------------------------------------------------
# 7. STEP D: Crossref by DOI for EVERY final DOI
# checks the DOI exists, and that it is OUR paper
# also fills abstracts still missing
# ------------------------------------------------------------

todo <- unique(na.omit(recs$doi_final))
todo <- todo[!paste0("C:", todo) %in% names(cache)]
message("D: ", length(todo), " Crossref DOI checks")

# Crossref filter takes many DOIs at once: 40 per request instead of 1.
# DOIs with a comma would break the filter syntax -> checked one by one
odd   <- todo[str_detect(todo, "[,|\\s]")]
batch <- split(setdiff(todo, odd), ceiling(seq_along(setdiff(todo, odd)) / 40))

for (b in batch) {
  a <- get_raw(cr_url, list(filter = paste0("doi:", b, collapse = ","),
                            rows = length(b), select = "DOI,title,issued,author,abstract"), rate = 5)
  if (a$code != 200) next                                   # retried next run
  found <- map(a$body$message$items, cr_row)
  names(found) <- map_chr(found, "doi")
  # DOI asked for but not returned = not a Crossref DOI
  for (d in b) cache_put(paste0("C:", d), if (is.null(found[[d]])) list(found = FALSE) else c(found[[d]], list(found = TRUE)))
}
for (d in odd) {
  a <- get_raw(paste0(cr_url, "/", URLencode(d, reserved = TRUE)), rate = 5)
  if (a$code == 200)      cache_put(paste0("C:", d), c(cr_row(a$body$message), list(found = TRUE)))
  else if (a$code == 404) cache_put(paste0("C:", d), list(found = FALSE))
}
saveRDS(cache, cache_f)

# ------------------------------------------------------------
# 8. FLAG each record
#   verified            DOI in Crossref; title identical, or similar (>= 0.90) with year within 3
#   title_mismatch      DOI in Crossref but it is a DIFFERENT work -> wrong DOI
#   doi_not_in_crossref DOI not found in Crossref (maybe DataCite etc.) -> cannot check
#   not_checked         API error, run again
#   title_unusable      our title is missing / "[No Title Found]" -> cannot compare
#   no_doi              no DOI anywhere -> cannot check
# ------------------------------------------------------------

recs$crossref_status <- NA_character_
recs$cr_title <- NA_character_
recs$cr_year  <- NA_integer_
recs$year_gap <- NA_real_
for (i in seq_len(nrow(recs))) {
  d <- recs$doi_final[i]
  if (is.na(d)) { recs$crossref_status[i] <- "no_doi"; next }
  cr <- cache[[paste0("C:", d)]]
  if (is.na(recs$title_n[i]) || recs$title_n[i] %in% c("", "no title found")) {
    recs$crossref_status[i] <- "title_unusable"; next   # our title is missing: cannot compare
  }
  if (!is.list(cr))     { recs$crossref_status[i] <- "not_checked"; next }
  if (!isTRUE(cr$found)) { recs$crossref_status[i] <- "doi_not_in_crossref"; next }
  recs$cr_title[i] <- cr$title
  recs$cr_year[i]  <- cr$year
  sim     <- title_sim(cr$title %||% "", recs$title_n[i])
  year_ok <- is.na(recs$year[i]) || is.na(cr$year) || abs(recs$year[i] - cr$year) <= 3  # online-first vs issue year
  recs$year_gap[i] <- if (is.na(recs$year[i]) || is.na(cr$year)) NA else abs(recs$year[i] - cr$year)
  # identical title = same work (year can differ: online-first, new edition)
  same_title <- !is.na(cr$title) && norm(cr$title) == recs$title_n[i]
  recs$crossref_status[i] <- ifelse(same_title || (sim >= ver_sim && year_ok), "verified", "title_mismatch")
  # Crossref abstract fallback (only if title matched)
  if (recs$crossref_status[i] == "verified" && is.na(recs$abstract_final[i]) &&
      !is.na(cr$abstract) && nchar(cr$abstract) > 50) {
    recs$abstract_final[i]  <- cr$abstract
    recs$abstract_source[i] <- "crossref_doi"
  }
}

# ------------------------------------------------------------
# 9. WRITE
# ------------------------------------------------------------

out <- recs |>
  select(id, key, type, source_file, year, title, author, journal,
         doi_original = doi_clean, doi_final, doi_source,
         crossref_status, cr_title, cr_year, year_gap,
         abstract_final, abstract_source, match_sim)

write_csv(out, "data/prisma/records_enriched.csv")                       # all included + flags
write_csv(filter(out, crossref_status == "verified"),
          "data/prisma/records_crossref_verified.csv")                    # only checkable ones
write_csv(bind_rows(review), "data/prisma/doi_matches_to_review.csv")     # weak matches, human check
write_csv(filter(out, crossref_status != "verified"),
          "data/prisma/records_not_verified.csv")                         # flagged list

summary <- bind_rows(
  tibble(item = "included records", n = nrow(out)),
  count(out, crossref_status) |> transmute(item = paste("crossref:", crossref_status), n),
  count(out, abstract_source) |> transmute(item = paste("abstract:", coalesce(abstract_source, "still missing")), n),
  count(out, doi_source)      |> transmute(item = paste("doi:", coalesce(doi_source, "none")), n),
  tibble(item = "weak matches in review file", n = nrow(bind_rows(review)))
)
write_csv(summary, "data/prisma/enrichment_summary.csv")
print(summary, n = Inf)

# status by record type: shows where checking is impossible (books, reports ...)
print(count(out, type, crossref_status) |> tidyr::pivot_wider(names_from = crossref_status, values_from = n, values_fill = 0))
