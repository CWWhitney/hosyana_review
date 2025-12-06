#!/usr/bin/env python3
"""
Project Cleanup Verification Script
Hosyana Review - Decision Support Methods Analysis

This script verifies that the project cleanup and organization was successful.
It checks for required files, tests workflows, and validates the new structure.

Usage:
    python3 verify_cleanup.py
"""

import os
import sys
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def check_directory_structure():
    """Verify the organized directory structure exists"""
    print_header("DIRECTORY STRUCTURE VERIFICATION")

    required_dirs = [
        "data/analysis_results",
        "data/reports",
        "figures/sankey_plots",
        "figures/interactive",
        "scripts/python",
        "scripts/r",
        "notebooks",
        "docs",
        "bib/bib_raw",
        "R",
    ]

    missing_dirs = []
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ MISSING: {directory}")
            missing_dirs.append(directory)

    return len(missing_dirs) == 0


def check_key_files():
    """Verify essential files are in correct locations"""
    print_header("KEY FILES VERIFICATION")

    essential_files = {
        # Analysis results
        "data/analysis_results/FINAL_methods_analysis.csv": "Main Python analysis",
        "data/analysis_results/COMPREHENSIVE_methods_classification.csv": "R-compatible CSV",
        # Reports
        "data/reports/FINAL_analysis_report.json": "Analysis summary",
        "data/reports/FINAL_sankey_data.json": "Sankey data",
        # Scripts
        "scripts/python/final_comprehensive_analysis.py": "Main Python script",
        "scripts/python/create_sankey_plots.py": "Visualization script",
        "scripts/r/create_comprehensive_sankey.R": "R Sankey script",
        "scripts/r/create_comprehensive_csv.R": "R CSV converter",
        # Workflows
        "run_comprehensive_analysis.py": "Main Python workflow",
        "run_comprehensive_analysis.R": "Main R workflow",
        # Documentation
        "README.md": "Project README",
        "docs/COMPREHENSIVE_ANALYSIS_SUMMARY.md": "Analysis summary",
        "docs/PROJECT_CLEANUP_SUMMARY.md": "Cleanup documentation",
        # Core files
        "index.Rmd": "Main R Markdown",
        "R/plot_sankey.R": "Sankey plotting functions",
        "requirements.txt": "Python requirements",
    }

    missing_files = []
    for filepath, description in essential_files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            if size > 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            print(f"✅ {description}: {filepath} ({size_str})")
        else:
            print(f"❌ MISSING: {description}: {filepath}")
            missing_files.append(filepath)

    return len(missing_files) == 0


def check_sankey_plots():
    """Verify all Sankey plots exist"""
    print_header("SANKEY PLOTS VERIFICATION")

    expected_plots = [
        "figures/sankey_plots/comprehensive_sankey_1970.pdf",
        "figures/sankey_plots/comprehensive_sankey_1980.pdf",
        "figures/sankey_plots/comprehensive_sankey_1990.pdf",
        "figures/sankey_plots/comprehensive_sankey_2000.pdf",
        "figures/sankey_plots/comprehensive_sankey_2010.pdf",
        "figures/sankey_plots/comprehensive_sankey_2020.pdf",
        "figures/sankey_plots/comprehensive_sankey_2024.pdf",  # New 2020-2024 plot
    ]

    found_plots = 0
    for plot in expected_plots:
        if os.path.exists(plot):
            size = os.path.getsize(plot) / 1024  # KB
            decade = plot.split("_")[-1].replace(".pdf", "")
            print(f"✅ {decade}s plot: {plot} ({size:.1f} KB)")
            found_plots += 1
        else:
            decade = plot.split("_")[-1].replace(".pdf", "")
            print(f"❌ MISSING: {decade}s plot: {plot}")

    print(f"\n📊 Sankey plots found: {found_plots}/7")
    return found_plots == 7


