identify_duplicates <- function(bib_data) {
  bib_data %>%
    mutate(
      # Simple title-based duplicate detection
      title_clean = str_remove_all(tolower(TITLE), "[^a-z0-9 ]"),
      is_duplicate = duplicated(title_clean) | duplicated(title_clean, fromLast = TRUE),
      
      # DOI-based duplicate detection
      is_doi_duplicate = !is.na(DOI) & (duplicated(DOI) | duplicated(DOI, fromLast = TRUE)),
      
      # Combined duplicate flag
      duplicate_status = case_when(
        is_doi_duplicate ~ "doi_duplicate",
        is_duplicate ~ "title_duplicate", 
        TRUE ~ "unique"
      )
    )
}