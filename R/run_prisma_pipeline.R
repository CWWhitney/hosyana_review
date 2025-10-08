run_prisma_pipeline <- function(bib_data) {

  
  # Track counts at each step
  step_counts <- list()
  
  # Step 1: Initial count
  step_counts$initial <- nrow(bib_data)
  cat("📊 Initial records:", step_counts$initial, "\n\n")
  
  # Step 2: Duplicate identification
  cat("1. Identifying duplicates...\n")
  bib_data <- identify_duplicates(bib_data)
  step_counts$after_duplicates <- sum(bib_data$duplicate_status == "unique")
  step_counts$duplicates_removed <- step_counts$initial - step_counts$after_duplicates
  cat("   Removed", step_counts$duplicates_removed, "duplicates\n")
  cat("   Records remaining:", step_counts$after_duplicates, "\n\n")
  
  # Step 3: Manual classifications
  cat("2. Applying manual classifications...\n")
  bib_data <- apply_manual_classifications(bib_data)
  step_counts$manually_excluded <- sum(bib_data$manual_decision == "exclude")
  step_counts$manually_included <- sum(bib_data$manual_decision == "include")
  step_counts$unreviewed <- sum(bib_data$manual_decision == "unreviewed")
  cat("   Manually excluded (bin):", step_counts$manually_excluded, "\n")
  cat("   Manually included (read):", step_counts$manually_included, "\n")
  cat("   Unreviewed records:", step_counts$unreviewed, "\n\n")
  
  # Step 4: Automated exclusion rules
  cat("3. Applying automated exclusion rules...\n")
  bib_data <- apply_exclusion_rules(bib_data)
  step_counts$excluded_doc_type <- sum(bib_data$exclude_doc_type & bib_data$manual_decision == "unreviewed")
  step_counts$excluded_language <- sum(bib_data$exclude_language & bib_data$manual_decision == "unreviewed")
  step_counts$excluded_non_scientific <- sum(bib_data$exclude_non_scientific & bib_data$manual_decision == "unreviewed")
  step_counts$excluded_content <- sum(bib_data$exclude_content & bib_data$manual_decision == "unreviewed")
  step_counts$excluded_preprint <- sum(bib_data$exclude_preprint & bib_data$manual_decision == "unreviewed")
  cat("   Invalid document types:", step_counts$excluded_doc_type, "\n")
  cat("   Non-English:", step_counts$excluded_language, "\n")
  cat("   Non-scientific:", step_counts$excluded_non_scientific, "\n")
  cat("   Irrelevant content:", step_counts$excluded_content, "\n")
  cat("   Preprints with published versions:", step_counts$excluded_preprint, "\n\n")
  
  # Step 5: Final classification
  cat("4. Applying final classification...\n")
  bib_data <- apply_final_classification(bib_data)
  step_counts$final_included <- sum(bib_data$final_decision == "include")
  step_counts$final_excluded <- sum(bib_data$final_decision == "exclude")
  cat("   Final included:", step_counts$final_included, "\n")
  cat("   Final excluded:", step_counts$final_excluded, "\n\n")
  
  # Generate results
  stats <- generate_prisma_stats(bib_data)
  export <- export_prisma_results(bib_data)
  
  return(list(
    classified_data = bib_data,
    step_counts = step_counts,
    statistics = stats,
    export_files = export
  ))
}
