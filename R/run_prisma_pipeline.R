run_prisma_pipeline <- function(bib_data) {

  
  # Execute pipeline
  bib_data <- identify_duplicates(bib_data)
  bib_data <- apply_manual_classifications(bib_data)
  bib_data <- apply_automated_exclusions(bib_data) 
  bib_data <- apply_final_classification(bib_data)
  
  # Generate results
  stats <- generate_prisma_stats(bib_data)
  flow_output <- generate_prisma_flow_output(stats)
  export <- export_prisma_results(bib_data)
  
  # Print PRISMA flow numbers
  cat(paste(flow_output, collapse = "\n"), "\n")
  
  return(list(
    classified_data = bib_data,
    statistics = stats,
    prisma_flow = flow_output,
    export_files = export
  ))
}