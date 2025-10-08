classify_decision_intensity <- function(bib_data) {
  intensity_categories <- define_keeney_intensity()
  
  bib_data %>%
    mutate(
      # Detect intensity levels in text
      intensity_levels = map_chr(full_text, function(text) {
        text_lower <- tolower(text)
        levels_detected <- character()
        
        for(level in names(intensity_categories)) {
          keywords <- intensity_categories[[level]]
          patterns <- paste0("\\b", keywords, "\\b")
          if(any(str_detect(text_lower, patterns))) {
            levels_detected <- c(levels_detected, level)
          }
        }
        
        paste(levels_detected, collapse = "; ")
      }),
      
      # Assign primary intensity level (highest detected)
      primary_intensity = case_when(
        str_detect(intensity_levels, "level5") ~ "Level 5: Deep Uncertainty",
        str_detect(intensity_levels, "level4") ~ "Level 4: Advanced Analysis", 
        str_detect(intensity_levels, "level3") ~ "Level 3: Structured Analysis",
        str_detect(intensity_levels, "level2") ~ "Level 2: Simple Analysis",
        str_detect(intensity_levels, "level1") ~ "Level 1: Intuitive Decisions",
        TRUE ~ "Unclassified"
      ),
      
      # Keeney's insight: most decisions are lower intensity
      follows_keeney_pattern = primary_intensity %in% c(
        "Level 1: Intuitive Decisions", 
        "Level 2: Simple Analysis"
      )
    )
}