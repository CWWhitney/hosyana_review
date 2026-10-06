# ============================================================
# Relevance screening on title + abstract
# Run after enrich_records.R:  Rscript R/relevance_screening.R
#
# Part 1  build screening table + cheap keyword triage (for PRIORITY only)
# Part 2  draw a 300-record validation sample -> human coding sheet
# Part 3  LLM screening (needs ANTHROPIC_API_KEY, see bottom)
#
# Keyword triage must NOT be used to exclude: it misses 61% of the
# records the team read and kept (checked on the manual 'read' tags).
# ============================================================

library(dplyr)
library(stringr)
library(stringi)
library(readr)
library(purrr)

dir.create("data/screening", showWarnings = FALSE)

# ------------------------------------------------------------
# PART 1. SCREENING TABLE
# ------------------------------------------------------------

full <- readRDS("data/prisma/records_full.rds")
enr  <- read_csv("data/prisma/records_enriched.csv", show_col_types = FALSE)

# remove control chars and Unicode non-characters (some abstracts have them)
clean <- function(x) x |> stri_replace_all_regex("[\\p{C}]", " ") |> str_squish()

# included records only; abstract = enriched abstract if we have one
recs <- enr |>
  transmute(id, key, type, year, title = clean(title), journal,
            abstract = clean(abstract_final), crossref_status) |>
  mutate(abstract = ifelse(abstract == "" | is.na(abstract), NA, abstract),
         has_abstract = !is.na(abstract))

# manual team tags (bin = thrown out, read = read and kept) for later checks
tags <- full |> select(id, tag_bin, tag_read)
recs <- left_join(recs, tags, by = "id")

# --- keyword triage: 3 concept groups in title + abstract
# D decision/policy   U uncertainty/risk   M model/method
pat_D <- "decision|decid|policy|policies|intervention|choice|prioriti[sz]|option"
pat_U <- "uncertain|risk|probabilis|stochastic|bayes|monte carlo|sensitivity analysis|variab|value of information|expected value|ambigu"
pat_M <- "model|simulat|framework|elicit|expert|stakeholder|scenario|analysis"

recs <- recs |>
  mutate(
    text = stri_trans_tolower(paste(title, abstract)),
    has_D = str_detect(text, pat_D),
    has_U = str_detect(text, pat_U),
    has_M = str_detect(text, pat_M),
    triage = case_when(has_D & has_U & has_M ~ "high",
                       has_D & has_U         ~ "medium",
                       has_D | has_U         ~ "low",
                       TRUE                  ~ "none")
  ) |> select(-text)

write_csv(recs, "data/screening/records_for_screening.csv")

cat("Included records:", nrow(recs), "\n")
print(count(recs, has_abstract, triage) |> tidyr::pivot_wider(names_from = triage, values_from = n, values_fill = 0))

# ------------------------------------------------------------
# PART 2. VALIDATION SAMPLE (300), for human coding
# 3 strata so we see relevant AND irrelevant records:
#   A high + medium triage   100
#   B low                    100
#   C none                   100
# Each row keeps its stratum size, so recall can be weighted back to all records.
# Records WITHOUT abstract are sampled too (title-only judgement is a real case).
# ------------------------------------------------------------

set.seed(2026)
strat <- recs |>
  mutate(stratum = case_when(triage %in% c("high", "medium") ~ "A_high_medium",
                             triage == "low"                 ~ "B_low",
                             TRUE                            ~ "C_none")) |>
  group_by(stratum) |> mutate(stratum_n = n()) |> ungroup()

sample300 <- strat |> group_by(stratum) |> slice_sample(n = 100) |> ungroup() |>
  slice_sample(prop = 1)   # shuffle so coders do not see strata in blocks

# coding sheet: no triage shown (do not bias the coder)
sheet <- sample300 |>
  transmute(sample_no = row_number(), id, key, year, title,
            abstract = str_trunc(coalesce(abstract, "[no abstract]"), 1500),
            coder1 = "", coder2 = "", notes = "")   # fill with: include / exclude / unsure
