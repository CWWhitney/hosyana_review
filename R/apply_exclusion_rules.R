# Function to apply automated exclusion rules
apply_exclusion_rules <- function(data) {
  
  # Check if LANGUAGE column exists and handle safely
  has_language_column <- "LANGUAGE" %in% names(data)
  
  data %>%
    mutate(
      # Rule 1: Document type exclusions
      exclude_document_type = case_when(
        str_detect(tolower(TITLE), "annual report|syllabus|catalog|course notes") ~ TRUE,
        str_detect(tolower(TITLE), "legal document|law review") ~ TRUE,
        str_detect(tolower(TITLE), "preprint|thesis") & 
          !is.na(JOURNAL) ~ TRUE,
        TRUE ~ FALSE
      ),
      
      # Rule 2: Language exclusion - fixed vectorization
      exclude_language = if(has_language_column) {
        !is.na(LANGUAGE) & tolower(LANGUAGE) != "english"
      } else {
        rep(FALSE, n())  # Return FALSE for all rows if no LANGUAGE column
      },
      
      # Rule 3: Content relevance
      exclude_content = case_when(
        !str_detect(tolower(TITLE), "decision|model|analysis|support") ~ TRUE,
        str_detect(tolower(TITLE), "bibliography collection|duplicate") ~ TRUE,
        TRUE ~ FALSE
      ),
      
      # Combined automated exclusion
      automated_exclude = exclude_document_type | exclude_language | exclude_content,
      
      # Final classification
      final_classification = case_when(
        manual_classification == "exclude" ~ "exclude",
        manual_classification == "include" ~ "include", 
        automated_exclude ~ "exclude",
        TRUE ~ "unclassified"
      ),
      
      # Reason for automated decisions
      exclusion_reason = case_when(
        manual_classification == "exclude" ~ manual_reason,
        exclude_document_type ~ "Invalid document type",
        exclude_language ~ "Non-English publication",
        exclude_content ~ "Irrelevant content", 
        manual_classification == "include" ~ manual_reason,
        TRUE ~ "Pending review"
      )
    )
}