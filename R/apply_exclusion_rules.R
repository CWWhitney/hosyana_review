apply_exclusion_rules <- function(bib_data) {
  bib_data %>%
    mutate(
      # Document type exclusions (specific patterns)
      exclude_doc_type = str_detect(tolower(TITLE), 
                                    "annual report|syllabus|catalog|course notes|legal document|bibliography collection"),
      
      # # Language exclusion - only if we have the field
      # exclude_language = ifelse("LANGUAGE" %in% names(bib_data),
      #                           !is.na(LANGUAGE) & tolower(LANGUAGE) != "english",
      #                           FALSE),
      
      # Scientific content check (be more specific)
      exclude_non_scientific = case_when(
        !is.na(JOURNAL) & str_detect(tolower(JOURNAL), 
                                     "legal review|law journal|news|magazine|newspaper") ~ TRUE,
        str_detect(tolower(TITLE), "^news:|^magazine:|^blog:|newspaper article") ~ TRUE,
        TRUE ~ FALSE
      ),
      
      # Preprint handling - only exclude if we're confident it's a duplicate
      exclude_preprint = case_when(
        !is.na(JOURNAL) & str_detect(tolower(JOURNAL), "arxiv|preprint|biorxiv|medrxiv") & 
          !is.na(PUBLISHER) & str_detect(tolower(PUBLISHER), "elsevier|springer|wiley|taylor") ~ TRUE,
        TRUE ~ FALSE
      ),
      
      # Content relevance - be more inclusive, focus on clear exclusions
      exclude_content = case_when(
        # Only exclude if clearly not decision-related
        str_detect(tolower(TITLE), "chemistry experiment|physics lab|pure mathematics|organic synthesis") ~ TRUE,
        # Keep anything that might be decision-related
        str_detect(tolower(TITLE), "decision|choice|select|evaluate|assess|analyze|model|uncertain|risk") ~ FALSE,
        # Default to include for systematic review
        TRUE ~ FALSE
      ),
      
      # Combined automated exclusion
      automated_exclude = exclude_doc_type | #exclude_language | 
        exclude_non_scientific | exclude_preprint | exclude_content,
      
      automated_reason = case_when(
        exclude_doc_type ~ "invalid_document_type",
       # exclude_language ~ "non_english",
        exclude_non_scientific ~ "non_scientific",
        exclude_preprint ~ "preprint_with_published_version", 
        exclude_content ~ "irrelevant_content",
        TRUE ~ "not_excluded"
      )
    )
}