write_csv(sheet, "data/screening/validation_sample_coding_sheet.csv")

# key with strata + triage + manual tags (keep apart from coders)
write_csv(sample300 |> mutate(sample_no = row_number()) |>
            select(sample_no, id, key, stratum, stratum_n, triage, has_abstract, tag_bin, tag_read),
          "data/screening/validation_sample_key.csv")

cat("\nValidation sample:", nrow(sheet), "records\n")
print(count(sample300, stratum, stratum_n))

# ------------------------------------------------------------
# PART 3. LLM SCREENING (not run unless a key is set)
# ANTHROPIC_API_KEY=<key> SCREEN_SAMPLE=1 Rscript R/relevance_screening.R   # 300 sample only
# ANTHROPIC_API_KEY=<key> Rscript R/relevance_screening.R                    # all records
# Every answer is cached in data/screening/llm_cache.rds (safe to re-run).
# Check agreement with the human sample BEFORE running on everything.
# ------------------------------------------------------------

api_key <- Sys.getenv("ANTHROPIC_API_KEY")
if (!nzchar(api_key)) {
  message("\nPart 3 skipped: no ANTHROPIC_API_KEY set.")
  quit(save = "no")
}

library(httr2)
library(jsonlite)

model    <- "claude-haiku-4-5-20251001"
cache_f  <- "data/screening/llm_cache.rds"
criteria <- read_file("data/screening/criteria.md")
cache    <- if (file.exists(cache_f)) readRDS(cache_f) else list()

# one record -> prompt
make_prompt <- function(title, abstract) paste0(
  "You screen records for a literature review. Use ONLY these criteria:\n\n", criteria,
  "\n\nRecord:\nTitle: ", title, "\nAbstract: ", coalesce(abstract, "[none]"),
  "\n\nAnswer with JSON only: {\"decision\":\"include|exclude|unsure\",\"reason\":\"max 20 words\"}")

# call the API once; returns list(decision, reason) or NULL on failure
screen_one <- function(title, abstract) {
  resp <- request("https://api.anthropic.com/v1/messages") |>
    req_headers(`x-api-key` = api_key, `anthropic-version` = "2023-06-01") |>
    req_body_json(list(model = model, max_tokens = 120,
                       messages = list(list(role = "user", content = make_prompt(title, abstract))))) |>
    req_retry(max_tries = 4) |> req_error(is_error = \(r) FALSE) |> req_perform()
  if (resp_status(resp) != 200) return(NULL)
  txt <- resp_body_json(resp)$content[[1]]$text
  # take the first {...} block, in case the model adds words around it
  js <- str_extract(txt, "\\{.*\\}")
  out <- tryCatch(fromJSON(js), error = function(e) NULL)
  if (is.null(out$decision) || !out$decision %in% c("include", "exclude", "unsure")) return(NULL)
  list(decision = out$decision, reason = out$reason %||% "")
}

todo <- if (Sys.getenv("SCREEN_SAMPLE") == "1") sample300 else recs
todo <- todo |> filter(!as.character(id) %in% names(cache))
message("Part 3: ", nrow(todo), " records to screen with ", model)

for (k in seq_len(nrow(todo))) {
  a <- screen_one(todo$title[k], todo$abstract[k])
  if (!is.null(a)) cache[[as.character(todo$id[k])]] <- a
  if (k %% 100 == 0) { saveRDS(cache, cache_f); message("  ", k, " / ", nrow(todo)) }
}
saveRDS(cache, cache_f)

res <- imap_dfr(cache, ~ tibble(id = as.integer(.y), llm_decision = .x$decision, llm_reason = .x$reason))
write_csv(res, "data/screening/llm_screening_results.csv")
print(count(res, llm_decision))
