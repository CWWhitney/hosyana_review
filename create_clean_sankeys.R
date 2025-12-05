# Create Clean Sankey Plots for Decision Support Methods Analysis
# Uses modified plot_sankey_clean function with consistent text size and no percentages

library(jsonlite)

# Source the clean plot_sankey function
source("R/plot_sankey_clean.R")

# Read the finalized sankey data
final_data <- fromJSON("FINAL_sankey_data.json")

# Function to create clean Sankey for one decade
create_clean_sankey <- function(decade_name, decade_data) {
  total_papers <- decade_data$total_papers
  methods <- decade_data$methods

  # Skip decades with insufficient papers
  if (total_papers < 80) {
    cat("Skipping", decade_name, "- only", total_papers, "papers (minimum 80 required)\n")
    return(NULL)
  }

  # Get method counts and sort by frequency
  method_counts <- unlist(methods)
  method_counts <- method_counts[method_counts > 0]
  method_counts <- sort(method_counts, decreasing = TRUE)

  # Take top methods for clear visualization (8 max)
  top_methods <- head(method_counts, 8)

  # Calculate papers with identified methods vs. others
  papers_with_methods <- sum(top_methods)
  papers_other <- total_papers - papers_with_methods

  # Prepare data for plot_sankey_clean function
  inputs <- total_papers
  losses <- c(as.numeric(top_methods), papers_other)
  unit <- "papers"

  # Create readable method labels (no counts, no percentages)
  method_names <- names(top_methods)
  readable_labels <- sapply(method_names, function(x) {
    switch(x,
      "DECISION_ANALYSIS" = "Decision Analysis",
      "POLICY_INTERVENTION" = "Policy/Intervention",
      "UNCERTAINTY_ANALYSIS" = "Uncertainty Analysis",
      "STAKEHOLDER_EXPERT" = "Stakeholder/Expert",
      "MODELING_SIMULATION" = "Modeling/Simulation",
      "BAYESIAN_PROBABILISTIC" = "Bayesian/Probabilistic",
      "COMPUTER_ASSISTED" = "Computer Assisted",
      "VALUE_INFORMATION" = "Value of Information",
      "MULTI_CRITERIA" = "Multi-Criteria",
      "OPTIMIZATION" = "Optimization",
      "ECONOMIC_EVALUATION" = "Economic Evaluation",
      "EVALUATION_ASSESSMENT" = "Evaluation/Assessment",
      "SYSTEMS_COMPLEXITY" = "Systems/Complexity",
      "TECHNOLOGY_INNOVATION" = "Technology/Innovation",
      "ENVIRONMENTAL_SUSTAINABILITY" = "Environmental",
      "QUALITY_PERFORMANCE" = "Quality/Performance",
      "RISK_SAFETY" = "Risk/Safety",
      "FORECASTING_PREDICTION" = "Forecasting",
      "BEHAVIORAL_PSYCHOLOGY" = "Behavioral",
      "GAME_THEORY" = "Game Theory",
      x # default to original if not found
    )
  })

  labels <- c(paste(decade_name, "Total"), readable_labels, "Other Methods")

  # Create PDF version using clean plot_sankey function
  plot_sankey_clean(
    inputs = inputs,
    losses = losses,
    unit = unit,
    labels = labels,
    format = "pdf"
  )

  # Rename to clean format: sankey_2000.pdf (no prefix, no .bmp)
  if (file.exists("Sankey.pdf")) {
    decade_short <- gsub("s$", "", tolower(decade_name))
    new_name <- paste0("sankey_", decade_short, ".pdf")
    file.rename("Sankey.pdf", new_name)
    cat("Created:", new_name, "\n")
  }

  # Calculate statistics
  method_percentage <- round((papers_with_methods / total_papers) * 100, 1)

  # Return summary information
  return(list(
    decade = decade_name,
    total_papers = total_papers,
    method_papers = papers_with_methods,
    method_percentage = method_percentage,
    top_methods = top_methods,
    method_count = length(top_methods)
  ))
}

# Main execution
cat("Creating Clean Sankey Plots for Decision Support Methods Analysis\n")
cat("Features: Consistent text size, percentages on arrows, counts at input\n")
cat(rep("=", 70), "\n")

# Get decades with substantial data
decades_to_plot <- names(final_data)[sapply(final_data, function(x) x$total_papers >= 80)]
decades_to_plot <- sort(decades_to_plot)

cat("Decades selected:", paste(decades_to_plot, collapse = ", "), "\n\n")

# Create clean plots for each decade
results <- list()
for (decade in decades_to_plot) {
  cat("Processing", decade, "...\n")

  result <- create_clean_sankey(decade, final_data[[decade]])
  if (!is.null(result)) {
    results[[decade]] <- result

    cat(sprintf("  Total papers: %d\n", result$total_papers))
    cat(sprintf(
      "  Papers with methods: %d (%.1f%%)\n",
      result$method_papers, result$method_percentage
    ))
    cat(sprintf("  Method categories shown: %d\n", result$method_count))
    cat("\n")
  }
}

# Summary
cat(rep("=", 70), "\n")
cat("CLEAN SANKEY PLOTS COMPLETED\n")
cat(rep("=", 70), "\n")

if (length(results) > 0) {
  cat("Generated files:\n")
  for (decade in names(results)) {
    decade_short <- gsub("s$", "", tolower(decade))
    cat(sprintf("  sankey_%s.pdf\n", decade_short))
  }

  cat(sprintf("\nTotal decades plotted: %d\n", length(results)))
  cat("Features applied:\n")
  cat("  ✓ Consistent text size (0.8) for all labels\n")
  cat("  ✓ Percentages shown on all arrows\n")
  cat("  ✓ Count shown at input, percentages for methods\n")
  cat("  ✓ Fixed multi-method paper handling\n")
  cat("  ✓ Clean filenames (sankey_YYYY.pdf)\n")
  cat("  ✓ PDF only (no .bmp files)\n")
} else {
  cat("No plots were generated.\n")
}

cat(rep("=", 70), "\n")
