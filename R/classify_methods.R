#!/usr/bin/env Rscript
# Decision Support Methods Classifier
#
# Classifies every paper in bib/bib_raw/*.bib into 20 decision-support-method
# categories via keyword matching. This is a pure-R replacement for an earlier
# Python-based classifier; the whole pipeline now runs in R.
#
# Usage:
#   Rscript R/classify_methods.R
#   # or: source("R/classify_methods.R"); classify_methods()
#
# Outputs:
#   data/analysis_results/FINAL_methods_analysis.csv
#   data/reports/FINAL_sankey_data.json
#   data/reports/FINAL_analysis_report.json

suppressPackageStartupMessages({
  library(dplyr)
  library(stringr)
  library(purrr)
  library(readr)
  library(tibble)
  library(jsonlite)
})

# ------------------------------------------------------------------
# Method categories (keyword lists)
# ------------------------------------------------------------------
METHOD_CATEGORIES <- list(
  DECISION_ANALYSIS = c(
    "decision analysis", "decision tree", "decision support", "decision making",
    "decision model", "decision framework", "decision process", "decision theory",
    "influence diagram", "decision network", "rollback analysis", "backward induction",
    "value of information", "information accuracy", "perfect information", "expected value",
    "decision criterion", "decision rule", "choice model", "alternative evaluation",
    "option assessment", "choice analysis", "prescriptive analytics", "normative decision",
    "rational choice", "decision support system", "DSS", "decision aid"
  ),
  POLICY_INTERVENTION = c(
    "policy analysis", "policy evaluation", "policy assessment", "policy model",
    "intervention analysis", "intervention evaluation", "intervention assessment",
    "policy support", "policy decision", "policy making", "policy framework",
    "policy tool", "policy instrument", "regulatory analysis", "governance",
    "public policy", "social policy", "economic policy", "environmental policy",
    "health policy", "intervention design", "program evaluation", "impact assessment",
    "cost-effectiveness", "cost-benefit", "policy option", "policy alternative",
    "policy scenario", "intervention strategy", "policy intervention",
    "implementation analysis", "regulatory impact", "evidence-based policy"
  ),
  UNCERTAINTY_ANALYSIS = c(
    "uncertainty analysis", "uncertainty assessment", "uncertainty quantification",
    "uncertainty propagation", "uncertainty modeling", "parameter uncertainty",
    "model uncertainty", "structural uncertainty", "epistemic uncertainty",
    "aleatory uncertainty", "deep uncertainty", "severe uncertainty", "risk analysis",
    "risk assessment", "risk evaluation", "risk management", "probabilistic risk",
    "quantitative risk", "variability analysis", "sensitivity analysis",
    "scenario analysis", "what-if analysis", "robustness analysis", "confidence interval",
    "prediction interval", "error propagation", "measurement uncertainty",
    "forecast uncertainty"
  ),
  STAKEHOLDER_EXPERT = c(
    "stakeholder analysis", "stakeholder engagement", "stakeholder involvement",
    "stakeholder participation", "stakeholder consultation", "expert judgment",
    "expert elicitation", "expert assessment", "expert opinion", "expert knowledge",
    "expert consultation", "expert panel", "expert system", "participatory",
    "participatory modeling", "collaborative decision", "group decision",
    "consensus building", "multi-stakeholder", "delphi method", "nominal group",
    "focus group", "structured interview", "knowledge elicitation",
    "preference elicitation", "participatory research", "co-design"
  ),
  MODELING_SIMULATION = c(
    "mathematical model", "conceptual model", "analytical model", "empirical model",
    "statistical model", "econometric model", "simulation model", "computer model",
    "computational model", "numerical model", "predictive model", "forecasting model",
    "monte carlo", "monte carlo simulation", "stochastic simulation",
    "discrete event simulation", "agent-based model", "system dynamics",
    "microsimulation", "dynamic model", "optimization model", "network model",
    "spatial model", "integrated model", "ensemble model", "meta-model",
    "surrogate model", "model validation", "model calibration"
  ),
  BAYESIAN_PROBABILISTIC = c(
    "bayesian", "bayes", "posterior", "prior", "likelihood", "bayesian inference",
    "bayesian analysis", "bayesian statistics", "bayesian network", "belief network",
    "bayesian updating", "markov chain monte carlo", "mcmc", "gibbs sampling",
    "metropolis", "hamiltonian monte carlo", "variational bayes", "empirical bayes",
    "probabilistic", "probability", "stochastic", "probability distribution",
    "probability model", "stochastic process", "random variable",
    "likelihood function", "maximum likelihood", "bootstrap", "statistical inference",
    "hypothesis testing"
  ),
  COMPUTER_ASSISTED = c(
    "computer assisted", "computer-assisted", "computer aided", "computerized",
    "digital", "automated", "software", "algorithm", "computational",
    "machine learning", "artificial intelligence", "deep learning", "neural network",
    "data mining", "big data", "analytics", "predictive analytics", "data science",
    "decision support system", "expert system", "knowledge-based system",
    "information system", "web-based", "online", "cloud-based", "dashboard",
    "visualization", "interactive", "software tool", "digital platform"
  ),
  VALUE_INFORMATION = c(
    "value of information", "value of perfect information", "value of imperfect information",
    "expected value of information", "evpi", "evii", "information value",
    "information accuracy", "information quality", "data quality", "measurement accuracy",
    "precision", "reliability", "validity", "information content", "information theory",
    "information gain", "entropy", "mutual information", "signal-to-noise",
    "measurement error", "prediction accuracy", "forecast accuracy",
    "diagnostic accuracy", "sensitivity", "specificity", "area under curve"
  ),
  MULTI_CRITERIA = c(
    "multi-criteria", "multicriteria", "multiple criteria", "mcda", "mcdm",
    "analytic hierarchy process", "ahp", "analytic network process", "anp",
    "topsis", "electre", "promethee", "vikor", "outranking", "concordance",
    "preference ranking", "multi-attribute", "multi-objective", "goal programming",
    "compromise programming", "utility function", "value function", "scoring method"
  ),
  OPTIMIZATION = c(
    "optimization", "optimisation", "minimize", "maximize", "optimal", "optimum",
    "linear programming", "nonlinear programming", "integer programming",
    "dynamic programming", "stochastic programming", "robust optimization",
    "multi-objective optimization", "pareto optimal", "evolutionary algorithm",
    "genetic algorithm", "particle swarm", "simulated annealing", "gradient descent"
  ),
  ECONOMIC_EVALUATION = c(
    "cost-effectiveness", "cost-benefit", "cost-utility", "economic evaluation",
    "health economics", "budget impact", "return on investment", "net present value",
    "cost per qaly", "quality adjusted life years", "incremental cost-effectiveness",
    "willingness to pay", "contingent valuation", "discrete choice experiment",
    "conjoint analysis", "benefit transfer", "meta-analysis"
  ),
  GAME_THEORY = c(
    "game theory", "strategic", "nash equilibrium", "dominant strategy",
    "prisoner dilemma", "bargaining", "negotiation", "auction theory",
    "mechanism design", "cooperative game", "behavioral game theory",
    "evolutionary game theory", "strategic interaction"
  ),
  BEHAVIORAL_PSYCHOLOGY = c(
    "behavioral", "behaviour", "psychology", "cognitive", "heuristic", "bias",
    "prospect theory", "bounded rationality", "anchoring", "availability heuristic",
    "framing effect", "loss aversion", "overconfidence", "cognitive bias",
    "decision psychology", "human factors", "behavioral economics"
  ),
  SYSTEMS_COMPLEXITY = c(
    "systems analysis", "systems thinking", "complex system", "socio-technical system",
    "socio-ecological system", "feedback", "emergence", "complexity science",
    "network analysis", "resilience", "adaptability", "sustainability",
    "adaptive management", "ecosystem", "supply chain"
  ),
  TECHNOLOGY_INNOVATION = c(
    "technology assessment", "health technology assessment", "hta", "innovation",
    "diffusion", "adoption", "implementation", "scaling up", "technology transfer",
    "knowledge transfer", "translational research", "research and development",
    "innovation system", "disruptive innovation", "technology roadmap"
  ),
  ENVIRONMENTAL_SUSTAINABILITY = c(
    "environmental assessment", "environmental impact", "life cycle assessment",
    "carbon footprint", "environmental management", "sustainability",
    "sustainable development", "circular economy", "climate change",
    "ecosystem services", "conservation", "natural resource management"
  ),
  QUALITY_PERFORMANCE = c(
    "quality improvement", "performance measurement", "performance indicator",
    "key performance indicator", "kpi", "balanced scorecard", "benchmarking",
    "best practice", "process improvement", "continuous improvement",
    "quality assurance", "outcome measurement", "impact evaluation"
  ),
  RISK_SAFETY = c(
    "risk management", "risk assessment", "hazard analysis", "safety analysis",
    "fault tree analysis", "reliability analysis", "probabilistic risk assessment",
    "safety management", "security", "disaster management", "crisis management"
  ),
  FORECASTING_PREDICTION = c(
    "forecasting", "prediction", "predictive", "forecast", "projection", "scenario",
    "time series", "trend analysis", "regression", "neural network forecasting",
    "ensemble forecasting", "judgmental forecasting", "forecast accuracy"
  ),
  EVALUATION_ASSESSMENT = c(
    "evaluation", "assessment", "appraisal", "review", "audit", "monitoring",
    "performance measurement", "impact evaluation", "program evaluation",
    "comparative analysis", "benchmarking", "effectiveness", "efficacy"
  )
)

