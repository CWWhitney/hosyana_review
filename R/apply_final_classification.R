apply_final_classification <- function(bib_data) {
  bib_data %>%
    mutate(
      final_decision = case_when(
        manual_decision == "exclude" ~ "exclude",  # bin papers always excluded
        manual_decision == "include" ~ "include",  # read papers always included
        duplicate_status != "unique" ~ "exclude",  # duplicates excluded
        automated_exclude ~ "exclude",  # automated rules exclude
        TRUE ~ "include"  # Default to include for systematic review
      ),
      
      exclusion_reason = case_when(
        manual_decision == "exclude" ~ manual_reason,
        manual_decision == "include" ~ "manually_included",  # Read papers show as manually included
        duplicate_status != "unique" ~ duplicate_status,
        automated_exclude ~ automated_reason,
        final_decision == "include" ~ "included_by_automation",
        TRUE ~ "unknown"
      )
    )
}