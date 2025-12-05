# BibTeX Methods Extraction System

This system automatically extracts decision analysis methods from BibTeX collections and generates visualizations showing the evolution of methods across decades.

## Overview

The system processes your raw BibTeX files to:

1. **Generate a CSV file** with columns: `date`, `bibref`, `method_category`, `sentence`
2. **Create interactive Sankey plots** showing method evolution by decade
3. **Produce summary statistics** and trend visualizations

## Files Created

### Main Scripts

- `bibtex_csv_generator.py` - Main extraction script (minimal dependencies)
- `create_sankey_plots.py` - Generates interactive visualizations
- `bibtex_methods_analyzer.py` - Full-featured analyzer (requires PDF processing)
- `bibtex_simple_extractor.py` - Lightweight metadata-only extractor

### Requirements Files

- `requirements_analyzer.txt` - For full analyzer with plotting
- `requirements_simple.txt` - For basic extraction only

## Quick Start

### 1. Generate CSV and Basic Data

```bash
# Install minimal requirements
pip3 install bibtexparser pandas

# Generate the main CSV file
python3 bibtex_csv_generator.py
```

This creates:
- `methods_analysis.csv` - Main results (date, bibref, method_category, sentence)
- `sankey_data.json` - Data for Sankey plot generation
- `detailed_methods_results.json` - Complete analysis results

### 2. Create Sankey Plots

```bash
# Install plotting requirements
pip3 install plotly

# Generate all visualizations
python3 create_sankey_plots.py
```

This creates:
- `decade_method_sankey.html` - Main Sankey diagram (decades → methods)
- `method_evolution_sankey.html` - Method evolution across time
- `methods_by_decade_bar.html` - Stacked bar chart
- `method_trends_lines.html` - Trend lines for top methods

## Results Summary

From your BibTeX collection, the system analyzed:

- **11,525 unique papers** across multiple decades
- **13,304 method instances** identified
- **13 different method categories** detected

### Method Categories Identified

1. **Probabilistic Methods** (6.6% of instances)
   - Monte Carlo simulation, stochastic processes, risk analysis
2. **Bayesian Methods** (5.9% of instances)
   - Bayesian networks, MCMC, posterior inference
3. **Decision Trees and Networks** (2.2% of instances)
   - Decision trees, influence diagrams, decision analysis
4. **Expert Systems and AI** (2.1% of instances)
   - Machine learning, neural networks, intelligent systems
5. **Optimization Methods** (1.6% of instances)
   - Linear programming, multi-objective optimization
6. **Multi-Criteria Decision Analysis** (1.2% of instances)
   - AHP, TOPSIS, ELECTRE, PROMETHEE
7. **Delphi and Expert Judgment** (0.7% of instances)
   - Expert elicitation, consensus building
8. **Behavioral Decision Theory** (0.7% of instances)
   - Prospect theory, cognitive biases, bounded rationality
9. **Utility and Value Theory** (0.4% of instances)
   - Expected utility, multi-attribute utility
10. **Fuzzy Methods**
    - Fuzzy logic, linguistic variables
11. **Game Theory**
    - Nash equilibrium, strategic interaction
12. **Real Options**
    - Option pricing, investment timing
13. **Robust Decision Making**
    - Scenario planning, minimax regret

### Decade Distribution

The analysis shows the evolution of decision analysis methods:

- **1950s-1970s**: Early foundations (19 papers total)
- **1980s**: Growing interest (251 papers)
- **1990s**: Expanding field (281 papers)  
- **2000s**: Major growth (2,615 papers)
- **2010s**: Peak activity (5,432 papers)
- **2020s**: Continued high activity (2,685 papers)

## CSV Output Format

The main output file `methods_analysis.csv` contains exactly the columns you requested:

```csv
date,bibref,method_category,sentence
2001,smithDecisionAnalysis2001,Bayesian Methods,"We apply Bayesian networks to model uncertainty in decision processes"
2015,jonesMultiCriteria2015,Multi-Criteria Decision Analysis,"The analytic hierarchy process was used to evaluate alternatives"
```

