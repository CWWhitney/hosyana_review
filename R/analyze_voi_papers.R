# Focus on VOI papers specifically
analyze_voi_papers <- function(data) {
  voi_papers <- data %>% filter(has_voi)
  
  if(nrow(voi_papers) == 0) {
    cat("No VOI papers found.\n")
    return(NULL)
  }
  
  cat("=== VOI PAPERS ANALYSIS ===\n")
  cat("Number of VOI papers:", nrow(voi_papers), "\n")
  
  # Methods used in VOI papers
  voi_methods <- voi_papers %>%
    filter(detected_methods != "") %>%
    separate_rows(detected_methods, sep = "; ") %>%
    count(detected_methods, sort = TRUE)
  
  cat("\nMethods used in VOI papers:\n")
  print(voi_methods)
  
  # Temporal trends of VOI
  voi_trends <- voi_papers %>%
    filter(!is.na(year)) %>%
    count(year, name = "voi_papers")
  
  if(nrow(voi_trends) > 0) {
    trend_plot <- ggplot(voi_trends, aes(x = year, y = voi_papers)) +
      geom_line(color = "#e74c3c", size = 1) +
      geom_point(color = "#e74c3c", size = 2) +
      labs(title = "VOI Papers Over Time",
           x = "Year", y = "Number of Papers") +
      theme_minimal()
    
    print(trend_plot)
  }
  
  return(voi_methods)
}
