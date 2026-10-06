# ============================================================
# PRISMA pipeline: raw Zotero .bib -> one reconciled count
# Run from project root: Rscript R/prisma_pipeline.R
# Every record gets ONE final status and ONE reason.
# Nothing is dropped silently.
# ============================================================

library(dplyr)
library(stringr)
library(readr)
library(purrr)
library(tibble)

dir.create("data/prisma", recursive = TRUE, showWarnings = FALSE)

# ------------------------------------------------------------
# 1. READ: own light parser
# (bibtex::read.bib and bib2df drop entries without warning)
# ------------------------------------------------------------

# fields we keep
keep_fields <- c("title", "year", "doi", "author", "journal",
                 "publisher", "keywords", "abstract", "file", "note")

# parse one entry (text block) into a one-row tibble
parse_entry <- function(txt) {
  # type and citekey from first line, e.g. "@article{smith2020,"
  head <- str_match(txt, "^@(\\w+)\\s*\\{\\s*([^,\\s]+)\\s*,")
  # find where each "field = " starts (start of a line)
  starts <- str_locate_all(txt, "(?m)^\\s*([A-Za-z-]+)\\s*=\\s*")[[1]]
  out <- setNames(rep(NA_character_, length(keep_fields)), keep_fields)
  if (nrow(starts) > 0) {
    # field names
    names_ <- str_match(str_sub(txt, starts[, 1], starts[, 2]),
                        "([A-Za-z-]+)\\s*=")[, 2] |> tolower()
    # value = text until next field starts
    ends <- c(starts[-1, 1] - 1, nchar(txt))
    vals <- str_sub(txt, starts[, 2] + 1, ends) |> str_trim()
    # last value still holds the entry's closing "}"
    vals[length(vals)] <- str_remove(vals[length(vals)], "\\}\\s*$")
    # drop trailing comma, braces and quotes
    vals <- vals |> str_remove(",\\s*$") |> str_remove_all("[{}\"]") |>
      str_squish()
    hit <- names_ %in% keep_fields
    out[names_[hit]] <- vals[hit]
  }
  # one row: type, key, then the kept fields
  tibble(type = head[1, 2], key = head[1, 3], !!!as.list(out))
}

# read one .bib file -> tibble with one row per entry
read_bib <- function(path) {
  raw <- read_file(path)
  # split before each "@type{" at line start
  blocks <- str_split(raw, "\n(?=@\\w+\\s*\\{)")[[1]]
  blocks <- blocks[str_detect(blocks, "^@\\w+\\s*\\{")]
  # drop @comment / @string / @preamble
  blocks <- blocks[!str_detect(blocks, regex("^@(comment|string|preamble)", ignore_case = TRUE))]
  map_dfr(blocks, parse_entry) |>
    mutate(source_file = basename(path))
}

# top-level files only.
# bib_raw/manual_run/ is NOT read: it is a stale copy (checked: all keys already in main files)
files <- list.files("bib/bib_raw", pattern = "\\.bib$", full.names = TRUE)
message("Reading ", length(files), " files ...")
raw <- map_dfr(files, read_bib)

# sanity: entries counted by "^@" per file must equal parsed rows
check <- tibble(source_file = basename(files),
                at_lines = map_int(files, ~ sum(str_detect(read_lines(.x), "^@\\w+\\s*\\{")))) |>
  left_join(count(raw, source_file, name = "parsed"), by = "source_file") |>
  mutate(ok = at_lines == parsed)
stopifnot(all(check$ok))
write_csv(check, "data/prisma/check_file_counts.csv")

# ------------------------------------------------------------
# 2. CLEAN: helper columns
# ------------------------------------------------------------

recs <- raw |>
  mutate(
    id = row_number(),
    year = suppressWarnings(as.integer(str_extract(year, "\\d{4}"))),
    # DOI: lowercase, strip URL prefix
    doi_clean = doi |> tolower() |> str_remove("^https?://(dx\\.)?doi\\.org/") |> str_squish(),
    doi_clean = na_if(doi_clean, ""),
    # title: lowercase letters/digits only
    title_clean = title |> tolower() |> str_remove_all("[^a-z0-9]") |> na_if(""),
    has_abstract = !is.na(abstract) & abstract != "",
    # file priority when choosing which duplicate to keep
    # (research papers first, reports / documents last)
    priority = case_when(
      str_detect(source_file, "^papers_low_info") ~ 4,
      str_detect(source_file, "^papers_")         ~ 1,
      str_detect(source_file, "^books_")          ~ 2,
      str_detect(source_file, "^chapters")        ~ 3,
      str_detect(source_file, "^reports")         ~ 5,
      str_detect(source_file, "^documents")       ~ 6,
      TRUE                                        ~ 7
    ),
    kw = tolower(coalesce(keywords, ""))
  )

