# Load required packages
library(dplyr)
library(stringr)
library(purrr)

# Function to classify papers based on keywords
classify_papers <- function(bib_data) {
  bib_data %>%
    mutate(
      # Extract keyword categories
      has_bin = str_detect(tolower(KEYWORDS), "\\bbin\\b"),
      has_read_cw = str_detect(tolower(KEYWORDS), "read cw"),
      has_read_pka = str_detect(tolower(KEYWORDS), "read pka"),
      has_read = has_read_cw | has_read_pka,
      
      # Classification logic
      manual_classification = case_when(
        has_bin ~ "exclude",
        has_read & !has_bin ~ "include", 
        TRUE ~ "unclassified"
      ),
      
      # Reason for manual classification
      manual_reason = case_when(
        has_bin ~ "Marked for removal by curator",
        has_read & !has_bin ~ "Manually reviewed and kept",
        TRUE ~ "Not yet manually reviewed"
      )
    )
}