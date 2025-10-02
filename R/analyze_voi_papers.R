analyze_voi_papers <- function(data) {
  voi_papers <- data %>% filter(has_voi)
  
  if(nrow(voi_papers) == 0) {
    return(list(methods = NULL, trends = NULL, summary = "No VOI papers found"))
  }
  
  # Methods used in VOI papers
  voi_methods <- voi_papers %>%
    filter(detected_methods != "") %>%
    separate_rows(detected_methods, sep = "; ") %>%
    count(detected_methods, sort = TRUE)
  
  # Temporal trends of VOI
  voi_trends <- voi_papers %>%
    filter(!is.na(year)) %>%
    count(year, name = "voi_papers")
  
  # Create plot
  trend_plot <- NULL
  if(nrow(voi_trends) > 0) {
    trend_plot <- ggplot(voi_trends, aes(x = year, y = voi_papers)) +
      geom_line(color = "#e74c3c", size = 1) +
      geom_point(color = "#e74c3c", size = 2) +
      labs(title = "VOI Papers Over Time",
           x = "Year", y = "Number of Papers") +
      theme_minimal()
  }
  
  # Return as list
  return(list(
    methods = voi_methods,
    trends_data = voi_trends,
    plot = trend_plot,
    summary = paste("VOI papers:", nrow(voi_papers))
  ))
}