# Used for the UNCERTAINTY_STATEMENTS metric (distinct from category keywords)
UNCERTAINTY_PATTERNS <- c(
  "uncertain(ty)?", "risk\\b", "variability", "confidence interval",
  "monte carlo", "simulation", "probability", "stochastic",
  "sensitivity", "robust", "scenario", "what.?if"
)

# ------------------------------------------------------------------
# Lightweight .bib parser (same approach as R/prisma_pipeline.R —
# bibtex::read.bib() and bib2df() silently drop malformed entries)
# ------------------------------------------------------------------
parse_bib_entry <- function(txt, keep_fields) {
  head <- str_match(txt, "^@(\\w+)\\s*\\{\\s*([^,\\s]+)\\s*,")
  starts <- str_locate_all(txt, "(?m)^\\s*([A-Za-z-]+)\\s*=\\s*")[[1]]
  out <- setNames(rep(NA_character_, length(keep_fields)), keep_fields)
  if (nrow(starts) > 0) {
    names_ <- str_match(str_sub(txt, starts[, 1], starts[, 2]), "([A-Za-z-]+)\\s*=")[, 2] |> tolower()
    ends <- c(starts[-1, 1] - 1, nchar(txt))
    vals <- str_sub(txt, starts[, 2] + 1, ends) |> str_trim()
    vals[length(vals)] <- str_remove(vals[length(vals)], "\\}\\s*$")
    vals <- vals |> str_remove(",\\s*$") |> str_remove_all("[{}\"]") |> str_squish()
    hit <- names_ %in% keep_fields
    out[names_[hit]] <- vals[hit]
  }
  tibble(key = head[1, 3], !!!as.list(out))
}

