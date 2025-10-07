generate_prisma_flow_output <- function(stats) {
  
  flow_text <- c(
    "# PRISMA Flow Diagram Numbers",
    "",
    "## Identification",
    paste("- Records identified through Google Scholar: ", stats$identification$records_identified_gs),
    paste("- Records identified through Web of Science: ", stats$identification$records_identified_wos), 
    paste("- Records identified through other sources: ", stats$identification$records_identified_other),
    paste("- **Total records identified**: ", stats$identification$total_identified),
    "",
    "## Screening", 
    paste("- Duplicates removed: ", stats$screening$duplicates_removed),
    paste("- Records screened: ", stats$screening$records_screened),
    paste("- Not relevant (automated): ", stats$screening$not_relevant_automated),
    paste("- Not fitting assessment details: ", stats$screening$not_fitting_assessment),
    "",
    "## Included",
    paste("- Reports sought for retrieval: ", stats$included$sought_retrieval),
    paste("- Reports assessed for eligibility: ", stats$included$assessed_eligibility), 
    paste("- **Quantitative assessment**: ", stats$included$quantitative_assessment),
    paste("- **Qualitative synthesis**: ", stats$included$qualitative_synthesis),
    paste("- **Studies included in review**: ", stats$included$studies_included)
  )
  
  return(flow_text)
}