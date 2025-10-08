detect_application_domains <- function(bib_data) {
  application_domains <- list(
    healthcare = c("health", "medical", "clinical", "patient", "treatment", "healthcare"),
    environmental = c("environment", "climate", "ecological", "sustainability", "conservation"),
    business = c("business", "supply chain", "marketing", "finance", "investment"),
    policy = c("policy", "regulation", "governance", "public policy", "government"),
    engineering = c("engineering", "manufacturing", "design", "system design")
  )
  
  detect_applications <- function(text) {
    if(is.na(text) || text == "") return("")
    text_lower <- tolower(text)
    apps_detected <- character()
    
    for(app in names(application_domains)) {
      keywords <- application_domains[[app]]
      patterns <- paste0("\\b", keywords, "\\b")
      if(any(str_detect(text_lower, patterns))) {
        apps_detected <- c(apps_detected, app)
      }
    }
    
    return(paste(unique(apps_detected), collapse = "; "))
  }
  
  bib_data %>%
    mutate(
      application_domains = map_chr(full_text, detect_applications)
    )
}