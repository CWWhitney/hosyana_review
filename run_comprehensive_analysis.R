#!/usr/bin/env Rscript
# Main Comprehensive Analysis Workflow Script (R)
# Hosyana Review - Decision Support Methods Analysis
#
# This script orchestrates the complete R analysis workflow using the organized file structure.
# It runs all R components and generates outputs in the correct directories.
#
# Usage:
#     Rscript run_comprehensive_analysis.R
#
# Outputs:
#     - data/analysis_results/ : R-compatible CSV files
#     - figures/sankey_plots/ : Publication-ready PDF Sankey plots
#     - index.html : Comprehensive HTML report

# Load required packages
suppressPackageStartupMessages({
  library(knitr)
  library(rmarkdown)
})

# Function to print formatted headers
print_header <- function(title) {
  cat("\n", paste(rep("=", 80), collapse = ""), "\n")
  cat(" ", title, "\n")
  cat(paste(rep("=", 80), collapse = ""), "\n\n")
}

# Function to print formatted steps
print_step <- function(step, description) {
  cat("\n🔄 Step", step, ":", description, "\n")
  cat(paste(rep("-", 60), collapse = ""), "\n")
}

# Function to run R scripts and handle errors
run_r_script <- function(script_path, description) {
  cat("Running:", description, "\n")
  cat("Script:", script_path, "\n")

  tryCatch(
    {
      source(script_path)
      cat("✅ Completed successfully\n")
      return(TRUE)
    },
    error = function(e) {
      cat("❌ Error:", e$message, "\n")
      return(FALSE)
    }
  )
}

# Function to check if file exists
check_file_exists <- function(filepath, description) {
  if (file.exists(filepath)) {
    size <- round(file.info(filepath)$size / 1024, 1) # KB
    cat("✅", description, ":", filepath, "(", size, "KB)\n")
    return(TRUE)
  } else {
    cat("❌ Missing:", description, ":", filepath, "\n")
    return(FALSE)
  }
}

# Main workflow function
main <- function() {
  print_header("COMPREHENSIVE HOSYANA REVIEW ANALYSIS WORKFLOW (R)")
  cat("Processing data with organized R workflow\n")
  cat("Working directory:", getwd(), "\n")

  # Verify we're in the right directory
  if (!file.exists("hosyana_review.Rproj")) {
    cat("❌ Error: Not in hosyana_review directory\n")
    cat("Please run this script from the hosyana_review project root\n")
    quit(status = 1)
  }

  # Check required directories exist
  required_dirs <- c(
    "data/analysis_results",
    "data/reports",
    "figures/sankey_plots",
    "scripts/r",
    "docs"
  )

  cat("\n📁 Verifying directory structure...\n")
  for (directory in required_dirs) {
    if (dir.exists(directory)) {
      cat("✅", directory, "\n")
    } else {
      cat("❌ Missing:", directory, "\n")
      dir.create(directory, recursive = TRUE, showWarnings = FALSE)
      cat("   Created:", directory, "\n")
    }
  }

  # Check if Python analysis results exist
  python_results <- "data/analysis_results/FINAL_methods_analysis.csv"
  if (!file.exists(python_results)) {
    cat("❌ Error: Python analysis results not found:", python_results, "\n")
    cat("Please run the Python analysis first:\n")
    cat("   python3 run_comprehensive_analysis.py\n")
    quit(status = 1)
  }

  start_time <- Sys.time()

  # Step 1: Generate R-compatible CSV
  print_step(1, "R-Compatible Data Generation")
  success <- run_r_script(
    "scripts/r/create_comprehensive_csv.R",
    "Converting Python results to R-compatible format"
  )

  if (!success) {
    cat("❌ Failed to create R-compatible CSV. Stopping workflow.\n")
    quit(status = 1)
  }

  # Step 2: Generate R-style Sankey plots
  print_step(2, "Publication-Ready Sankey Plots")
  success <- run_r_script(
    "scripts/r/create_comprehensive_sankey.R",
    "Creating publication-ready PDF Sankey plots"
  )

  if (!success) {
    cat("⚠️  Warning: R Sankey plots failed, continuing...\n")
  }

  # Step 3: Generate comprehensive R Markdown report
  print_step(3, "HTML Report Generation")
  tryCatch(
    {
      cat("Rendering index.Rmd to HTML...\n")
      rmarkdown::render("index.Rmd")
      cat("✅ HTML report generated successfully\n")
    },
    error = function(e) {
      cat("⚠️  Warning: HTML report generation failed:", e$message, "\n")
    }
  )

  # Verify outputs
  print_header("OUTPUT VERIFICATION")

  # Check analysis files
  cat("\n📊 Analysis Results:\n")
  check_file_exists(
    "data/analysis_results/FINAL_methods_analysis.csv",
    "Python analysis CSV"
  )
  check_file_exists(
    "data/analysis_results/COMPREHENSIVE_methods_classification.csv",
    "R-compatible CSV"
  )

  # Check Sankey plots
  cat("\n📈 Sankey Plots:\n")
  sankey_files <- c(
    "figures/sankey_plots/comprehensive_sankey_1970.pdf",
    "figures/sankey_plots/comprehensive_sankey_1980.pdf",
    "figures/sankey_plots/comprehensive_sankey_1990.pdf",
    "figures/sankey_plots/comprehensive_sankey_2000.pdf",
    "figures/sankey_plots/comprehensive_sankey_2010.pdf",
    "figures/sankey_plots/comprehensive_sankey_2020.pdf",
    "figures/sankey_plots/comprehensive_sankey_2024.pdf"
  )

  sankey_count <- 0
  for (sankey_file in sankey_files) {
    if (check_file_exists(sankey_file, "Sankey plot")) {
      sankey_count <- sankey_count + 1
    }
  }

  # Check documentation
  cat("\n📚 Documentation:\n")
  check_file_exists("docs/COMPREHENSIVE_ANALYSIS_SUMMARY.md", "Analysis summary")
  check_file_exists("index.html", "Main HTML report")

  # Final summary
  elapsed_time <- as.numeric(difftime(Sys.time(), start_time, units = "mins"))
  print_header("R WORKFLOW COMPLETE")

  cat("⏱️  Total execution time:", round(elapsed_time, 1), "minutes\n")
  cat("📊 PDF Sankey plots created:", sankey_count, "/7\n")

  # Quick statistics if CSV available
  if (file.exists("data/analysis_results/COMPREHENSIVE_methods_classification.csv")) {
    tryCatch(
      {
        df <- read.csv("data/analysis_results/COMPREHENSIVE_methods_classification.csv")
        cat("📄 Papers with methods in R CSV:", nrow(df), "\n")

        # Get year range
        if ("year" %in% names(df)) {
          year_range <- range(df$year, na.rm = TRUE)
          cat("📅 Year coverage:", year_range[1], "-", year_range[2], "\n")
        }
      },
      error = function(e) {
        cat("📄 R CSV created (could not read stats):", e$message, "\n")
      }
    )
  }

  cat("\n🎉 R ANALYSIS WORKFLOW COMPLETED SUCCESSFULLY!\n")
  cat("\nR-specific outputs:\n")
  cat("  • R-compatible data: data/analysis_results/COMPREHENSIVE_methods_classification.csv\n")
  cat("  • Publication plots: figures/sankey_plots/comprehensive_sankey_*.pdf\n")
  cat("  • HTML report: index.html\n")
  cat("\nFor complete workflow including Python analysis, run:\n")
  cat("  python3 run_comprehensive_analysis.py\n")
}

# Execute main function if script is run directly
if (!interactive()) {
  main()
}