# ------------------------------------------------------------
# 3. DEDUPLICATE (3 steps, each counted)
# keep the best copy; remove only the extra copies
# (old code removed ALL copies, including the original)
# ------------------------------------------------------------

recs <- recs |> arrange(priority, desc(has_abstract), id) |>
  mutate(status = NA_character_, reason = NA_character_)

# helper: flag extra copies by a grouping column
flag_dups <- function(df, col, label) {
  extra <- !is.na(df[[col]]) & is.na(df$status) &
    duplicated(ifelse(is.na(df$status), df[[col]], NA))
  df$status[extra] <- "removed"
  df$reason[extra] <- label
  df
}

# (a) same citekey = same Zotero item exported twice
recs <- flag_dups(recs, "key", "duplicate_citekey")
# (b) same DOI
recs <- flag_dups(recs, "doi_clean", "duplicate_doi")
# (c) same title + year
recs <- recs |> mutate(ty = ifelse(is.na(title_clean) | is.na(year), NA, paste(title_clean, year)))
recs <- flag_dups(recs, "ty", "duplicate_title_year")

# (d) duplicates found by hand: same work, but year / title form differs
# (preprint vs published, wrong year, garbled author). Curated list, one row per pair:
# data/prisma/duplicates_reviewed.csv  (remove_key = extra copy, keep_key = the one we keep)
rev_f <- "data/prisma/duplicates_reviewed.csv"
if (file.exists(rev_f)) {
  rev <- read_csv(rev_f, show_col_types = FALSE)
  hit <- is.na(recs$status) & recs$key %in% rev$remove_key
  recs$status[hit] <- "removed"
  recs$reason[hit] <- "duplicate_reviewed"
  # every pair must be found, and the copy we keep must still be in play
  stopifnot(sum(hit) == nrow(rev), all(rev$keep_key %in% recs$key[is.na(recs$status)]))
}

# ------------------------------------------------------------
# 4. MANUAL SCREENING (Zotero keywords)
# 'bin'      = we threw it out
# 'read cw'  = we read it and kept it
# ------------------------------------------------------------

recs <- recs |>
  mutate(
    tag_bin  = str_detect(kw, "(^|[;,]\\s*)bin(\\s*[;,]|$)"),
    tag_read = str_detect(kw, "read (cw|pka)")
  )

# conflict: both tags. 'bin' wins (same as old code)
n_conflict <- sum(recs$tag_bin & recs$tag_read & is.na(recs$status))

recs <- recs |>
  mutate(
    reason = ifelse(is.na(status) & tag_bin, "manual_bin", reason),
    status = ifelse(is.na(status) & tag_bin, "removed", status)
  )

# ------------------------------------------------------------
# 5. AUTOMATED EXCLUSION (same rules as old 03_*.Rmd)
# only for records NOT manually read
# ------------------------------------------------------------

recs <- recs |>
  mutate(
    t = tolower(title),
    j = tolower(coalesce(journal, "")),
    p = tolower(coalesce(publisher, "")),
    # not a paper: report, syllabus, catalogue ...
    r_doc  = str_detect(t, "annual report|syllabus|catalog|course notes|legal document|bibliography collection"),
    # not scientific: news, law journals
    r_sci  = str_detect(j, "legal review|law journal|news|magazine|newspaper") |
             str_detect(t, "^news:|^magazine:|^blog:|newspaper article"),
    # preprint server + commercial publisher = published copy exists
    r_pre  = str_detect(j, "arxiv|preprint|biorxiv|medrxiv") &
             str_detect(p, "elsevier|springer|wiley|taylor"),
    # clearly off-topic
    r_off  = str_detect(t, "chemistry experiment|physics lab|pure mathematics|organic synthesis"),
    auto_reason = case_when(
      r_doc ~ "auto_invalid_document_type",
      r_sci ~ "auto_non_scientific",
      r_pre ~ "auto_preprint_with_published_version",
      r_off ~ "auto_irrelevant_content",
      TRUE  ~ NA_character_
    ),
    hit = is.na(status) & !tag_read & !is.na(auto_reason),
    reason = ifelse(hit, auto_reason, reason),
    status = ifelse(hit, "removed", status)
  )

# ------------------------------------------------------------
# 6. WHAT IS LEFT = INCLUDED (for classification)
# ------------------------------------------------------------

