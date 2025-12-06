#!/usr/bin/env Rscript
# Comprehensive Sankey Plot Generator using Python Analysis Results
#
# This script creates R-style Sankey plots using the comprehensive analysis
# from final_comprehensive_analysis.py which processes ALL bib files.
#
# Requirements: Run final_comprehensive_analysis.py first to generate data files
#
# Usage: Rscript create_comprehensive_sankey.R

# Load required libraries
suppressPackageStartupMessages({
  library(dplyr)
  library(purrr)
  library(jsonlite)
  library(stringr)
  library(tidyr)
})

# Source the plotting function
source("R/plot_sankey.R")

# Function to create Sankey plots from comprehensive data
create_comprehensive_sankey <- function() {
  cat("Loading comprehensive analysis data...\n")

  # Check if required files exist
  if (!file.exists("FINAL_methods_analysis.csv")) {
    stop("FINAL_methods_analysis.csv not found. Run final_comprehensive_analysis.py first.")
  }

  if (!file.exists("FINAL_sankey_data.json")) {
    stop("FINAL_sankey_data.json not found. Run final_comprehensive_analysis.py first.")
  }

  # Load the comprehensive data
  methods_data <- read.csv("FINAL_methods_analysis.csv", stringsAsFactors = FALSE)
  sankey_data <- fromJSON("FINAL_sankey_data.json")

  cat("Loaded", nrow(methods_data), "papers from comprehensive analysis\n")

  # Method columns in the CSV (binary indicators)
  method_columns <- c(
    "DECISION_ANALYSIS", "POLICY_INTERVENTION", "UNCERTAINTY_ANALYSIS",
    "STAKEHOLDER_EXPERT", "MODELING_SIMULATION", "BAYESIAN_PROBABILISTIC",
    "COMPUTER_ASSISTED", "VALUE_INFORMATION", "MULTI_CRITERIA", "OPTIMIZATION",
    "ECONOMIC_EVALUATION", "GAME_THEORY", "BEHAVIORAL_PSYCHOLOGY",
    "SYSTEMS_COMPLEXITY", "TECHNOLOGY_INNOVATION", "ENVIRONMENTAL_SUSTAINABILITY",
    "QUALITY_PERFORMANCE", "RISK_SAFETY", "FORECASTING_PREDICTION", "EVALUATION_ASSESSMENT"
  )

  # Convert binary method columns to long format
  method_long <- methods_data %>%
    filter(HAS_METHODS == 1) %>% # Only papers with detected methods
    mutate(
      decade = case_when(
        YEAR >= 2020 & YEAR <= 2024 ~ 2024, # Special category for 2020-2024
        TRUE ~ floor(YEAR / 10) * 10
      ),
      decade = ifelse(decade < 1950, 1950, decade) # Group early decades
    ) %>%
    filter(decade >= 1970) %>%
    select(BIBREF, decade, all_of(method_columns)) %>%
    tidyr::pivot_longer(cols = all_of(method_columns), names_to = "method", values_to = "detected") %>%
    filter(detected == 1)

  # Count methods by decade
  method_counts <- method_long %>%
    count(decade, method, sort = TRUE)

  cat("Processing method counts by decade...\n")

  # Create decade-specific Sankey plots (including 2020-2024)
  decades <- c(seq(1970, 2020, 10), 2024)

  for (target_decade in decades) {
    period_label <- ifelse(target_decade == 2024, "2020-2024", paste0(target_decade, "s"))
    cat("Creating Sankey plot for", period_label, "period...\n")

    # Get data for this decade/period
    decade_data <- method_counts %>%
      filter(decade == target_decade) %>%
      arrange(desc(n)) %>%
      head(8) # Top 8 methods for clarity

    if (nrow(decade_data) == 0) {
      cat("No data for", period_label, "period, skipping...\n")
      next
    }

    total_papers <- sum(decade_data$n)

    # Prepare data for Sankey
    inputs <- c(total_papers, 0)
    losses <- decade_data$n

    # Create labels
    method_labels <- decade_data$method %>%
      str_replace_all("_", " ") %>%
      str_to_title() %>%
      str_trunc(25) # Truncate long names

    labels <- c(
      paste("Total Papers", period_label),
      "Flow",
      method_labels
    )

    # Create the plot
    pdf_name <- paste0("comprehensive_sankey_", target_decade, ".pdf")

    pdf(pdf_name, width = 12, height = 8)
    par(cex = 0.8, cex.main = 1.0, cex.lab = 0.8, cex.axis = 0.8)

    plot_sankey(inputs, losses, "Papers", labels)

    # Add title
    title(paste("Decision Support Methods -", period_label),
      cex.main = 1.2, font.main = 2
    )

    dev.off()

    cat("Created", pdf_name, "with", total_papers, "papers and", nrow(decade_data), "method types\n")
  }

  # Create summary statistics
  cat("\n=== COMPREHENSIVE SANKEY SUMMARY ===\n")

  total_papers_with_methods <- methods_data %>%
    filter(HAS_METHODS == 1) %>%
    nrow()

  decade_summary <- method_counts %>%
    group_by(decade) %>%
    summarise(
      papers = sum(n),
      method_types = n(),
      .groups = "drop"
    )

  cat("Total papers with methods detected:", total_papers_with_methods, "\n")
  cat("Coverage by decade/period:\n")

  for (i in 1:nrow(decade_summary)) {
    decade <- decade_summary$decade[i]
    papers <- decade_summary$papers[i]
    types <- decade_summary$method_types[i]
    period_label <- ifelse(decade == 2024, "2020-2024", paste0(decade, "s"))
    cat(sprintf("  %s: %d papers, %d method types\n", period_label, papers, types))
  }

  # Top methods overall
  top_methods <- method_counts %>%
    group_by(method) %>%
    summarise(total_papers = sum(n), .groups = "drop") %>%
    arrange(desc(total_papers)) %>%
    head(10)

  cat("\nTop 10 methods across all decades:\n")
  for (i in 1:nrow(top_methods)) {
    method <- str_replace_all(top_methods$method[i], "_", " ")
    count <- top_methods$total_papers[i]
    cat(sprintf("  %s: %d papers\n", method, count))
  }

  cat("\n=== FILES CREATED ===\n")
  created_files <- paste0("comprehensive_sankey_", decades, ".pdf")
  existing_files <- created_files[file.exists(created_files)]

  if (length(existing_files) > 0) {
    cat("Successfully created Sankey plots:\n")
    for (file in existing_files) {
      period_info <- ifelse(grepl("2024", file), " (2020-2024 period)", "")
      cat("  ✓", file, period_info, "\n")
    }
  } else {
    cat("No Sankey plots were created.\n")
  }

  return(list(
    decade_summary = decade_summary,
    top_methods = top_methods,
    total_papers = total_papers_with_methods
  ))
}

# Main execution
if (!interactive()) {
  cat("=== COMPREHENSIVE SANKEY PLOT GENERATOR ===\n")
  cat("Processing ALL bibliography files through Python analysis results\n\n")

  tryCatch(
    {
      results <- create_comprehensive_sankey()
      cat("\n✓ Comprehensive Sankey plots generated successfully!\n")
      cat("✓ All bibliography files processed\n")
      cat("✓ Method detection completed\n")
      cat("✓ Sankey visualizations created\n")
    },
    error = function(e) {
      cat("Error:", e$message, "\n")
      cat("\nPlease ensure you have:\n")
      cat("1. Run 'python3 final_comprehensive_analysis.py' first\n")
      cat("2. Required R packages installed (dplyr, purrr, jsonlite, stringr)\n")
      cat("3. plot_sankey.R file available in R/ directory\n")
      stop("Script execution failed")
    }
  )
}
