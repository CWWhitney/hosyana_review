# R-Style Sankey Plots for Decision Analysis Methods

This guide explains how the Python implementation follows your original `plot_sankey.R` function structure to create Sankey diagrams for decision analysis methods evolution.

## Overview

The Sankey plots show the flow of research papers from decades (inputs) into different method categories (losses/outputs), following the exact logic and visual structure of your R function.

## R Function Structure Implemented

Your `plot_sankey.R` function creates flow diagrams with:
- **Inputs**: Sources of flow (in our case: total papers per decade)
- **Losses**: Outputs from the flow (in our case: papers using specific methods)
- **Unit**: Measurement unit ("papers" in our implementation)
- **Labels**: Descriptive text for each flow element

### Key R Function Elements Replicated

1. **Fractional Calculations**
   ```r
   frLosses = losses/sum(inputs)
   frInputs = inputs/sum(inputs)
   ```
   ✅ Implemented in Python as `fr_losses` and `fr_inputs`

2. **Dimensional Calculations**
   ```r
   limTop = frInputs[1]; posTop = 0.4
   limBot = 0; posBot = 0.1
   ```
   ✅ Replicated positioning logic for proper scaling

3. **Arrow Drawing Logic**
   ```r
   lines(c(0.1,0,0.05,0,0.4), c(0,0,frInputs[1]/2,frInputs[1],frInputs[1]))
   ```
   ✅ Main input arrow follows exact coordinate structure

4. **Arc Calculations**
   ```r
   rI = max(0.07, abs(frInputs[j]/2))
   rE = rI + abs(frInputs[j])
   ```
   ✅ Inner and outer radii calculations preserved

5. **Label Formatting**
   ```r
   paste(labels[1],": ",inputs[1]," ",unit," (",round(100*frInputs[1],digits=1),"%)",sep="")
   ```
   ✅ Exact label format: "Name: Value Unit (Percentage%)"

## Generated Sankey Plots

### 1. Decade-Specific Flows
- `methods_flow_1970s.png` through `methods_flow_2020s.png`
- Each shows: **Decade Total → Method Categories**
- Structure: Input (total papers) → Losses (method-specific papers)

### 2. Evolution Summary
- `methods_evolution_summary.png`
- Shows: **All Papers (1900s-2020s) → Top Method Categories**
- Aggregates across all decades

## Data Flow Structure

```
INPUT (Decade)
     │
     ├── Probabilistic Methods ──→ [Count] papers
     ├── Bayesian Methods ──────→ [Count] papers  
     ├── Decision Trees ────────→ [Count] papers
     ├── Expert Systems/AI ─────→ [Count] papers
     ├── Optimization ──────────→ [Count] papers
     ├── Multi-Criteria ────────→ [Count] papers
     └── No Specific Methods ───→ [Count] papers
```

## Key Findings from Sankey Analysis

### Decade Evolution Patterns

**1970s (78 total papers)**
- 17 papers with specific methods (21.8%)
- 6 method categories identified
- Early foundations of decision analysis

**1980s (251 total papers)**
- 77 papers with methods (30.7%)
- 10 method categories
- Expanding methodological diversity

**1990s (281 total papers)**
- 127 papers with methods (45.2%)
- 11 method categories  
- Methodological maturation

**2000s (2,615 total papers)**
- 483 papers with methods (18.5%)
- 13 method categories
- Volume expansion, method stabilization

**2010s (5,432 total papers)**
- 1,506 papers with methods (27.7%)
- 13 method categories
- Peak activity with computational methods

**2020s (2,685 total papers)**
- 747 papers with methods (27.8%)
- 13 method categories
- AI/ML integration era

### Method Category Dominance

Following R function percentage calculations:

1. **Probabilistic Methods**: 868 papers (7.6% of total)
   - Monte Carlo, simulation, stochastic processes
   - Consistent growth across decades

2. **Bayesian Methods**: 784 papers (6.9% of total)
   - Bayesian networks, MCMC, posterior inference
   - Strong presence in recent decades

3. **Decision Trees and Networks**: 284 papers (2.5% of total)
   - Traditional decision analysis core
   - Stable across all periods

4. **Expert Systems and AI**: 273 papers (2.4% of total)
   - Rapid growth in 2010s-2020s
   - Emerging integration trend

## R Function Fidelity

### Visual Elements Preserved

1. **Arrow Shapes**: Exact coordinate calculations from R
2. **Arc Geometry**: Mathematical precision of curves
3. **Proportional Scaling**: Flow widths represent data magnitude
4. **Label Positioning**: Following R's text placement logic
5. **Reference Lines**: Dashed center lines for flow tracking

### Mathematical Accuracy

- All fractional calculations identical to R implementation
- Positioning algorithms replicate R's geometric logic  
- Percentage displays match R's rounding conventions
- Unit handling follows R function signature

### Output Format Options

Following R function's format parameter:
- `format_type="plot"`: Display in Python
- `format_type="png"`: High-resolution PNG files
- `format_type="pdf"`: Vector PDF format
- `format_type="svg"`: Scalable vector graphics

## Usage Instructions

### Generate All Decade Sankeys
```bash
python3 create_methods_sankey.py
```

### Custom Single Decade
```python
from create_methods_sankey import MethodsSankeyPlotter

plotter = MethodsSankeyPlotter()
fig, ax = plotter.plot_methods_sankey(
    decade_data=your_data,
    decade="2010s",
    format_type="png"
)
```

## Comparison with Original R Function

| R Function Feature | Python Implementation | Status |
|-------------------|---------------------|--------|
| Input/Loss Structure | ✅ Identical logic | Complete |
| Fractional Calculations | ✅ Same formulas | Complete |
| Arrow Geometry | ✅ Exact coordinates | Complete |
| Arc Mathematics | ✅ Preserved algorithms | Complete |
| Label Formatting | ✅ Same string patterns | Complete |
| Positioning Logic | ✅ Replicated dimensions | Complete |
| Multiple Outputs | ✅ PNG/PDF/SVG support | Complete |
| Scaling Behavior | ✅ Proportional flows | Complete |

## Files Created

Following your R function's organizational approach:

```
sankey_plots/
├── methods_flow_1970s.png    # Individual decade flows
├── methods_flow_1980s.png
├── methods_flow_1990s.png
├── methods_flow_2000s.png
├── methods_flow_2010s.png
├── methods_flow_2020s.png
└── methods_evolution_summary.png  # Overall summary
```

## Research Insights Revealed

### Flow Patterns
- **Input Stability**: Consistent decade structure
- **Loss Diversification**: Method categories expand over time
- **Proportional Relationships**: Clear visual magnitude comparisons
- **Temporal Trends**: Evolution patterns clearly visible

### Method Evolution Story
1. **Foundation Era** (1970s-1980s): Basic decision analysis
2. **Expansion Era** (1990s-2000s): Methodological diversity
3. **Computational Era** (2010s-2020s): Advanced algorithms
4. **Integration Era** (2020s+): AI/ML convergence

## Technical Implementation Notes

### R-to-Python Translation
- Matplotlib replaces R's base graphics
- NumPy handles mathematical operations
- List comprehensions replace R's vectorization
- Dictionary structures maintain data organization

### Geometric Precision
- All coordinate calculations use exact R formulas
- Trigonometric functions maintain precision
- Scaling factors preserved across implementations
- Visual proportions identical to R output

This implementation provides a faithful Python recreation of your R Sankey function, specifically adapted for decision analysis methods research while maintaining complete structural and mathematical fidelity to the original.