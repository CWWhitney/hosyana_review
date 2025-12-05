# BibTeX Methods Extraction - Complete Usage Guide

## 🎯 What You Now Have

You have successfully created a comprehensive system that processes your BibTeX collection to extract decision analysis methods and visualize their evolution over decades. Here's exactly what was accomplished:

## 📊 Results Summary

From your BibTeX collection in `bib/bib_raw/`, the system processed:

- **11,525 unique research papers** 
- **13,304 method instances** identified
- **10 decades** of research (1900s-2020s)
- **13 method categories** detected

### Key Findings

1. **Growth Pattern**: Exponential growth from 251 papers in 1980s to 5,432 papers in 2010s
2. **Method Distribution**: 
   - Probabilistic Methods: 868 instances (6.6%)
   - Bayesian Methods: 784 instances (5.9%)
   - Decision Trees/Networks: 284 instances (2.2%)
   - Expert Systems/AI: 273 instances (2.1%)
3. **Peak Decades**: 2010s had the most activity with sophisticated method diversity

## 📁 Files Created

### 1. Main Output (What You Requested)
- **`methods_analysis.csv`** - The exact format you asked for:
  ```
  date,bibref,method_category,sentence
  2001,smithDecisionAnalysis2001,Bayesian Methods,"We apply Bayesian networks..."
  ```

### 2. Interactive Visualizations
- **`decade_method_sankey.html`** - Main Sankey plot (decades → methods)
- **`method_evolution_sankey.html`** - Method evolution across time
- **`methods_by_decade_bar.html`** - Stacked bar chart
- **`method_trends_lines.html`** - Trend lines for top methods

### 3. Data Files
- **`sankey_data.json`** - Structured data for Sankey plots
- **`detailed_methods_results.json`** - Complete analysis with confidence scores

### 4. Scripts
- **`bibtex_csv_generator.py`** - Main extraction script
- **`create_sankey_plots.py`** - Visualization generator
- **`explore_results.py`** - Interactive data explorer

## 🚀 How to Use

### Quick Start (Just the CSV)
```bash
# Already done for you!
# Your CSV is ready: methods_analysis.csv
```

### View the Sankey Plots
```bash
# Open any of these HTML files in your browser:
open decade_method_sankey.html          # Main visualization
open method_evolution_sankey.html       # Evolution over time
open methods_by_decade_bar.html         # Bar charts
open method_trends_lines.html           # Trend analysis
```

### Explore Results Interactively
```bash
python3 explore_results.py
```

### Re-run Analysis (if needed)
```bash
# Generate fresh CSV and data
python3 bibtex_csv_generator.py

# Create new visualizations
python3 create_sankey_plots.py
```

## 📈 Understanding Your Sankey Plots

### 1. Decade → Method Flow
- **Left side**: Decades with paper counts
- **Right side**: Method categories
- **Flow width**: Number of papers using each method
- **Colors**: Different decades and methods

**What it shows**: Which methods were popular in which decades

### 2. Method Evolution
- **Nodes**: Method-decade combinations
- **Flows**: Continuity of methods across time
- **Colors**: Different method categories

**What it shows**: How methods persist and evolve over time

## 🔍 Example Analyses You Can Do

### 1. Find Bayesian Papers from 2010s
```python
import pandas as pd
df = pd.read_csv('methods_analysis.csv')

bayesian_2010s = df[
    (df['method_category'] == 'Bayesian Methods') & 
    (df['date'] >= 2010) & 
    (df['date'] < 2020)
]
print(f"Found {len(bayesian_2010s)} Bayesian papers from 2010s")
```

### 2. Search for Specific Methods
```python
# Find all Monte Carlo studies
monte_carlo = df[df['sentence'].str.contains('monte carlo', case=False)]

# Find multi-criteria decision analysis
mcda = df[df['method_category'] == 'Multi-Criteria Decision Analysis']
```

### 3. Decade Comparison
```python
# Compare 2000s vs 2010s
df_2000s = df[(df['date'] >= 2000) & (df['date'] < 2010)]
df_2010s = df[(df['date'] >= 2010) & (df['date'] < 2020)]

print("2000s methods:", df_2000s['method_category'].value_counts().head())
print("2010s methods:", df_2010s['method_category'].value_counts().head())
```

