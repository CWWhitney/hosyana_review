# FIXED confidence scoring - using columns that actually exist
add_confidence_scores <- function(data) {
  data %>%
    mutate(
      # Use the columns we just created
      method_confidence = case_when(
        methods_from_title != "" & detected_methods != "" ~ "high",
        methods_from_title != "" ~ "medium", 
        detected_methods != "" ~ "medium",
        TRUE ~ "none"
      ),
      
      # Count methods
      method_count = ifelse(detected_methods == "", 0, 
                            str_count(detected_methods, ";") + 1),
      
      # Specific method flags
      has_voi = str_detect(tolower(full_text), "\\bvalue of information\\b|\\bvoi\\b"),
      has_uncertainty = str_detect(tolower(full_text), "\\buncertainty|\\bprobabilistic|\\bsensitivity\\b"),
      has_bayesian = str_detect(tolower(full_text), "\\bbayesian|\\bbayes\\b"),
      has_simulation = str_detect(tolower(full_text), "\\bsimulation|\\bmonte carlo\\b")
    )
}