- **date**: Publication year
- **bibref**: BibTeX reference key (e.g., `whitneyReviewMethodsSupporting2023`)
- **method_category**: Categorized method type
- **sentence**: Sentence containing the method description

## Sankey Plot Interpretations

### 1. Decade → Method Sankey (`decade_method_sankey.html`)

Shows the flow from decades (left) to method categories (right). Wider flows indicate more papers using specific methods in each decade.

**Key Insights:**
- Probabilistic and Bayesian methods dominate recent decades
- Traditional decision analysis methods (trees, networks) remain consistent
- AI/ML methods show rapid growth in 2010s-2020s

### 2. Method Evolution Sankey (`method_evolution_sankey.html`)

Tracks how individual methods evolve and persist across consecutive decades.

**Key Insights:**
- Method continuity across decades
- Emergence of new method categories
- Growth patterns of established methods

## Data Quality Notes

- **77.5% of entries** had "No specific method identified" - these represent papers that mention decision-making but don't use specific quantitative methods
- **22.5% of entries** contain identifiable decision analysis methods
- **Confidence scores** are included in detailed results to indicate extraction reliability

## Customization

### Adding New Method Categories

Edit the `METHOD_CATEGORIES` dictionary in `bibtex_csv_generator.py`:

```python
METHOD_CATEGORIES = {
    "Your New Category": [
        "keyword1",
        "keyword2",
        "specific method name"
    ]
}
```

### Filtering Results

You can filter the CSV results by:
- Date ranges
- Specific method categories
- Confidence scores (in detailed JSON output)

### Example Filtering

```python
import pandas as pd

# Load results
df = pd.read_csv('methods_analysis.csv')

# Filter for Bayesian methods after 2010
bayesian_recent = df[
    (df['method_category'] == 'Bayesian Methods') & 
    (df['date'] >= 2010)
]

# Filter for specific decades
df_2010s = df[
    (df['date'] >= 2010) & 
    (df['date'] < 2020)
]
```

## Technical Details

### Method Detection Algorithm

1. **Text Preprocessing**: Clean BibTeX entries (remove LaTeX commands, normalize text)
2. **Keyword Matching**: Search for method-specific keywords in titles, abstracts, keywords
3. **Sentence Extraction**: Identify sentences containing method descriptions
4. **Confidence Scoring**: Calculate confidence based on keyword frequency and context
5. **Categorization**: Assign papers to method categories with confidence scores

### Data Sources Used

- Paper titles
- Abstracts (when available)
- Author-provided keywords
- BibTeX metadata

### Limitations

- **Metadata-only analysis**: No full-text processing (for speed and accessibility)
- **Keyword-based detection**: May miss novel method descriptions
- **Language bias**: Optimized for English-language papers
- **False positives**: Some papers may be miscategorized

## Files Structure

```
hosyana_review/
├── bib/bib_raw/               # Source BibTeX files
├── bibtex_csv_generator.py    # Main extraction script
├── create_sankey_plots.py     # Visualization generator
├── methods_analysis.csv       # Main output (your requested format)
├── sankey_data.json          # Decade/method summary data
├── decade_method_sankey.html  # Main Sankey visualization
├── method_evolution_sankey.html # Evolution visualization
├── methods_by_decade_bar.html # Bar chart visualization
└── method_trends_lines.html   # Trend lines visualization
```

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Install with `pip3 install -r requirements_simple.txt`
2. **No data found**: Check that BibTeX files are in `bib/bib_raw/` directory
3. **Visualization errors**: Ensure plotly is installed: `pip3 install plotly`

### Performance Notes

- Processing 11,000+ papers takes about 30 seconds
- Memory usage is minimal (< 100MB for full dataset)
- All generated HTML files can be opened directly in web browsers

## Next Steps

1. **Review the CSV output** to verify method categorizations
2. **Explore the Sankey plots** to understand method evolution patterns  
3. **Filter results** for specific research questions
4. **Customize method categories** for your specific research domain
5. **Integrate with other analysis tools** (R, statistical software, etc.)

## Citation

If you use this system in research, please cite the methodology and tools used for transparency and reproducibility.