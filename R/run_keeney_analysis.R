run_keeney_analysis <- function(bib_data) {
  
  # Step 1: Ensure application domains are detected
  if(!"application_domains" %in% names(bib_data)) {
    cat("Detecting application domains...\n")
    bib_data <- detect_application_domains(bib_data)
  }
  
  # Step 2: Apply intensity classification
  cat("Classifying decision intensity...\n")
  bib_data <- classify_decision_intensity(bib_data)
  
  # Step 3: Analyze patterns
  cat("Analyzing Keeney patterns...\n")
  intensity_stats <- analyze_keeney_pattern(bib_data)
  
  return(list(
    classified_data = bib_data,
    intensity_stats = intensity_stats
  ))
}