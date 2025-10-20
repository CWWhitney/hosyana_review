# Add confidence scores for method detection
add_confidence_scores <- function(data) {
  data %>%
    mutate(
      # Confidence based on where method was detected
      method_confidence = case_when(
        methods_from_title != "" & detected_methods != "" ~ "high",
        methods_from_title != "" ~ "medium",
        detected_methods != "" ~ "medium",
        TRUE ~ "low"
      ),
      
      # Number of methods detected
      method_count = str_count(detected_methods, ";") + 1,
      method_count = ifelse(detected_methods == "", 0, method_count),
      
      # Has VOI specifically (your key interest)
      has_voi = str_detect(tolower(full_text), "\\bvalue of information\\b|\\bvoi\\b"),
      
      # Has uncertainty methods
      has_uncertainty = str_detect(tolower(full_text), 
                                   "\\buncertainty|\\bprobabilistic|\\bsensitivity|\\brisk\\b")
    )
}
