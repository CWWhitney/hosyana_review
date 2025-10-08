analyze_keeney_pattern <- function(bib_data) {
  intensity_analysis <- bib_data %>%
    filter(primary_intensity != "Unclassified") %>%
    count(primary_intensity, sort = TRUE) %>%
    mutate(
      percentage = n / sum(n) * 100,
      keeney_prediction = case_when(
        primary_intensity %in% c("Level 1: Intuitive Decisions", "Level 2: Simple Analysis") ~ "High frequency (Keeney prediction)",
        TRUE ~ "Lower frequency (Keeney prediction)"
      )
    )
  
  return(intensity_analysis)
}