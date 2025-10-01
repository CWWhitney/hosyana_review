# Method frequency analysis
analyze_method_frequency <- function(data) {
  method_counts <- data %>%
    filter(detected_methods != "") %>%
    separate_rows(detected_methods, sep = "; ") %>%
    count(detected_methods, sort = TRUE)
  
  # Plot
  p <- ggplot(method_counts, aes(x = reorder(detected_methods, n), y = n)) +
    geom_col(fill = "steelblue", alpha = 0.8) +
    coord_flip() +
    labs(title = "Methods Detected in Literature",
         subtitle = paste("From", nrow(data), "papers"),
         x = "Method", y = "Number of Papers") +
    theme_minimal()
  
  return(list(plot = p, counts = method_counts))
}