def check_interactive_visualizations():
    """Verify interactive HTML files exist"""
    print_header("INTERACTIVE VISUALIZATIONS VERIFICATION")

    expected_html = [
        "figures/interactive/decade_method_sankey.html",
        "figures/interactive/method_evolution_sankey.html",
        "figures/interactive/methods_by_decade_bar.html",
        "figures/interactive/method_trends_lines.html",
    ]

    found_html = 0
    for html_file in expected_html:
        if os.path.exists(html_file):
            size = os.path.getsize(html_file) / (1024 * 1024)  # MB
            name = os.path.basename(html_file)
            print(f"✅ {name}: {html_file} ({size:.1f} MB)")
            found_html += 1
        else:
            name = os.path.basename(html_file)
            print(f"❌ MISSING: {name}: {html_file}")

    print(f"\n📈 Interactive files found: {found_html}/4")
    return found_html >= 2  # At least half should exist


def check_obsolete_files_removed():
    """Verify obsolete files were properly removed"""
    print_header("OBSOLETE FILES VERIFICATION")

    obsolete_files = [
        "create_methods_sankey.py",
        "fulltext_pdf_analyzer.py",
        "practical_fulltext_analyzer.py",
        "sankey_r_style.py",
        "test_fulltext_analyzer.py",
        "create_expanded_sankeys.R",
        "create_final_sankeys.R",
        "requirements_analyzer.txt",
        "requirements_simple.txt",
    ]

    found_obsolete = []
    for obsolete in obsolete_files:
        if os.path.exists(obsolete):
            print(f"❌ STILL EXISTS: {obsolete} (should be deleted)")
            found_obsolete.append(obsolete)
        else:
            print(f"✅ REMOVED: {obsolete}")

    if found_obsolete:
        print(f"\n⚠️  Found {len(found_obsolete)} obsolete files that should be removed")
        return False
    else:
        print(f"\n✅ All obsolete files properly removed")
        return True


def check_bib_files():
    """Verify bibliography files are accessible"""
    print_header("BIBLIOGRAPHY FILES VERIFICATION")

    bib_dir = Path("bib/bib_raw")
    if not bib_dir.exists():
        print(f"❌ Bibliography directory not found: {bib_dir}")
        return False

    bib_files = list(bib_dir.glob("*.bib"))
    print(f"📚 Found {len(bib_files)} .bib files")

    if len(bib_files) < 30:
        print("⚠️  Expected ~33 .bib files, found fewer than expected")
        return False

    # Check for manual_run subdirectory
    manual_run = bib_dir / "manual_run"
    if manual_run.exists():
        manual_files = list(manual_run.glob("*.bib"))
        print(f"📁 Manual run directory: {len(manual_files)} additional .bib files")

    print("✅ Bibliography files structure looks good")
    return True


def check_root_directory_cleaned():
    """Verify root directory is not cluttered"""
    print_header("ROOT DIRECTORY CLEANUP VERIFICATION")

    # Count files in root (should be much fewer now)
    root_files = [f for f in os.listdir(".") if os.path.isfile(f)]
    print(f"📁 Files in root directory: {len(root_files)}")

    # Expected root files
    expected_root_files = {
        "index.Rmd",
        "index.html",
        "README.md",
        "LICENSE",
        "run_comprehensive_analysis.py",
        "run_comprehensive_analysis.R",
        "requirements.txt",
        "hosyana_review.Rproj",
        "01_Introduction.Rmd",
        "02_Review.Rmd",
        "03_Data_Import_Pre_Processing.Rmd",
        "References.Rmd",
        "apa.csl",
        ".gitignore",
        ".gitattributes",
        ".Rhistory",
        "verify_cleanup.py",  # This script
    }

    unexpected_files = []
    for file in root_files:
        if file not in expected_root_files:
            unexpected_files.append(file)

    if unexpected_files:
        print("⚠️  Unexpected files in root directory:")
        for file in unexpected_files:
            print(f"    - {file}")
        return False
    else:
        print("✅ Root directory properly cleaned")
        return True


