# Create Expanded Decade Sankey Plots for Decision Support Methods
# Uses the existing plot_sankey.R function with expanded method categories
# Based on comprehensive search terms and broader decision support concepts

library(jsonlite)

# Source the existing plot_sankey function
source("R/plot_sankey.R")

# Read the expanded sankey data
expanded_data <- fromJSON("expanded_sankey_data.json")

# Function to create a Sankey for one decade with expanded categories
create_expanded_sankey <- function(decade_name, decade_data) {
  total_papers <- decade_data$total_papers
  methods <- decade_data$methods

  # Skip decades with too few papers
  if (total_papers < 100) {
    cat("Skipping", decade_name, "- only", total_papers, "papers\n")
    return(NULL)
  }

  # Get method counts (sorted by count)
  method_counts <- unlist(methods)
  method_counts <- method_counts[method_counts > 0]
  method_counts <- sort(method_counts, decreasing = TRUE)

  # Take top methods for clarity (more than before since we have better detection)
  top_methods <- head(method_counts, 8)

  # Calculate papers without methods or other methods
  papers_with_methods <- sum(top_methods)
  papers_without_methods <- total_papers - papers_with_methods

  # Prepare data for plot_sankey function
  inputs <- total_papers
  losses <- c(as.numeric(top_methods), papers_without_methods)
  unit <- "papers"

  # Create readable labels from method names
  method_names <- names(top_methods)
  # Convert technical names to readable labels
  readable_names <- sapply(method_names, function(x) {
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
      "ENVIRONMENTAL_SUSTAINABILITY" = "Environmental/Sustainability",
      "QUALITY_PERFORMANCE" = "Quality/Performance",
      "RISK_SAFETY" = "Risk/Safety",
      "FORECASTING_PREDICTION" = "Forecasting/Prediction",
      "BEHAVIORAL_PSYCHOLOGY" = "Behavioral/Psychology",
      "GAME_THEORY" = "Game Theory",
      x
    ) # default to original if not found
  })

  labels <- c(paste(decade_name, "Total"), readable_names, "Other/No Methods")

  # Create PDF version
  plot_sankey(
    inputs = inputs,
    losses = losses,
    unit = unit,
    labels = labels,
    format = "pdf"
  )

  # Rename the generated file
  if (file.exists("Sankey.pdf")) {
    new_name <- paste0("expanded_sankey_", gsub("s$", "", tolower(decade_name)), ".pdf")
    file.rename("Sankey.pdf", new_name)
    cat("Created:", new_name, "\n")
  }

  # Create BMP version for compatibility
  plot_sankey(
    inputs = inputs,
    losses = losses,
    unit = unit,
    labels = labels,
    format = "bmp"
  )

  if (file.exists("Sankey.bmp")) {
    new_name <- paste0("expanded_sankey_", gsub("s$", "", tolower(decade_name)), ".bmp")
    file.rename("Sankey.bmp", new_name)
    cat("Created:", new_name, "\n")
  }

  # Calculate method percentage
  method_percentage <- (papers_with_methods / total_papers) * 100

  # Return summary info
  return(list(
    decade = decade_name,
    total_papers = total_papers,
    method_papers = papers_with_methods,
    method_percentage = method_percentage,
    top_methods = top_methods
  ))
}

# Main execution
cat("Creating expanded decade-by-decade Sankey plots\n")
cat("Based on comprehensive decision support method categories\n")
cat(rep("=", 70), "\n")

# Get decades with substantial data (increased threshold due to better detection)
decades_to_plot <- names(expanded_data)[sapply(expanded_data, function(x) x$total_papers >= 100)]
decades_to_plot <- sort(decades_to_plot)

cat("Processing decades:", paste(decades_to_plot, collapse = ", "), "\n\n")

# Create plots for each decade
results <- list()
for (decade in decades_to_plot) {
  cat("Processing", decade, "...\n")

  result <- create_expanded_sankey(decade, expanded_data[[decade]])
  if (!is.null(result)) {
    results[[decade]] <- result

    # Print summary
    cat(sprintf("  Total papers: %d\n", result$total_papers))
    cat(sprintf(
      "  Papers with methods: %d (%.1f%%)\n",
      result$method_papers, result$method_percentage
    ))
    cat("  Top methods:\n")
    for (i in seq_along(result$top_methods)) {
      method_name <- names(result$top_methods)[i]
      method_count <- result$top_methods[[i]]
      percentage <- (method_count / result$total_papers) * 100
      cat(sprintf("    %s: %d papers (%.1f%%)\n", method_name, method_count, percentage))
    }
    cat("\n")
  }
}

cat(rep("=", 70), "\n")
cat("EXPANDED ANALYSIS SUMMARY\n")
cat(rep("=", 70), "\n")

if (length(results) > 0) {
  total_all_papers <- sum(sapply(results, function(x) x$total_papers))
  total_method_papers <- sum(sapply(results, function(x) x$method_papers))
  overall_percentage <- (total_method_papers / total_all_papers) * 100

  cat(sprintf("Total papers across plotted decades: %d\n", total_all_papers))
  cat(sprintf(
    "Papers with identified methods: %d (%.1f%%)\n",
    total_method_papers, overall_percentage
  ))

  # Aggregate methods across all decades
  all_methods <- list()
  for (result in results) {
    for (method in names(result$top_methods)) {
      if (method %in% names(all_methods)) {
        all_methods[[method]] <- all_methods[[method]] + result$top_methods[[method]]
      } else {
        all_methods[[method]] <- result$top_methods[[method]]
      }
    }
  }

  # Sort and display overall top methods
  all_methods <- sort(unlist(all_methods), decreasing = TRUE)
  cat("\nTop methods across all decades:\n")
  for (i in 1:min(10, length(all_methods))) {
    method_name <- names(all_methods)[i]
    method_count <- all_methods[[i]]
    percentage <- (method_count / total_all_papers) * 100
    cat(sprintf("  %s: %d papers (%.1f%%)\n", method_name, method_count, percentage))
  }

  cat("\nEvolution of method detection rates:\n")
  for (decade in names(results)) {
    result <- results[[decade]]
    cat(sprintf(
      "  %s: %.1f%% of papers have methods\n",
      decade, result$method_percentage
    ))
  }

  cat("\nFiles created:\n")
  for (decade in names(results)) {
    decade_short <- gsub("s$", "", tolower(decade))
    cat(sprintf("  expanded_sankey_%s.pdf\n", decade_short))
    cat(sprintf("  expanded_sankey_%s.bmp\n", decade_short))
  }
} else {
  cat("No results to summarize.\n")
}

cat("\nExpanded decade Sankey plots completed!\n")
cat("These plots show much broader method coverage based on your original search terms.\n")
