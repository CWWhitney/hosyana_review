# Hosyana Review: Comprehensive Decision Support Methods Analysis

A systematic analysis of decision support methods in literature using automated text mining and visualization techniques.

## 🎯 Project Overview

This project analyzes **12,625+ papers** from comprehensive bibliography collections to identify and categorize decision support methods across **70+ years** of research (1955-2024). It provides automated method detection, statistical analysis, and publication-ready visualizations.

### Key Achievements
- ✅ **Complete Coverage**: Processes ALL .bib files (33 files, 12,625+ papers)
- ✅ **High Detection Rate**: 66.4% method detection across 20 categories
- ✅ **Multi-Format Output**: CSV data, PDF plots, interactive HTML visualizations
- ✅ **Publication Ready**: Clean Sankey plots with consistent formatting

## 📁 Project Structure

```
hosyana_review/
├── 📊 data/
│   ├── analysis_results/          # CSV files with analysis results
│   │   ├── FINAL_methods_analysis.csv           # Main Python analysis (12,625 papers)
│   │   ├── COMPREHENSIVE_methods_classification.csv  # R-compatible format (8,380 papers)
│   │   └── *.csv                  # Additional analysis results
│   └── reports/                   # JSON reports and logs
│       ├── FINAL_analysis_report.json
│       ├── FINAL_sankey_data.json
│       └── *.log
├── 📈 figures/
│   ├── sankey_plots/             # Publication-ready PDF plots
│   │   ├── comprehensive_sankey_1970.pdf
│   │   ├── comprehensive_sankey_1980.pdf
│   │   ├── ...                   # One plot per decade + 2020-2024
│   │   └── comprehensive_sankey_2024.pdf
│   └── interactive/              # Interactive HTML visualizations
│       ├── decade_method_sankey.html
│       ├── method_evolution_sankey.html
│       └── *.html
├── 🔧 scripts/
│   ├── python/                   # Python analysis scripts
│   │   ├── final_comprehensive_analysis.py    # Main analysis engine
│   │   ├── create_sankey_plots.py            # Interactive visualizations
│   │   └── explore_results.py               # Interactive exploration
│   └── r/                        # R visualization scripts
│       ├── create_comprehensive_sankey.R     # PDF Sankey plots
│       └── create_comprehensive_csv.R        # Data format conversion
├── 📚 notebooks/                 # Interactive analysis notebooks
│   ├── interactive_analysis_example.ipynb   # Jupyter notebook
│   └── interactive_analysis_example.Rmd     # R Markdown notebook
├── 📖 docs/                      # Documentation
│   ├── COMPREHENSIVE_ANALYSIS_SUMMARY.md
│   └── *.md                      # Additional documentation
├── 🗂️ bib/                       # Bibliography data
│   └── bib_raw/                  # Raw .bib files (33 files)
├── 🛠️ R/                         # R functions
│   └── plot_sankey.R             # Sankey plotting functions
├── 📄 Core Files
│   ├── index.Rmd                 # Main R Markdown report
│   ├── index.html                # Generated HTML report
│   ├── run_comprehensive_analysis.py  # Main Python workflow
│   └── run_comprehensive_analysis.R   # Main R workflow
└── 🔧 Config Files
    ├── requirements.txt           # Python dependencies
    └── hosyana_review.Rproj      # RStudio project
```

## 🚀 Quick Start

### Prerequisites

**Python Environment:**
```bash
pip install -r requirements.txt
```

**R Environment:**
```r
install.packages(c("dplyr", "ggplot2", "readr", "tidyr", "stringr", "jsonlite", "rmarkdown", "knitr"))
```

### Option 1: Complete Analysis (Recommended)

Run the full workflow including Python analysis and R visualizations:

```bash
python3 run_comprehensive_analysis.py
```

This processes ALL .bib files and generates:
- CSV analysis results in `data/analysis_results/`
- PDF Sankey plots in `figures/sankey_plots/`
- Interactive HTML visualizations in `figures/interactive/`
- Comprehensive HTML report: `index.html`

### Option 2: R-Only Workflow

If you already have Python results, run R analysis only:

```r
Rscript run_comprehensive_analysis.R
```

### Option 3: Manual Step-by-Step

