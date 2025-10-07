apply_final_classification <- function(bib_data) {
  bib_data %>%
    mutate(
      final_decision = case_when(
        manual_decision == "exclude" ~ "exclude",
        manual_decision == "include" ~ "include",
        duplicate_status != "unique" ~ "exclude",
        automated_exclude ~ "exclude",
        TRUE ~ "include"  # Default to include for systematic review
      ),
      
      exclusion_reason = case_when(
        manual_decision == "exclude" ~ manual_reason,
        duplicate_status != "unique" ~ duplicate_status,
        automated_exclude ~ automated_reason,
        final_decision == "include" ~ "included",
        TRUE ~ "unknown"
      )
    )
}