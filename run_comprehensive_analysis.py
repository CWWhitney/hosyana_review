#!/usr/bin/env python3
"""
Main Comprehensive Analysis Workflow Script
Hosyana Review - Decision Support Methods Analysis

This script orchestrates the complete analysis workflow using the organized file structure.
It runs all components in the correct order and generates all outputs.

Usage:
    python3 run_comprehensive_analysis.py

Outputs:
    - data/analysis_results/ : CSV files with analysis results
    - data/reports/ : JSON reports and logs
    - figures/sankey_plots/ : Publication-ready PDF Sankey plots
    - figures/interactive/ : Interactive HTML visualizations
    - docs/ : Documentation and summaries
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_step(step, description):
    """Print a formatted step"""
    print(f"\n🔄 Step {step}: {description}")
    print("-" * 60)


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    print(f"Command: {command}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True, cwd="."
        )

        if result.stdout:
            print(
                "Output:",
                result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""),
            )

        print("✅ Completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath) / 1024  # KB
        print(f"✅ {description}: {filepath} ({size:.1f} KB)")
        return True
    else:
        print(f"❌ Missing: {description}: {filepath}")
        return False


def main():
    """Main workflow execution"""

    print_header("COMPREHENSIVE HOSYANA REVIEW ANALYSIS WORKFLOW")
    print("Processing ALL bibliography files with organized output structure")
    print(f"Working directory: {os.getcwd()}")

    # Verify we're in the right directory
    if not os.path.exists("hosyana_review.Rproj"):
        print("❌ Error: Not in hosyana_review directory")
        print("Please run this script from the hosyana_review project root")
        sys.exit(1)

    # Check required directories exist
    required_dirs = [
        "bib/bib_raw",
        "scripts/python",
        "scripts/r",
        "data/analysis_results",
        "data/reports",
        "figures/sankey_plots",
        "figures/interactive",
        "docs",
    ]

    print("\n📁 Verifying directory structure...")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ Missing: {directory}")
            os.makedirs(directory, exist_ok=True)
            print(f"   Created: {directory}")

    # Count bibliography files
    bib_files = list(Path("bib/bib_raw").glob("*.bib"))
    print(f"\n📚 Found {len(bib_files)} bibliography files to process")

    start_time = time.time()

    # Step 1: Run comprehensive Python analysis
    print_step(1, "Python Comprehensive Analysis")
    success = run_command(
        "python3 scripts/python/final_comprehensive_analysis.py",
        "Analyzing all bibliography files and detecting methods",
    )

    if not success:
        print("❌ Failed to complete Python analysis. Stopping workflow.")
        sys.exit(1)

    # Step 2: Generate interactive Python visualizations
    print_step(2, "Interactive Visualizations")
    success = run_command(
        "python3 scripts/python/create_sankey_plots.py",
        "Creating interactive HTML Sankey plots and visualizations",
    )

    if not success:
        print("⚠️  Warning: Interactive visualizations failed, continuing...")

    # Step 3: Generate R-compatible CSV
    print_step(3, "R-Compatible Data Generation")
    success = run_command(
        "Rscript scripts/r/create_comprehensive_csv.R",
        "Converting Python results to R-compatible format",
    )

    if not success:
        print("⚠️  Warning: R CSV generation failed, continuing...")

    # Step 4: Generate R-style Sankey plots
    print_step(4, "Publication-Ready Sankey Plots")
    success = run_command(
        "Rscript scripts/r/create_comprehensive_sankey.R",
        "Creating publication-ready PDF Sankey plots",
    )

    if not success:
        print("⚠️  Warning: R Sankey plots failed, continuing...")

    # Step 5: Generate comprehensive report
    print_step(5, "HTML Report Generation")
    success = run_command(
        "Rscript -e \"rmarkdown::render('index.Rmd')\"",
        "Generating comprehensive HTML report",
    )

    if not success:
        print("⚠️  Warning: HTML report generation failed, continuing...")

    # Verify outputs
    print_header("OUTPUT VERIFICATION")

    # Check main analysis files
    print("\n📊 Analysis Results:")
    check_file_exists(
        "data/analysis_results/FINAL_methods_analysis.csv", "Main analysis CSV"
    )
    check_file_exists(
        "data/analysis_results/COMPREHENSIVE_methods_classification.csv",
        "R-compatible CSV",
    )

    # Check reports
    print("\n📋 Reports:")
    check_file_exists("data/reports/FINAL_analysis_report.json", "Analysis summary")
    check_file_exists("data/reports/FINAL_sankey_data.json", "Sankey data")
    check_file_exists("data/reports/final_analysis.log", "Processing log")

    # Check visualizations
    print("\n📈 Visualizations:")
    sankey_files = [
        "figures/sankey_plots/comprehensive_sankey_1970.pdf",
        "figures/sankey_plots/comprehensive_sankey_1980.pdf",
        "figures/sankey_plots/comprehensive_sankey_1990.pdf",
        "figures/sankey_plots/comprehensive_sankey_2000.pdf",
        "figures/sankey_plots/comprehensive_sankey_2010.pdf",
        "figures/sankey_plots/comprehensive_sankey_2020.pdf",
        "figures/sankey_plots/comprehensive_sankey_2024.pdf",
    ]

    sankey_count = 0
    for sankey_file in sankey_files:
        if check_file_exists(sankey_file, f"Sankey plot"):
            sankey_count += 1

    interactive_files = [
        "figures/interactive/decade_method_sankey.html",
        "figures/interactive/method_evolution_sankey.html",
        "figures/interactive/methods_by_decade_bar.html",
        "figures/interactive/method_trends_lines.html",
    ]

    interactive_count = 0
    for interactive_file in interactive_files:
        if check_file_exists(interactive_file, "Interactive visualization"):
            interactive_count += 1

    # Check documentation
    print("\n📚 Documentation:")
    check_file_exists("docs/COMPREHENSIVE_ANALYSIS_SUMMARY.md", "Analysis summary")
    check_file_exists("index.html", "Main HTML report")

    # Final summary
    elapsed_time = time.time() - start_time
    print_header("WORKFLOW COMPLETE")

    print(f"⏱️  Total execution time: {elapsed_time / 60:.1f} minutes")
    print(f"📚 Bibliography files processed: {len(bib_files)}")
    print(f"📊 PDF Sankey plots created: {sankey_count}/7")
    print(f"📈 Interactive visualizations: {interactive_count}/4")

    # Quick statistics from main analysis file
    if os.path.exists("data/analysis_results/FINAL_methods_analysis.csv"):
        try:
            import pandas as pd

            df = pd.read_csv("data/analysis_results/FINAL_methods_analysis.csv")
            papers_with_methods = len(df[df["HAS_METHODS"] == 1])
            detection_rate = papers_with_methods / len(df) * 100

            print(f"📄 Total papers analyzed: {len(df):,}")
            print(f"🔍 Papers with methods detected: {papers_with_methods:,}")
            print(f"📈 Detection rate: {detection_rate:.1f}%")

        except ImportError:
            print("📄 Analysis files created (pandas not available for stats)")
        except Exception as e:
            print(f"📄 Analysis files created (could not read stats: {e})")

    print("\n🎉 COMPREHENSIVE ANALYSIS WORKFLOW COMPLETED SUCCESSFULLY!")
    print("\nNext steps:")
    print("  • Review results in data/analysis_results/")
    print("  • View PDF plots in figures/sankey_plots/")
    print("  • Open interactive visualizations in figures/interactive/")
    print("  • Read analysis summary in docs/COMPREHENSIVE_ANALYSIS_SUMMARY.md")
    print("  • View complete report: open index.html in browser")


if __name__ == "__main__":
    main()