```bash
# Step 1: Python Analysis (processes all 33 .bib files)
python3 scripts/python/final_comprehensive_analysis.py

# Step 2: Interactive Visualizations
python3 scripts/python/create_sankey_plots.py

# Step 3: R-Compatible Data
Rscript scripts/r/create_comprehensive_csv.R

# Step 4: Publication Sankey Plots
Rscript scripts/r/create_comprehensive_sankey.R

# Step 5: HTML Report
Rscript -e "rmarkdown::render('index.Rmd')"
```

## 📊 Key Results Summary

### Papers Analyzed
- **Total Papers**: 12,625 across all .bib files
- **Papers with Methods**: 8,380 (66.4% detection rate)
- **Time Coverage**: 1955-2024 (70 years)
- **Peak Decade**: 2010s with 4,130 papers
- **Recent Trends**: 2,077 papers in 2020-2024

### Top Decision Support Methods
1. **Decision Analysis**: 1,513 papers
2. **Computer Assisted**: 1,131 papers
3. **Evaluation Assessment**: 787 papers
4. **Systems Complexity**: 712 papers
5. **Policy Intervention**: 694 papers
6. **Bayesian Probabilistic**: 522 papers
7. **Uncertainty Analysis**: 498 papers
8. **Technology Innovation**: 400 papers

### Method Evolution Insights
- **1970s-1990s**: Traditional decision analysis and optimization
- **2000s**: Computer-assisted methods and evaluation frameworks
- **2010s+**: Complexity science, Bayesian approaches, multi-criteria analysis
- **2020-2024**: Evaluation assessment dominance (39% of recent research)

## 📈 Output Files Guide

### Analysis Data
- **`FINAL_methods_analysis.csv`**: Complete Python analysis (12,625 papers with binary method indicators)
- **`COMPREHENSIVE_methods_classification.csv`**: R-compatible format (8,380 papers with primary methods)

### Visualizations
- **PDF Sankey Plots**: 7 publication-ready plots (1970s-2024, including 2020-2024 focus)
- **Interactive HTML**: 4 dynamic visualizations for exploration

### Reports
- **`index.html`**: Complete integrated analysis report
- **JSON Reports**: Statistical summaries and data for further analysis
- **Markdown Docs**: Comprehensive analysis documentation

## 🔧 Interactive Analysis

### Jupyter Notebook (Python)
```bash
jupyter lab notebooks/interactive_analysis_example.ipynb
```
- Line-by-line execution (like RStudio)
- Immediate output display
- Rich visualizations

### R Markdown (RStudio)
Open `notebooks/interactive_analysis_example.Rmd` in RStudio
- Familiar RStudio workflow
- `Ctrl+Enter` line execution
- Integrated environment

## 📚 Method Categories

The analysis detects 20 comprehensive method categories:

**Core Decision Methods:**
- Decision Analysis, Multi-Criteria Decision Analysis, Game Theory

**Quantitative Approaches:**
- Bayesian/Probabilistic, Optimization, Economic Evaluation

**Technology & Innovation:**
- Computer Assisted, Technology Innovation, Systems Complexity

**Assessment & Evaluation:**
- Evaluation Assessment, Quality Performance, Risk Safety

**Human-Centered Methods:**
- Stakeholder Expert, Behavioral Psychology, Uncertainty Analysis

**And more...** (see full list in analysis results)

## 🔍 Data Sources

- **33 .bib files** in `bib/bib_raw/` directory
- Comprehensive coverage of decision support literature
- Multiple publication types: journal articles, books, reports, conference papers
- Automated duplicate detection and quality filtering

## 🤝 Contributing

1. **Add new .bib files** to `bib/bib_raw/` directory
2. **Run analysis** with `python3 run_comprehensive_analysis.py`
3. **Review results** in organized output directories
4. **Update documentation** as needed

## 📄 Citation

When using this analysis or methodology, please cite:

```bibtex
@misc{hosyana_review_2024,
  title={Comprehensive Decision Support Methods Analysis: Automated Literature Review of 12,625+ Papers},
  author={Whitney, Cory and Contributors},
  year={2024},
  note={Systematic analysis covering 1955-2024}
}
```

## 📞 Support

- **Documentation**: See `docs/` directory for detailed guides
- **Interactive Help**: Use notebooks for step-by-step exploration
- **Method Details**: Review `scripts/` for implementation specifics

---

**Last Updated**: December 2024  
**Version**: 2.0 (Organized Structure)  
**Coverage**: 12,625 papers across 70 years  
**Status**: ✅ Complete Analysis Available