read_bib_file <- function(path, keep_fields) {
  raw <- read_file(path)
  blocks <- str_split(raw, "\n(?=@\\w+\\s*\\{)")[[1]]
  blocks <- blocks[str_detect(blocks, "^@\\w+\\s*\\{")]
  blocks <- blocks[!str_detect(blocks, regex("^@(comment|string|preamble)", ignore_case = TRUE))]
  map_dfr(blocks, parse_bib_entry, keep_fields = keep_fields)
}

# Removes braces and LaTeX commands from a BibTeX field (vectorized)
clean_bibtex_text <- function(text) {
  text <- ifelse(is.na(text), "", text)
  text <- str_remove_all(text, "^[{}]+|[{}]+$")
  text <- str_replace_all(text, "\\\\[a-zA-Z]+\\{([^}]*)\\}", "\\1")
  text <- str_replace_all(text, "\\\\[a-zA-Z]+", "")
  text <- str_replace_all(text, "[{}]", "")
  str_squish(text)
}

# Splits a keyword field on the first separator found
split_keywords <- function(keywords_str) {
  if (is.na(keywords_str) || keywords_str == "") {
    return(character(0))
  }
  for (sep in c(",", ";", "|", "\n")) {
    if (str_detect(keywords_str, fixed(sep))) {
      kw <- str_trim(str_split(keywords_str, fixed(sep))[[1]])
      return(kw[kw != ""])
    }
  }
  str_trim(keywords_str)
}

