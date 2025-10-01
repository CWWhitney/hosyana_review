# Enhanced detection function
detect_methods_enhanced <- function(text) {
  if(is.na(text) || text == "") return("")
  
  text_lower <- tolower(text)
  methods_detected <- character()
  
  for(method in names(method_categories)) {
    keywords <- method_categories[[method]]
    # Use word boundaries to avoid partial matches
    patterns <- paste0("\\b", keywords, "\\b")
    if(any(str_detect(text_lower, patterns))) {
      methods_detected <- c(methods_detected, method)
    }
  }
  
  return(paste(unique(methods_detected), collapse = "; "))
}