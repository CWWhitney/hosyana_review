#!/usr/bin/env Rscript
# Comprehensive CSV Converter for R Workflow Compatibility
#
# This script converts the Python analysis results into the format expected
# by the R workflow, creating a comprehensive CSV with method classifications
# that works with ALL bibliography files.
#
# Requirements: Run final_comprehensive_analysis.py first
#
# Usage: Rscript create_comprehensive_csv.R

# Load required libraries
suppressPackageStartupMessages({
  library(dplyr)
  library(stringr)
  library(readr)
  library(tidyr)
})

# Function to convert Python data to R workflow format
create_comprehensive_csv <- function() {
  cat("=== COMPREHENSIVE CSV CONVERTER ===\n")
  cat("Converting Python analysis to R workflow format\n\n")

  # Check if required file exists
  if (!file.exists("FINAL_methods_analysis.csv")) {
    stop("FINAL_methods_analysis.csv not found. Run final_comprehensive_analysis.py first.")
  }

  # Load the comprehensive data
  cat("Loading comprehensive analysis data...\n")
  methods_data <- read_csv("FINAL_methods_analysis.csv", show_col_types = FALSE)
  cat("Loaded", nrow(methods_data), "papers from comprehensive analysis\n")

  # Method columns mapping (Python column -> R friendly name)
  method_mapping <- c(
    "DECISION_ANALYSIS" = "Decision Analysis",
    "POLICY_INTERVENTION" = "Policy Intervention",
    "UNCERTAINTY_ANALYSIS" = "Uncertainty Analysis",
    "STAKEHOLDER_EXPERT" = "Stakeholder Expert Methods",
    "MODELING_SIMULATION" = "Modeling Simulation",
    "BAYESIAN_PROBABILISTIC" = "Bayesian Probabilistic",
    "COMPUTER_ASSISTED" = "Computer Assisted",
    "VALUE_INFORMATION" = "Value Information",
    "MULTI_CRITERIA" = "Multi Criteria",
    "OPTIMIZATION" = "Optimization",
    "ECONOMIC_EVALUATION" = "Economic Evaluation",
    "GAME_THEORY" = "Game Theory",
    "BEHAVIORAL_PSYCHOLOGY" = "Behavioral Psychology",
    "SYSTEMS_COMPLEXITY" = "Systems Complexity",
    "TECHNOLOGY_INNOVATION" = "Technology Innovation",
    "ENVIRONMENTAL_SUSTAINABILITY" = "Environmental Sustainability",
    "QUALITY_PERFORMANCE" = "Quality Performance",
    "RISK_SAFETY" = "Risk Safety",
    "FORECASTING_PREDICTION" = "Forecasting Prediction",
    "EVALUATION_ASSESSMENT" = "Evaluation Assessment"
  )

  method_columns <- names(method_mapping)

  # Create method descriptions
  method_descriptions <- c(
    "Decision Analysis" = "Formal frameworks for structuring and analyzing complex decisions under uncertainty using mathematical models and probability theory.",
    "Policy Intervention" = "Methods for analyzing and designing policy interventions and their impacts on decision-making processes.",
    "Uncertainty Analysis" = "Techniques for quantifying, propagating, and managing uncertainty in decision-making processes.",
    "Stakeholder Expert Methods" = "Approaches for incorporating stakeholder knowledge and expert judgment into decision processes.",
    "Modeling Simulation" = "Computer-based modeling and simulation techniques for decision support and scenario analysis.",
    "Bayesian Probabilistic" = "Bayesian statistical methods and probabilistic approaches to decision-making under uncertainty.",
    "Computer Assisted" = "Computer-based tools and systems that assist in decision-making processes.",
    "Value Information" = "Methods for assessing the value of information in decision-making contexts.",
    "Multi Criteria" = "Multi-criteria decision analysis methods for handling multiple objectives and criteria.",
    "Optimization" = "Mathematical techniques for finding the best solution from a set of feasible alternatives.",
    "Economic Evaluation" = "Economic analysis methods for evaluating costs, benefits, and financial implications of decisions.",
    "Game Theory" = "Game-theoretic approaches to strategic decision-making in competitive or cooperative settings.",
    "Behavioral Psychology" = "Behavioral and psychological approaches to understanding and improving decision-making.",
    "Systems Complexity" = "Systems thinking and complexity science approaches to decision-making in complex environments.",
    "Technology Innovation" = "Methods for managing and evaluating technology adoption and innovation decisions.",
    "Environmental Sustainability" = "Decision-making methods that incorporate environmental sustainability considerations.",
    "Quality Performance" = "Quality management and performance measurement approaches in decision-making.",
    "Risk Safety" = "Risk assessment and safety analysis methods for decision support.",
    "Forecasting Prediction" = "Forecasting and predictive modeling techniques for future-oriented decision-making.",
    "Evaluation Assessment" = "Methods for evaluating and assessing the effectiveness of decisions and interventions."
  )

  cat("Processing method classifications...\n")

  # Filter papers with detected methods and create primary method
  papers_with_methods <- methods_data %>%
    filter(HAS_METHODS == 1) %>%
    rowwise() %>%
    mutate(
      # Find the primary method (first detected method in priority order)
      primary_method = {
        detected_methods <- method_columns[sapply(method_columns, function(col) get(col) == 1)]
        if (length(detected_methods) > 0) {
          method_mapping[detected_methods[1]]
        } else {
          "No Methods Detected"
        }
      },

      # Get all detected methods for subcategories
      all_methods = {
        detected_methods <- method_columns[sapply(method_columns, function(col) get(col) == 1)]
        paste(method_mapping[detected_methods], collapse = "; ")
      },

      # Create method description
      method_description = {
        if (primary_method != "No Methods Detected") {
          method_descriptions[primary_method]
        } else {
          ""
        }
      }
    ) %>%
    ungroup()

  cat("Creating comprehensive CSV output...\n")

  # Create the comprehensive CSV in R workflow format
  comprehensive_csv <- papers_with_methods %>%
    select(
      bibref = BIBREF,
      title = TITLE,
      year = YEAR,
      authors = AUTHORS,
      journal = JOURNAL,
      main_method_category = primary_method,
      all_detected_methods = all_methods,
      method_description,
      confidence = CONFIDENCE,
      abstract = ABSTRACT,
      keywords = KEYWORDS
    ) %>%
    mutate(
      # Add subcategories (simplified - using first 3 detected methods)
      subcategory_1 = sapply(strsplit(all_detected_methods, "; "), function(x) ifelse(length(x) > 1, x[2], "")),
      subcategory_2 = sapply(strsplit(all_detected_methods, "; "), function(x) ifelse(length(x) > 2, x[3], "")),
      subcategory_3 = sapply(strsplit(all_detected_methods, "; "), function(x) ifelse(length(x) > 3, x[4], "")),

      # Clean up NA values
      subcategory_1 = ifelse(is.na(subcategory_1), "", subcategory_1),
      subcategory_2 = ifelse(is.na(subcategory_2), "", subcategory_2),
      subcategory_3 = ifelse(is.na(subcategory_3), "", subcategory_3)
    ) %>%
    arrange(year, bibref)

  # Save the comprehensive CSV
  output_file <- "COMPREHENSIVE_methods_classification.csv"
  write_csv(comprehensive_csv, output_file)

  cat("Comprehensive CSV saved to:", output_file, "\n")

  # Create summary statistics
  cat("\n=== COMPREHENSIVE CSV SUMMARY ===\n")
  cat("Total papers with methods:", nrow(comprehensive_csv), "\n")
  cat("Date range:", min(comprehensive_csv$year, na.rm = TRUE), "-", max(comprehensive_csv$year, na.rm = TRUE), "\n")

  # Method distribution
  method_dist <- comprehensive_csv %>%
    count(main_method_category, sort = TRUE) %>%
    head(10)

  cat("\nTop 10 primary method categories:\n")
  for (i in 1:nrow(method_dist)) {
    cat(sprintf("  %s: %d papers\n", method_dist$main_method_category[i], method_dist$n[i]))
  }

  # Decade distribution
  decade_dist <- comprehensive_csv %>%
    mutate(decade = floor(year / 10) * 10) %>%
    count(decade, sort = FALSE)

  cat("\nPapers by decade:\n")
  for (i in 1:nrow(decade_dist)) {
    cat(sprintf("  %ds: %d papers\n", decade_dist$decade[i], decade_dist$n[i]))
  }

  # Multi-method papers
  multi_method <- comprehensive_csv %>%
    mutate(method_count = str_count(all_detected_methods, ";") + 1) %>%
    filter(method_count > 1)

  cat("\nMulti-method papers:", nrow(multi_method), "papers\n")
  cat("Average methods per paper:", round(mean(str_count(comprehensive_csv$all_detected_methods, ";") + 1), 2), "\n")

  return(list(
    output_file = output_file,
    total_papers = nrow(comprehensive_csv),
    method_distribution = method_dist,
    decade_distribution = decade_dist
  ))
}

# Main execution
if (!interactive()) {
  tryCatch(
    {
      results <- create_comprehensive_csv()
      cat("\n✓ Comprehensive CSV created successfully!\n")
      cat("✓ All", results$total_papers, "papers with detected methods included\n")
      cat("✓ Compatible with R workflow Sankey plot generation\n")
      cat("✓ Method classifications and descriptions added\n")
      cat("\nOutput file:", results$output_file, "\n")
    },
    error = function(e) {
      cat("Error:", e$message, "\n")
      cat("\nPlease ensure you have:\n")
      cat("1. Run 'python3 final_comprehensive_analysis.py' first\n")
      cat("2. Required R packages installed (dplyr, stringr, readr, tidyr)\n")
      stop("Script execution failed")
    }
  )
}
