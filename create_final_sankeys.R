# Create Final Sankey Plots for Decision Support Methods Analysis
# Uses the existing plot_sankey.R function with finalized comprehensive data
# Generates simple, clean decade-by-decade Sankey plots showing method evolution

library(jsonlite)

# Source the existing plot_sankey function
source("R/plot_sankey.R")

# Read the finalized sankey data
final_data <- fromJSON("FINAL_sankey_data.json")

# Function to create finalized Sankey for one decade
create_final_sankey <- function(decade_name, decade_data) {
  total_papers <- decade_data$total_papers
  methods <- decade_data$methods

  # Skip decades with insufficient papers for meaningful analysis
  if (total_papers < 80) {
    cat("Skipping", decade_name, "- only", total_papers, "papers (minimum 80 required)\n")
    return(NULL)
  }

  # Get method counts and sort by frequency
  method_counts <- unlist(methods)
  method_counts <- method_counts[method_counts > 0]
  method_counts <- sort(method_counts, decreasing = TRUE)

  # Take top methods for clear visualization (8 max for readability)
  top_methods <- head(method_counts, 8)

  # Calculate papers with identified methods vs. others
  papers_with_methods <- sum(top_methods)
  papers_other <- total_papers - papers_with_methods

  # Prepare data for plot_sankey function
  inputs <- total_papers
  losses <- c(as.numeric(top_methods), papers_other)
  unit <- "papers"

  # Create readable method labels
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

  # Create PDF version using your original plot_sankey function
  plot_sankey(
    inputs = inputs,
    losses = losses,
    unit = unit,
    labels = labels,
    format = "pdf"
  )

  # Rename the generated file
  if (file.exists("Sankey.pdf")) {
    new_name <- paste0("FINAL_sankey_", gsub("s$", "", tolower(decade_name)), ".pdf")
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
    new_name <- paste0("FINAL_sankey_", gsub("s$", "", tolower(decade_name)), ".bmp")
    file.rename("Sankey.bmp", new_name)
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
cat("Creating Final Sankey Plots for Decision Support Methods Analysis\n")
cat("Using finalized data with 66.4% method detection rate\n")
cat(rep("=", 75), "\n")

# Get decades with substantial data for meaningful Sankey plots
decades_to_plot <- names(final_data)[sapply(final_data, function(x) x$total_papers >= 80)]
decades_to_plot <- sort(decades_to_plot)

cat("Decades selected for Sankey plots:", paste(decades_to_plot, collapse = ", "), "\n\n")

# Create plots for each selected decade
results <- list()
for (decade in decades_to_plot) {
  cat("Processing", decade, "...\n")

  result <- create_final_sankey(decade, final_data[[decade]])
  if (!is.null(result)) {
    results[[decade]] <- result

    # Print detailed summary
    cat(sprintf("  Total papers: %d\n", result$total_papers))
    cat(sprintf(
      "  Papers with methods: %d (%.1f%%)\n",
      result$method_papers, result$method_percentage
    ))
    cat(sprintf("  Method categories shown: %d\n", result$method_count))
    cat("  Top methods in", decade, ":\n")

    for (i in seq_along(result$top_methods)) {
      method_name <- names(result$top_methods)[i]
      method_count <- result$top_methods[[i]]
      percentage <- round((method_count / result$total_papers) * 100, 1)
      cat(sprintf(
        "    %d. %s: %d papers (%.1f%%)\n",
        i, method_name, method_count, percentage
      ))
    }
    cat("\n")
  }
}

# Generate comprehensive summary
cat(rep("=", 75), "\n")
cat("FINAL SANKEY ANALYSIS SUMMARY\n")
cat(rep("=", 75), "\n")

if (length(results) > 0) {
  total_all_papers <- sum(sapply(results, function(x) x$total_papers))
  total_method_papers <- sum(sapply(results, function(x) x$method_papers))
  overall_percentage <- round((total_method_papers / total_all_papers) * 100, 1)

  cat(sprintf("Decades analyzed: %d\n", length(results)))
  cat(sprintf("Total papers across all decades: %d\n", total_all_papers))
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

  # Display top methods across all decades
  all_methods <- sort(unlist(all_methods), decreasing = TRUE)
  cat("\nTop methods across all plotted decades:\n")
  for (i in 1:min(10, length(all_methods))) {
    method_name <- names(all_methods)[i]
    method_count <- all_methods[[i]]
    percentage <- round((method_count / total_all_papers) * 100, 1)
    cat(sprintf(
      "  %d. %s: %d papers (%.1f%%)\n",
      i, method_name, method_count, percentage
    ))
  }

  # Show evolution of method adoption rates
  cat("\nMethod adoption rates by decade:\n")
  for (decade in names(results)) {
    result <- results[[decade]]
    cat(sprintf(
      "  %s: %.1f%% of papers use identifiable methods\n",
      decade, result$method_percentage
    ))
  }

  # List all generated files
  cat("\nGenerated Sankey plot files:\n")
  for (decade in names(results)) {
    decade_short <- gsub("s$", "", tolower(decade))
    cat(sprintf("  FINAL_sankey_%s.pdf (vector graphics)\n", decade_short))
    cat(sprintf("  FINAL_sankey_%s.bmp (raster image)\n", decade_short))
  }

  cat("\nEvolution story revealed by Sankey plots:\n")
  decade_names <- names(results)
  if (length(decade_names) >= 2) {
    first_decade <- results[[decade_names[1]]]
    last_decade <- results[[decade_names[length(decade_names)]]]

    cat(sprintf(
      "  %s: %d papers, %.1f%% with methods\n",
      first_decade$decade, first_decade$total_papers, first_decade$method_percentage
    ))
    cat(sprintf(
      "  %s: %d papers, %.1f%% with methods\n",
      last_decade$decade, last_decade$total_papers, last_decade$method_percentage
    ))

    growth_factor <- round(last_decade$total_papers / first_decade$total_papers, 1)
    cat(sprintf("  Growth: %.1fx increase in papers over time\n", growth_factor))
  }
} else {
  cat("No decades met the minimum criteria for Sankey plot generation.\n")
}

cat(rep("=", 75), "\n")
cat("FINAL SANKEY PLOTS COMPLETED SUCCESSFULLY\n")
cat("Each plot shows: Decade Total → Top Method Categories → Other Methods\n")
cat("Plots reveal the evolution of decision support methods across decades\n")
cat(rep("=", 75), "\n")

# Save a summary of the Sankey analysis
sankey_summary <- list(
  analysis_date = Sys.Date(),
  total_decades_analyzed = length(results),
  total_papers_in_sankeys = if (length(results) > 0) sum(sapply(results, function(x) x$total_papers)) else 0,
  overall_method_rate = if (length(results) > 0) {
    total_method_papers <- sum(sapply(results, function(x) x$method_papers))
    total_all_papers <- sum(sapply(results, function(x) x$total_papers))
    round((total_method_papers / total_all_papers) * 100, 1)
  } else {
    0
  },
  decades_plotted = names(results),
  top_methods_overall = if (exists("all_methods")) names(all_methods)[1:min(5, length(all_methods))] else c()
)

# Save summary as JSON for reference
library(jsonlite)
write_json(sankey_summary, "FINAL_sankey_summary.json", pretty = TRUE)
cat("Analysis summary saved to: FINAL_sankey_summary.json\n")
