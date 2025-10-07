generate_prisma_stats <- function(bib_data) {
  
  stats <- list(
    # Identification phase
    identification = list(
      records_identified_gs = sum(!is.na(bib_data$DOI) & str_detect(tolower(bib_data$BIBTEXKEY), "gs|google")),
      records_identified_wos = sum(!is.na(bib_data$DOI) & str_detect(tolower(bib_data$BIBTEXKEY), "wos|webofscience")),
      records_identified_other = sum(is.na(bib_data$DOI) | !str_detect(tolower(bib_data$BIBTEXKEY), "gs|wos|google|webofscience")),
      total_identified = nrow(bib_data)
    ),
    
    # Screening phase  
    screening = list(
      duplicates_removed = sum(bib_data$duplicate_status != "unique"),
      not_relevant_automated = sum(bib_data$automated_exclude & bib_data$exclusion_reason == "irrelevant_content"),
      not_fitting_assessment = sum(bib_data$automated_exclude & bib_data$exclusion_reason == "invalid_document_type"),
      records_screened = nrow(bib_data) - sum(bib_data$duplicate_status != "unique")
    ),
    
    # Included phase
    included = list(
      sought_retrieval = sum(bib_data$final_decision == "include"),
      assessed_eligibility = sum(bib_data$final_decision == "include" & bib_data$manual_decision == "include"),
      quantitative_assessment = sum(bib_data$final_decision == "include"),
      qualitative_synthesis = sum(bib_data$final_decision == "include" & bib_data$manual_decision == "include"),
      studies_included = sum(bib_data$final_decision == "include")
    )
  )
  
  # Calculate derived statistics
  stats$identification$total_identified <- 
    stats$identification$records_identified_gs +
    stats$identification$records_identified_wos + 
    stats$identification$records_identified_other
  
  stats$screening$records_screened <- 
    stats$identification$total_identified - stats$screening$duplicates_removed
  
  return(stats)
}