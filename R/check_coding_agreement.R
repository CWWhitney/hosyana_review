# ============================================================
# Read the filled coder sheets, check them, report agreement
# Put the returned files in data/screening/coder_sheets/ (same names)
# Run: Rscript R/check_coding_agreement.R
# Output: data/screening/human_labels.csv  (consensus + disagreements)
# ============================================================

library(dplyr)
library(tidyr)
library(readr)
library(readxl)
library(purrr)
library(stringr)

files <- list.files("data/screening/coder_sheets", pattern = "^coder_.*\\.xlsx$", full.names = TRUE)
ok    <- c("include", "exclude", "unsure")

# read one coder file -> sample_no, label
read_coder <- function(f) {
  who <- str_match(basename(f), "coder_(.*)\\.xlsx")[, 2]
  d   <- read_excel(f, sheet = "coding") |>
    transmute(sample_no, coder = who, label = str_to_lower(str_squish(label)))
  # complain about anything that is not include / exclude / unsure
  bad <- d |> filter(!label %in% ok | is.na(label))
  if (nrow(bad) > 0) message(who, ": ", nrow(bad), " rows empty or invalid (e.g. sample_no ", paste(head(bad$sample_no, 5), collapse = ", "), ")")
  d
}
labels <- map_dfr(files, read_coder) |> filter(label %in% ok)
wide   <- labels |> pivot_wider(names_from = coder, values_from = label)

# ------------------------------------------------------------
# Pairwise agreement + Cohen's kappa (no extra package)
# ------------------------------------------------------------
kappa <- function(a, b) {
  keep <- !is.na(a) & !is.na(b); a <- a[keep]; b <- b[keep]
  lv <- ok
  tab <- table(factor(a, lv), factor(b, lv))
  po <- sum(diag(tab)) / sum(tab)
  pe <- sum(rowSums(tab) * colSums(tab)) / sum(tab)^2
  c(n = sum(tab), agree = round(po, 3), kappa = round((po - pe) / (1 - pe), 3))
}
coders <- setdiff(names(wide), "sample_no")
pairs  <- combn(coders, 2, simplify = FALSE)
agree  <- map_dfr(pairs, ~ tibble::as_tibble_row(c(pair = paste(.x, collapse = " vs "), kappa(wide[[.x[1]]], wide[[.x[2]]]))))
print(agree)

# ------------------------------------------------------------
# Consensus: majority label; ties / 3-way splits go to discussion
# ------------------------------------------------------------
wide$consensus <- apply(wide[, coders], 1, function(x) {
  tb <- sort(table(x[!is.na(x)]), decreasing = TRUE)
  if (length(tb) == 0) NA else if (length(tb) == 1 || tb[1] > tb[2]) names(tb)[1] else "DISCUSS"
})
write_csv(wide, "data/screening/human_labels.csv")
cat("\nConsensus counts:\n"); print(count(wide, consensus))
cat("Records to discuss:", sum(wide$consensus == "DISCUSS", na.rm = TRUE), "\n")