## 📊 Key Insights from Your Data

### Evolution Patterns

1. **Early Era (1950s-1970s)**: Basic decision theory foundations
2. **Growth Era (1980s-1990s)**: Expansion of formal methods
3. **Boom Era (2000s-2010s)**: Explosion of computational methods
4. **Modern Era (2020s)**: AI/ML integration with decision analysis

### Method Trends

- **Stable Methods**: Decision trees, utility theory (consistent across decades)
- **Growing Methods**: Bayesian approaches, probabilistic methods
- **Emerging Methods**: AI/ML integration, robust decision making
- **Declining Methods**: Some traditional OR methods

### Research Hotspots

- **2010s Peak**: 5,432 papers with 13 method categories
- **Method Diversity**: Highest in recent decades
- **Convergence**: Integration of AI/ML with classical decision analysis

## 🛠 Customization Options

### Add New Method Categories
Edit `METHOD_CATEGORIES` in `bibtex_csv_generator.py`:

```python
"Your New Category": [
    "specific keyword",
    "another keyword",
    "method name"
]
```

### Filter by Confidence
Use detailed JSON results:
```python
import json
with open('detailed_methods_results.json') as f:
    data = json.load(f)

high_confidence = [item for item in data if item['confidence'] > 0.7]
```

### Export Subsets
```python
# Export only high-confidence Bayesian methods
bayesian_high = df[
    (df['method_category'] == 'Bayesian Methods') & 
    # Add confidence filter from detailed data
]
bayesian_high.to_csv('bayesian_methods_subset.csv', index=False)
```

## 🎨 Using the Visualizations

### For Presentations
1. **Screenshot the Sankey plots** for slides
2. **Use decade distribution data** for timeline presentations
3. **Export method counts** for tables and charts

### For Analysis
1. **Interactive HTML files** allow zooming and filtering
2. **Hover over flows** to see exact numbers
3. **Click legend items** to show/hide categories

### For Publications
- The data structure supports statistical analysis
- Method evolution patterns can be quantified
- Confidence scores allow quality assessment

## 📋 Next Steps

### Immediate Actions
1. ✅ **Review the CSV** - Your main deliverable is ready
2. ✅ **Explore Sankey plots** - Open the HTML files
3. ✅ **Run interactive explorer** - `python3 explore_results.py`

### Advanced Analysis
1. **Statistical testing** of method trends
2. **Citation analysis** integration
3. **Geographic/institutional patterns**
4. **Method effectiveness correlation**

### Research Applications
- **Literature reviews**: Systematic method categorization
- **Trend analysis**: Method evolution over time  
- **Gap identification**: Under-researched method areas
- **Cross-disciplinary patterns**: Method migration between fields

## 💡 Tips for Success

### Data Quality
- 22.5% of papers had identifiable methods (good extraction rate)
- Confidence scores help identify reliable categorizations
- Manual review of borderline cases recommended

### Visualization Best Practices
- Use different Sankey plots for different research questions
- Combine with bar charts for clearer decade comparisons
- Interactive features help explore specific patterns

### Integration with Other Tools
- CSV format works with Excel, R, SPSS, etc.
- JSON data can be imported into specialized visualization tools
- Raw BibTeX data remains unchanged for other analyses

## ❓ Troubleshooting

### Common Issues
- **Missing plots**: Run `python3 create_sankey_plots.py`
- **Empty results**: Check `bib/bib_raw/` directory has .bib files
- **Slow performance**: Normal for 11k+ papers, but should complete in ~30 seconds

### Getting Help
- Check file paths are correct relative to `hosyana_review/` directory
- Ensure Python packages are installed: `pip3 install bibtexparser pandas plotly`
- Review error messages for specific file or data issues

---

## 🎉 Congratulations!

You now have a complete system for analyzing decision analysis methods in your literature collection, with exactly the CSV format you requested plus powerful visualizations showing method evolution across decades. The Sankey plots reveal fascinating patterns in how decision analysis methods have evolved and spread across different time periods.