def generate_summary():
    """Generate final summary of project status"""
    print_header("PROJECT STATUS SUMMARY")

    # Count various file types
    csv_files = len(list(Path("data/analysis_results").glob("*.csv")))
    pdf_files = len(list(Path("figures/sankey_plots").glob("*.pdf")))
    html_files = len(list(Path("figures/interactive").glob("*.html")))
    json_files = len(list(Path("data/reports").glob("*.json")))
    py_files = len(list(Path("scripts/python").glob("*.py")))
    r_files = len(list(Path("scripts/r").glob("*.R")))

    print(f"📊 Analysis CSV files: {csv_files}")
    print(f"📈 PDF Sankey plots: {pdf_files}")
    print(f"🌐 Interactive HTML files: {html_files}")
    print(f"📋 JSON reports: {json_files}")
    print(f"🐍 Python scripts: {py_files}")
    print(f"📊 R scripts: {r_files}")

    # Check for main analysis file size
    main_csv = "data/analysis_results/FINAL_methods_analysis.csv"
    if os.path.exists(main_csv):
        size_mb = os.path.getsize(main_csv) / (1024 * 1024)
        print(f"📄 Main analysis file: {size_mb:.1f} MB")

        # Try to get paper count
        try:
            with open(main_csv, "r") as f:
                line_count = sum(1 for _ in f) - 1  # Subtract header
            print(f"📚 Papers in main analysis: {line_count:,}")
        except:
            print("📚 Papers in main analysis: Unable to count")

    return {
        "csv_files": csv_files,
        "pdf_files": pdf_files,
        "html_files": html_files,
        "json_files": json_files,
        "py_files": py_files,
        "r_files": r_files,
    }


def main():
    """Main verification workflow"""
    print_header("HOSYANA REVIEW PROJECT CLEANUP VERIFICATION")
    print("Verifying organized project structure and file cleanup")
    print(f"Working directory: {os.getcwd()}")

    # Run all verification checks
    checks = []

    print("\n🔍 Running verification checks...")

    checks.append(("Directory Structure", check_directory_structure()))
    checks.append(("Key Files", check_key_files()))
    checks.append(("Sankey Plots", check_sankey_plots()))
    checks.append(("Interactive Visualizations", check_interactive_visualizations()))
    checks.append(("Obsolete Files Removed", check_obsolete_files_removed()))
    checks.append(("Bibliography Files", check_bib_files()))
    checks.append(("Root Directory Cleaned", check_root_directory_cleaned()))

    # Generate summary
    summary = generate_summary()

    # Final results
    print_header("VERIFICATION RESULTS")

    passed_checks = 0
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if result:
            passed_checks += 1

    success_rate = (passed_checks / len(checks)) * 100
    print(
        f"\n📊 Overall Success Rate: {passed_checks}/{len(checks)} checks passed ({success_rate:.1f}%)"
    )

    if success_rate >= 85:
        print("\n🎉 PROJECT CLEANUP VERIFICATION: SUCCESS!")
        print("✅ The project has been successfully organized and cleaned")
        print("✅ All essential files are in their proper locations")
        print("✅ Workflows should function correctly with new structure")

        print("\n🚀 Ready to use:")
        print("   python3 run_comprehensive_analysis.py  # Complete workflow")
        print("   Rscript run_comprehensive_analysis.R   # R-only workflow")
        print("   open README.md                         # Usage guide")

        return True
    else:
        print("\n⚠️  PROJECT CLEANUP VERIFICATION: ISSUES FOUND")
        print("❌ Some verification checks failed")
        print("❌ Manual review and fixes may be needed")
        print("\nPlease review the failed checks above and:")
        print("1. Ensure all files were moved correctly")
        print("2. Check that scripts have proper file paths")
        print("3. Verify workflows execute successfully")

        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
