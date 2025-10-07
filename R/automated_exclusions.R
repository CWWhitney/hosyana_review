apply_automated_exclusions <- function(bib_data) {
  bib_data %>%
    mutate(
      # Document type exclusions
      exclude_doc_type = str_detect(tolower(TITLE), 
                                    "annual report|syllabus|catalog|course notes|legal document"),
      
      # Content relevance
      exclude_content = !str_detect(tolower(TITLE), 
                                    "decision|model|analysis|support|uncertainty"),
      
      # Combined automated exclusion
      automated_exclude = exclude_doc_type | exclude_content,
      
      automated_reason = case_when(
        exclude_doc_type ~ "invalid_document_type",
        exclude_content ~ "irrelevant_content", 
        TRUE ~ "not_excluded"
      )
    )
}