# Classifies a whole vector of analysis texts at once (vectorized for speed)
classify_text_vector <- function(text_vec) {
  n <- length(text_vec)
  text_vec <- ifelse(is.na(text_vec), "", text_vec)
  text_lower <- str_to_lower(text_vec)
  category_names <- names(METHOD_CATEGORIES)

  has_method_mat <- matrix(0L, nrow = n, ncol = length(category_names), dimnames = list(NULL, category_names))
  confidence_mat <- matrix(0, nrow = n, ncol = length(category_names), dimnames = list(NULL, category_names))

  for (cat in category_names) {
    keywords <- METHOD_CATEGORIES[[cat]]
    detect_mat <- do.call(cbind, lapply(keywords, function(kw) str_detect(text_lower, fixed(kw))))
    count_mat <- do.call(cbind, lapply(keywords, function(kw) str_count(text_lower, fixed(kw))))

    matches <- rowSums(detect_mat)
    occurrences <- rowSums(count_mat)
    has_method <- matches > 0

    base_confidence <- pmin((matches * 0.1) + (occurrences * 0.03), 0.6)
    diversity_bonus <- pmin(matches * 0.08, 0.3)
    confidence <- pmin(base_confidence + diversity_bonus, 1.0)
    confidence[!has_method] <- 0

    has_method_mat[, cat] <- as.integer(has_method)
    confidence_mat[, cat] <- confidence
  }

  detected_methods <- vapply(seq_len(n), function(i) {
    idx <- which(has_method_mat[i, ] == 1)
    if (length(idx) == 0) {
      return("NONE")
    }
    paste(sprintf("%s(%.2f)", category_names[idx], confidence_mat[i, idx]), collapse = "; ")
  }, character(1))

  has_any <- rowSums(has_method_mat) > 0
  overall_confidence <- ifelse(has_any, round(rowSums(confidence_mat) / length(category_names), 3), 0)

  uncertainty_mat <- do.call(cbind, lapply(
    UNCERTAINTY_PATTERNS,
    function(p) str_count(text_lower, regex(p, ignore_case = TRUE))
  ))

  out <- as_tibble(has_method_mat)
  out$DETECTED_METHODS <- detected_methods
  out$HAS_METHODS <- as.integer(has_any)
  out$CONFIDENCE <- overall_confidence
  out$UNCERTAINTY_STATEMENTS <- rowSums(uncertainty_mat)
  out$TEXT_LENGTH <- nchar(text_vec)
  out
}

# Groups classified results by decade for the Sankey plots
build_sankey_data <- function(results) {
  category_names <- names(METHOD_CATEGORIES)
  by_decade <- results |>
    filter(!is.na(YEAR)) |>
    mutate(decade = paste0((YEAR %/% 10) * 10, "s"))

  decade_list <- list()
  for (d in sort(unique(by_decade$decade))) {
    rows <- by_decade[by_decade$decade == d, ]
    methods <- list()
    for (cat in category_names) {
      count <- sum(rows[[cat]] == 1)
      if (count > 0) methods[[cat]] <- count
    }
    decade_list[[d]] <- list(total_papers = nrow(rows), methods = methods)
  }
  decade_list
}

# Builds the summary statistics report
build_report <- function(results) {
  category_names <- names(METHOD_CATEGORIES)
  total_papers <- nrow(results)
  papers_with_methods <- sum(results$HAS_METHODS == 1)
  detection_rate <- if (total_papers > 0) (papers_with_methods / total_papers) * 100 else 0

  method_stats <- list()
  for (cat in category_names) {
    count <- sum(results[[cat]] == 1)
    method_stats[[cat]] <- list(
      count = count,
      percentage = if (total_papers > 0) (count / total_papers) * 100 else 0
    )
  }

  by_decade <- results |>
    filter(!is.na(YEAR)) |>
    mutate(decade = paste0((YEAR %/% 10) * 10, "s"))

  decade_distribution <- by_decade |> count(decade)
  decade_distribution <- setNames(as.list(decade_distribution$n), decade_distribution$decade)

  method_by_decade <- list()
  for (d in sort(unique(by_decade$decade))) {
    rows <- by_decade[by_decade$decade == d, ]
    cats <- list()
    for (cat in category_names) {
      count <- sum(rows[[cat]] == 1)
      if (count > 0) cats[[cat]] <- count
    }
    if (length(cats) > 0) method_by_decade[[d]] <- cats
  }

  category_sum <- rowSums(as.matrix(results[category_names]))

  list(
    analysis_summary = list(
      total_papers = total_papers,
      papers_with_methods = papers_with_methods,
      detection_rate = detection_rate,
      high_confidence_papers = sum(results$CONFIDENCE > 0.3),
      multi_method_papers = sum(category_sum >= 3),
      average_confidence = if (total_papers > 0) mean(results$CONFIDENCE) else 0
    ),
    method_statistics = method_stats,
    decade_distribution = decade_distribution,
    method_by_decade = method_by_decade,
    validation_metrics = list(
      categories_detected = sum(vapply(method_stats, function(x) x$count > 0, logical(1))),
      decades_covered = length(unique(by_decade$decade)),
      coverage_completeness = detection_rate
    )
  )
}

