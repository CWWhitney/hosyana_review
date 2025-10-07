apply_manual_classifications <- function(bib_data) {
  bib_data %>%
    mutate(
      has_bin = str_detect(tolower(KEYWORDS), "\\bbin\\b"),
      has_read = str_detect(tolower(KEYWORDS), "read cw|read pka"),
      
      manual_decision = case_when(
        has_bin ~ "exclude",
        has_read & !has_bin ~ "include",
        TRUE ~ "unreviewed"
      ),
      
      manual_reason = case_when(
        has_bin ~ "curator_marked_bin",
        has_read ~ "manually_reviewed_keep",
        TRUE ~ "not_reviewed"
      )
    )
}