recs <- recs |>
  mutate(
    reason = ifelse(is.na(status), ifelse(tag_read, "included_manual_read", "included_unreviewed"), reason),
    status = ifelse(is.na(status), "included", status),
    # quality flags (not exclusions)
    flag_no_year     = is.na(year),
    flag_no_abstract = !has_abstract,
    flag_no_doi      = is.na(doi_clean),
    flag_linter_err  = str_detect(kw, "linter/error")
  )

# ------------------------------------------------------------
# 7. WRITE: master table (one row per raw record)
# ------------------------------------------------------------

master <- recs |>
  select(id, key, type, source_file, year, title, author, journal, doi = doi_clean,
         status, reason, starts_with("flag_"), tag_bin, tag_read)
write_csv(master, "data/prisma/records_master.csv")
# full table with all kept fields (abstract, keywords ...) for later scripts
saveRDS(recs, "data/prisma/records_full.rds")

# ------------------------------------------------------------
# 8. PRISMA COUNTS
# ------------------------------------------------------------

n_raw      <- nrow(recs)
n_dup      <- sum(recs$reason %in% c("duplicate_citekey", "duplicate_doi", "duplicate_title_year", "duplicate_reviewed"))
n_manual   <- sum(recs$reason == "manual_bin")
n_auto     <- sum(str_starts(recs$reason, "auto_"))
n_included <- sum(recs$status == "included")

# arithmetic must close
stopifnot(n_raw - n_dup - n_manual - n_auto == n_included)

counts <- bind_rows(
  # reported at search time, NOT verifiable from files
  tibble(stage = "identification", item = "Google Scholar (reported, April-July 2023)", n = 17600, source = "search_results/Systematic_Review-Sankey.csv"),
  tibble(stage = "identification", item = "Web of Science (reported)",                   n = 14,    source = "search_results/Systematic_Review-Sankey.csv"),
  tibble(stage = "identification", item = "CABI (reported)",                             n = 13,    source = "02_Review.Rmd"),
  # verifiable from files
  tibble(stage = "library", item = "Records in Zotero exports (bib/bib_raw/*.bib)", n = n_raw, source = "this script"),
  tibble(stage = "dedup",   item = "Removed: same citekey (exported twice)",      n = sum(recs$reason == "duplicate_citekey"),    source = "this script"),
  tibble(stage = "dedup",   item = "Removed: same DOI",                           n = sum(recs$reason == "duplicate_doi"),        source = "this script"),
  tibble(stage = "dedup",   item = "Removed: same title + year",                  n = sum(recs$reason == "duplicate_title_year"), source = "this script"),
  tibble(stage = "dedup",   item = "Removed: same work, other year/version (checked by hand)", n = sum(recs$reason == "duplicate_reviewed"), source = "duplicates_reviewed.csv"),
  tibble(stage = "screening", item = "Removed: manual 'bin' tag",                 n = n_manual,                                   source = "this script"),
  tibble(stage = "screening", item = "Removed: auto rule, invalid document type", n = sum(recs$reason == "auto_invalid_document_type"), source = "this script"),
  tibble(stage = "screening", item = "Removed: auto rule, non-scientific",        n = sum(recs$reason == "auto_non_scientific"),        source = "this script"),
  tibble(stage = "screening", item = "Removed: auto rule, preprint with published version", n = sum(recs$reason == "auto_preprint_with_published_version"), source = "this script"),
  tibble(stage = "screening", item = "Removed: auto rule, irrelevant content",    n = sum(recs$reason == "auto_irrelevant_content"),    source = "this script"),
  tibble(stage = "included", item = "Included (manual 'read' tag)",               n = sum(recs$reason == "included_manual_read"), source = "this script"),
  tibble(stage = "included", item = "Included (not manually reviewed)",           n = sum(recs$reason == "included_unreviewed"),  source = "this script"),
  tibble(stage = "included", item = "TOTAL included",                             n = n_included,                                 source = "this script")
)
write_csv(counts, "data/prisma/prisma_counts.csv")

# quality flags among included (what limits classification)
inc <- filter(recs, status == "included")
quality <- tibble(
  item = c("included", "with abstract", "with DOI", "with year", "linter error flag", "both bin and read tags (bin wins)"),
  n    = c(nrow(inc), sum(inc$has_abstract), sum(!inc$flag_no_doi), sum(!inc$flag_no_year),
           sum(inc$flag_linter_err), n_conflict)
)
write_csv(quality, "data/prisma/quality_flags.csv")

# print summary
print(counts, n = Inf, width = Inf)
print(quality)
print(count(recs, source_file, status) |> tidyr::pivot_wider(names_from = status, values_from = n, values_fill = 0), n = Inf)
