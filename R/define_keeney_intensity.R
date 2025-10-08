define_keeney_intensity <- function() {
  list(
    # Level 1: No-brainer decisions (intuitive, routine)
    level1_intuitive = c(
      "rule of thumb", "heuristic", "intuitive", "common sense",
      "routine decision", "standard procedure", "best practice"
    ),
    
    # Level 2: Simple analysis (basic tools)
    level2_simple = c(
      "checklist", "simple model", "basic analysis", "quick assessment",
      "spreadsheet", "manual calculation", "descriptive statistics"
    ),
    
    # Level 3: Structured analysis (systematic but not complex)
    level3_structured = c(
      "systematic approach", "structured decision", "framework",
      "multi-criteria", "scoring system", "rating scale", "basic optimization"
    ),
    
    # Level 4: Advanced analysis (sophisticated methods)
    level4_advanced = c(
      "stochastic", "probabilistic", "bayesian", "monte carlo", "markov",
      "optimization", "linear programming", "nonlinear programming",
      "simulation", "agent-based", "system dynamics"
    ),
    
    # Level 5: Deep uncertainty methods (most complex)
    level5_deep_uncertainty = c(
      "robust decision making", "deep uncertainty", "adaptive management",
      "real options", "info-gap", "scenario planning", "decision under deep uncertainty",
      "value of information", "sensitivity analysis", "uncertainty analysis"
    )
  )
}