# Processes every .bib file in bib_dir and writes the CSV/JSON outputs
classify_methods <- function(bib_dir = "bib/bib_raw",
                              csv_out = "data/analysis_results/FINAL_methods_analysis.csv",
                              sankey_out = "data/reports/FINAL_sankey_data.json",
                              report_out = "data/reports/FINAL_analysis_report.json") {
  keep_fields <- c("title", "author", "year", "abstract", "keywords", "journal", "booktitle")

  # top-level files only, same as R/prisma_pipeline.R (bib_raw/manual_run/ is a stale copy)
  files <- sort(list.files(bib_dir, pattern = "\\.bib$", full.names = TRUE))
  cat("Found", length(files), "BibTeX files in", bib_dir, "\n")
  raw <- map_dfr(files, read_bib_file, keep_fields = keep_fields)
  cat("Parsed", nrow(raw), "entries\n")

  title_clean <- clean_bibtex_text(raw$title)
  authors_clean <- clean_bibtex_text(raw$author)
  abstract_clean <- clean_bibtex_text(raw$abstract)
  keywords_clean <- clean_bibtex_text(raw$keywords)
  journal_raw <- clean_bibtex_text(raw$journal)
  booktitle_raw <- clean_bibtex_text(raw$booktitle)
  journal_clean <- ifelse(journal_raw != "", journal_raw, booktitle_raw)
  year_clean <- suppressWarnings(as.integer(str_extract(raw$year, "\\d{4}")))

  keyword_lists <- map(keywords_clean, split_keywords)
  keywords_weighted <- vapply(keyword_lists, paste, character(1), collapse = " ")
  keywords_display <- vapply(keyword_lists, function(x) paste(x, collapse = "; "), character(1))

  # weighted analysis text: title counts 3x, abstract 2x, matching the Python scorer
  analysis_text <- str_trim(paste0(
    paste(title_clean, title_clean, title_clean), ". ",
    paste(abstract_clean, abstract_clean), ". ",
    keywords_weighted, ". ",
    journal_clean
  ))

  methods <- classify_text_vector(analysis_text)
  bibref <- ifelse(is.na(raw$key) | raw$key == "", "unknown", raw$key)

  results <- bind_cols(
    tibble(
      TITLE = title_clean,
      YEAR = year_clean,
      BIBREF = bibref,
      AUTHORS = authors_clean,
      JOURNAL = journal_clean
    ),
    methods[, c("DETECTED_METHODS", "CONFIDENCE", "HAS_METHODS", "UNCERTAINTY_STATEMENTS", "TEXT_LENGTH")],
    methods[, names(METHOD_CATEGORIES)],
    tibble(ABSTRACT = abstract_clean, KEYWORDS = keywords_display)
  ) |>
    arrange(coalesce(YEAR, 0L), TITLE)

  dir.create(dirname(csv_out), recursive = TRUE, showWarnings = FALSE)
  dir.create(dirname(sankey_out), recursive = TRUE, showWarnings = FALSE)

  write_csv(results, csv_out)
  cat("Saved", nrow(results), "papers to", csv_out, "\n")

  write(toJSON(build_sankey_data(results), auto_unbox = TRUE, pretty = TRUE), sankey_out)
  cat("Saved Sankey data to", sankey_out, "\n")

  write(toJSON(build_report(results), auto_unbox = TRUE, pretty = TRUE), report_out)
  cat("Saved analysis report to", report_out, "\n")

  invisible(results)
}

if (!interactive()) {
  classify_methods()
}
