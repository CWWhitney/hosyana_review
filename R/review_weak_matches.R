# ============================================================
# Review the weak DOI matches with explicit rules
# Run after enrich_records.R:  Rscript R/review_weak_matches.R
# Input:  data/prisma/doi_matches_to_review.csv
# Output: data/prisma/doi_review_decisions.csv  (every weak match + decision)
#         data/prisma/doi_review_human.csv      (what still needs eyes)
# enrich_records.R reads the decisions and applies the accepted ones.
# ============================================================

library(dplyr)
library(stringr)
library(readr)
library(purrr)
library(stringi)

weak <- read_csv("data/prisma/doi_matches_to_review.csv", show_col_types = FALSE)
enr  <- read_csv("data/prisma/records_enriched.csv", show_col_types = FALSE)

# ------------------------------------------------------------
# 1. AUTHOR MATCH, accent-proof
# "Gabri\els" (latex) and "Gabriëls" must both become "gabriels"
# ------------------------------------------------------------

norm_auth <- function(x) {
  x |> str_remove_all("\\\\['`^~=.]?") |>           # latex accents: \'i  \"e  ->  i  e
    stri_trans_general("Latin-ASCII") |>            # ë -> e, é -> e
    tolower() |> str_replace_all("[^a-z ]", " ") |> str_squish()
}

# last word of the first author's surname ("van Loenen, B." -> "loenen")
# our format: "Last, First and Last2, First2"
our_surnames <- function(a) {
  a |> str_split(" and ") |> map(~ .x |> str_remove(",.*$") |> norm_auth() |>
                                    str_remove("\\b(jr|sr|ii|iii|iv)$") |> str_squish() |>  # "Cox Jr" -> cox
                                    str_extract("[a-z]+$")) |> map(~ .x[!is.na(.x)])
}

# status: confirmed / different / candidate_missing
author_status <- function(ours, cand) {
  sn <- our_surnames(ours)[[1]]
  if (is.na(cand) || cand == "" || length(sn) == 0) return("candidate_missing")
  cn    <- norm_auth(cand)
  found <- map_lgl(sn, ~ str_detect(cn, paste0("\\b", .x, "\\b")))
  # first author found, or at least half of the authors
  if (found[1] || mean(found) >= 0.5) "confirmed" else "different"
}

# ------------------------------------------------------------
# 2. SCORE EACH WEAK MATCH
# ------------------------------------------------------------

# DOIs we already hold for other records (a match to one of these = duplicate)
held <- enr |> filter(!is.na(doi_final)) |> select(held_id = id, doi = doi_final)

d <- weak |>
  mutate(
    author_state = map2_chr(our_author, cand_authors, author_status),
    year_gap     = abs(our_year - cand_year),
    # same DOI already used by another record in our set?
    dup_of       = held$held_id[match(cand_doi, held$doi)],
    dup_of       = ifelse(!is.na(dup_of) & dup_of != id, dup_of, NA),
    # same DOI proposed for two of our records
    dup_in_weak  = duplicated(cand_doi) | duplicated(cand_doi, fromLast = TRUE)
  ) |>
  # one candidate per record: keep the best (highest sim)
  arrange(id, desc(sim)) |> distinct(id, .keep_all = TRUE)

# ------------------------------------------------------------
# 3. DECISION RULES (first match wins)
# ------------------------------------------------------------

d <- d |>
  mutate(
    ygap_ok = is.na(year_gap) | year_gap <= 3,
    decision = case_when(
      is.na(cand_doi)                                         ~ "reject_no_doi",
      !is.na(dup_of)                                          ~ "human_possible_duplicate_record",
      dup_in_weak                                             ~ "human_same_doi_for_two_records",
      author_state == "different"                             ~ "reject_author_different",
      author_state == "confirmed" & sim >= 0.95 & ygap_ok     ~ "accept",
      author_state == "confirmed" & sim >= 0.90 & (is.na(year_gap) | year_gap <= 1) ~ "accept",
      author_state == "confirmed" & sim >= 0.95               ~ "human_year_gap_edition",
      # candidate has no authors: cannot check them. Accept ONLY if the title is
      # identical, long (>= 4 words) and the year within 1. Marked, so it can be filtered.
      author_state == "candidate_missing" & sim >= 0.99 & lengths(strsplit(our_title, " ")) >= 4 &
        (is.na(year_gap) | year_gap <= 1)                     ~ "accept_title_year_only",
      author_state == "candidate_missing"                     ~ "human_candidate_has_no_authors",
      TRUE                                                    ~ "human_other"
    )
  )

write_csv(d, "data/prisma/doi_review_decisions.csv")
write_csv(filter(d, str_starts(decision, "human")), "data/prisma/doi_review_human.csv")

cat("weak matches:", nrow(weak), "| unique records:", nrow(d), "\n")
print(count(d, decision, sort = TRUE))
