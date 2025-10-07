export_prisma_results <- function(bib_data, output_dir = "output/prisma") {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  
  # Export included papers
  included_papers <- bib_data %>% filter(final_decision == "include")
  bib2df::df2bib(included_papers, file.path(output_dir, "included_papers.bib"))
  
  # Export excluded papers with reasons
  excluded_papers <- bib_data %>% filter(final_decision == "exclude")
  bib2df::df2bib(excluded_papers, file.path(output_dir, "excluded_papers.bib"))
  
  # Export detailed classification
  classification_details <- bib_data %>%
    select(BIBTEXKEY, TITLE, final_decision, exclusion_reason, manual_decision)
  
  write.csv(classification_details, 
            file.path(output_dir, "prisma_classification_details.csv"), 
            row.names = FALSE)
  
  return(list(
    included_count = nrow(included_papers),
    excluded_count = nrow(excluded_papers),
    included_file = file.path(output_dir, "included_papers.bib"),
    excluded_file = file.path(output_dir, "excluded_papers.bib")
  ))
}