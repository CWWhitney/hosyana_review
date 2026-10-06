# ============================================================
# Add the enrichment / Crossref check stage to the PRISMA counts
# Run after prisma_pipeline.R and enrich_records.R:
#   Rscript R/prisma_counts_final.R
# Output: data/prisma/prisma_counts_full.csv
# No record is removed here. This stage only reports checks.
# ============================================================

library(dplyr)
library(readr)
library(tibble)

# counts from the screening pipeline (identification -> included)
base <- read_csv("data/prisma/prisma_counts.csv", show_col_types = FALSE)

# the included records with Crossref flags, DOIs and abstracts
enr <- read_csv("data/prisma/records_enriched.csv", show_col_types = FALSE)

# n of included must match between the two scripts
n_included <- base$n[base$item == "TOTAL included"]
stopifnot(nrow(enr) == n_included)

# helper: count records with a given status
n_status <- function(s) sum(enr$crossref_status == s)

# ------------------------------------------------------------
# Stage "verification": every included record falls in ONE group
# ------------------------------------------------------------
ver <- tribble(
  ~stage,         ~item,                                                       ~n,
  "verification", "Included records checked against Crossref",                 nrow(enr),
  "verification", "Verified (DOI in Crossref, title matches)",                 n_status("verified"),
  "verification", "Not verified: DOI points to a different work",             n_status("title_mismatch"),
  "verification", "Not verified: DOI not in Crossref",                         n_status("doi_not_in_crossref"),
  "verification", "Not verified: our title missing",                           n_status("title_unusable"),
  "verification", "Not verified: no DOI found",                                n_status("no_doi")
)

# the groups must add up to all included records
stopifnot(sum(ver$n[3:6]) + ver$n[2] == nrow(enr))

# ------------------------------------------------------------
# Stage "enrichment": what the lookups added
# ------------------------------------------------------------
enrich <- tribble(
  ~stage,       ~item,                                              ~n,
  "enrichment", "DOI: already in Zotero",                           sum(enr$doi_source == "original", na.rm = TRUE),
  "enrichment", "DOI: added by title match (OpenAlex or Crossref, incl. reviewed)", sum(enr$doi_source %in% c("openalex_title_match", "crossref_title_match", "reviewed_accept", "reviewed_accept_title_year_only"), na.rm = TRUE),
  "enrichment", "DOI: total",                                       sum(!is.na(enr$doi_final)),
  "enrichment", "Abstract: already in Zotero",                      sum(enr$abstract_source == "original", na.rm = TRUE),
  "enrichment", "Abstract: added (OpenAlex or Crossref)",           sum(enr$abstract_source != "original", na.rm = TRUE),
  "enrichment", "Abstract: total",                                  sum(!is.na(enr$abstract_final)),
  "enrichment", "Abstract: still missing",                          sum(is.na(enr$abstract_final))
)

# DOI and abstract totals must add up too
stopifnot(enrich$n[1] + enrich$n[2] == enrich$n[3])
stopifnot(enrich$n[4] + enrich$n[5] == enrich$n[6])
stopifnot(enrich$n[6] + enrich$n[7] == nrow(enr))

# weak matches (title found, but year / author / similarity not strong enough)
# decisions come from R/review_weak_matches.R
dec_f <- "data/prisma/doi_review_decisions.csv"
if (file.exists(dec_f)) {
  dec <- read_csv(dec_f, show_col_types = FALSE)
  n_dec <- function(x) sum(dec$decision %in% x)
  weak <- tribble(
    ~stage,       ~item,                                                                  ~n,
    "weak_match", "Weak DOI matches reviewed (unique records)",                           nrow(dec),
    "weak_match", "Accepted by rule (title + author + year match), DOI added",            n_dec(c("accept", "accept_title_year_only")),
    "weak_match", "Rejected: no DOI on candidate",                                        n_dec("reject_no_doi"),
    "weak_match", "Rejected: different authors (other work)",                             n_dec("reject_author_different"),
    "weak_match", "Left for human check",                                                 sum(startsWith(dec$decision, "human"))
  )
  # the four groups must add up to all reviewed records
  stopifnot(sum(weak$n[2:5]) == weak$n[1])
  # also: how many of the records with a DOI added are verified in Crossref
  rev <- enr |> filter(startsWith(coalesce(doi_source, ""), "reviewed_"))
  weak <- bind_rows(weak, tibble(stage = "weak_match",
    item = "  of the accepted: verified in Crossref", n = sum(rev$crossref_status == "verified")))
  enrich <- bind_rows(enrich, weak)
}

# ------------------------------------------------------------
# Join and write
# ------------------------------------------------------------
full <- bind_rows(base, ver |> mutate(source = "records_enriched.csv"),
                  enrich |> mutate(source = "records_enriched.csv"))
write_csv(full, "data/prisma/prisma_counts_full.csv")
print(full |> select(stage, item, n), n = Inf)
