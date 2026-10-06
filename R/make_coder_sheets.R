# ============================================================
# One Excel file per coder for the 300-record validation sample
# Run: Rscript R/make_coder_sheets.R
# Coders must NOT see each other's labels: send each person only their own file.
# Output: data/screening/coder_sheets/coder_<name>.xlsx
# ============================================================

library(dplyr)
library(readr)
library(writexl)

dir.create("data/screening/coder_sheets", showWarnings = FALSE)

# who codes (everyone codes ALL 300 records, so we can measure agreement)
coders <- c("Cory", "Prajna", "Dorcas")

sheet    <- read_csv("data/screening/validation_sample_coding_sheet.csv", show_col_types = FALSE)
criteria <- readLines("data/screening/criteria.md")

for (who in coders) {
  # sheet 1: the work. Same records, same order, for every coder.
  work <- sheet |>
    transmute(sample_no, year, title, abstract,
              label = "",   # type exactly: include / exclude / unsure
              notes = "")
  # sheet 2: criteria, so the file is self-contained
  instr <- tibble::tibble(criteria = criteria)
  write_xlsx(list(coding = work, criteria = instr),
             path = file.path("data/screening/coder_sheets", paste0("coder_", who, ".xlsx")))
}
message("Wrote ", length(coders), " files in data/screening/coder_sheets/")
