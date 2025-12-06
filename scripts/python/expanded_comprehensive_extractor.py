#!/usr/bin/env python3
"""
Expanded Comprehensive Methods Extractor for Decision Support Literature

Based on original search terms:
"decision"+("intervention"OR"policy")+"uncertainty"+("expert"OR"stakeholder")+
("model"OR"monte carlo"OR"simulation"OR"Bayesian"OR"computer assisted")+
("value of information"OR"information accuracy")

This version includes much broader categories to capture decision support,
policy analysis, intervention evaluation, stakeholder engagement, and
uncertainty analysis methods.
"""

import csv
import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import bibtexparser

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExpandedMethodsExtractor:
    """Vastly expanded extraction based on original search strategy"""

    # Massively expanded method categories based on search terms and decision support literature
    METHOD_CATEGORIES = {
        # Core decision analysis methods
        "DECISION_ANALYSIS": [
            "decision analysis",
            "decision tree",
            "decision support",
            "decision making",
            "decision model",
            "decision framework",
            "decision process",
            "decision theory",
            "influence diagram",
            "decision network",
            "rollback analysis",
            "backward induction",
            "value of information",
            "information accuracy",
            "perfect information",
            "expected value",
            "decision criterion",
            "decision rule",
            "choice model",
            "alternative evaluation",
            "option assessment",
            "choice analysis",
            "prescriptive analytics",
            "normative decision",
            "rational choice",
        ],
        # Policy and intervention analysis
        "POLICY_INTERVENTION": [
            "policy analysis",
            "policy evaluation",
            "policy assessment",
            "policy model",
            "intervention analysis",
            "intervention evaluation",
            "intervention assessment",
            "policy support",
            "policy decision",
            "policy making",
            "policy framework",
            "policy tool",
            "policy instrument",
            "regulatory analysis",
            "governance",
            "public policy",
            "social policy",
            "economic policy",
            "environmental policy",
            "health policy",
            "intervention design",
            "program evaluation",
            "impact assessment",
            "cost-effectiveness",
            "cost-benefit",
            "policy option",
            "policy alternative",
            "policy scenario",
            "intervention strategy",
            "policy intervention",
            "implementation analysis",
            "policy implementation",
            "regulatory impact",
            "policy simulation",
            "intervention modeling",
            "policy optimization",
            "evidence-based policy",
            "policy research",
            "intervention research",
        ],
        # Uncertainty and risk analysis
        "UNCERTAINTY_ANALYSIS": [
            "uncertainty analysis",
            "uncertainty assessment",
            "uncertainty quantification",
            "uncertainty propagation",
            "uncertainty modeling",
            "parameter uncertainty",
            "model uncertainty",
            "structural uncertainty",
            "epistemic uncertainty",
            "aleatory uncertainty",
            "deep uncertainty",
            "severe uncertainty",
            "risk analysis",
            "risk assessment",
            "risk evaluation",
            "risk management",
            "risk modeling",
            "probabilistic risk",
            "quantitative risk",
            "risk characterization",
            "variability analysis",
            "sensitivity analysis",
            "scenario analysis",
            "what-if analysis",
            "stress testing",
            "robustness analysis",
            "confidence interval",
            "credible interval",
            "prediction interval",
            "error propagation",
            "error analysis",
            "measurement uncertainty",
            "modeling uncertainty",
            "forecast uncertainty",
            "projection uncertainty",
        ],
        # Stakeholder and expert engagement
        "STAKEHOLDER_EXPERT": [
            "stakeholder analysis",
            "stakeholder engagement",
            "stakeholder involvement",
            "stakeholder participation",
            "stakeholder consultation",
            "stakeholder input",
            "expert judgment",
            "expert elicitation",
            "expert assessment",
            "expert opinion",
            "expert knowledge",
            "expert consultation",
            "expert panel",
            "expert system",
            "participatory",
            "participatory modeling",
            "participatory decision",
            "collaborative decision",
            "group decision",
            "consensus building",
            "multi-stakeholder",
            "stakeholder-driven",
            "community-based",
            "delphi method",
            "nominal group",
            "focus group",
            "structured interview",
            "knowledge elicitation",
            "preference elicitation",
            "value elicitation",
            "participatory research",
            "action research",
            "co-design",
            "co-creation",
            "citizen participation",
            "public participation",
            "social learning",
            "deliberative process",
            "facilitated workshop",
            "stakeholder workshop",
        ],
        # Modeling and simulation approaches
        "MODELING_SIMULATION": [
            "mathematical model",
            "conceptual model",
            "analytical model",
            "empirical model",
            "statistical model",
            "econometric model",
            "simulation model",
            "computer model",
            "computational model",
            "numerical model",
            "predictive model",
            "forecasting model",
            "monte carlo",
            "monte carlo simulation",
            "stochastic simulation",
            "discrete event simulation",
            "agent-based model",
            "system dynamics",
            "microsimulation",
            "macrosimulation",
            "dynamic model",
            "static model",
            "linear model",
            "nonlinear model",
            "optimization model",
            "network model",
            "spatial model",
            "temporal model",
            "integrated model",
            "coupled model",
            "ensemble model",
            "meta-model",
            "surrogate model",
            "emulator",
            "model validation",
            "model verification",
            "model calibration",
            "computer simulation",
            "numerical simulation",
            "scenario modeling",
        ],
        # Bayesian and probabilistic methods
        "BAYESIAN_PROBABILISTIC": [
            "bayesian",
            "bayes",
            "posterior",
            "prior",
            "likelihood",
            "bayesian inference",
            "bayesian analysis",
            "bayesian statistics",
            "bayesian network",
            "belief network",
            "bayesian updating",
            "markov chain monte carlo",
            "mcmc",
            "gibbs sampling",
            "metropolis",
            "hamiltonian monte carlo",
            "variational bayes",
            "empirical bayes",
            "hierarchical bayes",
            "approximate bayesian",
            "probabilistic",
            "probability",
            "stochastic",
            "random",
            "statistical",
            "probability distribution",
            "probability model",
            "stochastic process",
            "markov process",
            "random variable",
            "probability density",
            "likelihood function",
            "maximum likelihood",
            "expectation maximization",
            "bootstrap",
            "jackknife",
            "resampling",
            "cross-validation",
            "statistical inference",
            "hypothesis testing",
        ],
        # Computer-assisted and digital methods
        "COMPUTER_ASSISTED": [
            "computer assisted",
            "computer-assisted",
            "computer aided",
            "computer-aided",
            "computerized",
            "digital",
            "automated",
            "software",
            "algorithm",
            "computational",
            "machine learning",
            "artificial intelligence",
            "deep learning",
            "neural network",
            "data mining",
            "big data",
            "analytics",
            "predictive analytics",
            "data science",
            "decision support system",
            "expert system",
            "knowledge-based system",
            "information system",
            "management information system",
            "geographic information system",
            "web-based",
            "online",
            "internet-based",
            "cloud-based",
            "mobile application",
            "dashboard",
            "visualization",
            "interactive",
            "user interface",
            "software tool",
            "digital platform",
            "electronic",
            "cyber",
            "virtual",
            "augmented reality",
            "simulation software",
            "modeling software",
            "statistical software",
        ],
        # Value of information and accuracy
        "VALUE_INFORMATION": [
            "value of information",
            "value of perfect information",
            "value of imperfect information",
            "expected value of information",
            "evpi",
            "evii",
            "information value",
            "information accuracy",
            "information quality",
            "data quality",
            "measurement accuracy",
            "precision",
            "reliability",
            "validity",
            "information content",
            "information theory",
            "information gain",
            "entropy",
            "mutual information",
            "signal-to-noise",
            "measurement error",
            "observation error",
            "sampling error",
            "bias",
            "calibration",
            "discrimination",
            "model performance",
            "prediction accuracy",
            "forecast accuracy",
            "estimation accuracy",
            "classification accuracy",
            "diagnostic accuracy",
            "sensitivity",
            "specificity",
            "positive predictive value",
            "negative predictive value",
            "area under curve",
            "receiver operating characteristic",
        ],
        # Multi-criteria decision analysis
        "MULTI_CRITERIA": [
            "multi-criteria",
            "multicriteria",
            "multi-criterion",
            "multicriterion",
            "multiple criteria",
            "multiple criterion",
            "mcda",
            "mcdm",
            "madm",
            "modm",
            "analytic hierarchy process",
            "ahp",
            "analytic network process",
            "anp",
            "topsis",
            "electre",
            "promethee",
            "vikor",
            "saw",
            "wpm",
            "wsm",
            "outranking",
            "concordance",
            "discordance",
            "preference ranking",
            "multi-attribute",
            "multiattribute",
            "multi-objective",
            "multiobjective",
            "goal programming",
            "compromise programming",
            "reference point",
            "utility function",
            "value function",
            "scoring method",
            "weighting method",
        ],
        # Optimization methods
        "OPTIMIZATION": [
            "optimization",
            "optimisation",
            "minimize",
            "maximize",
            "optimal",
            "optimum",
            "linear programming",
            "nonlinear programming",
            "integer programming",
            "mixed integer",
            "dynamic programming",
            "stochastic programming",
            "robust optimization",
            "chance-constrained",
            "multi-objective optimization",
            "pareto optimal",
            "pareto front",
            "evolutionary algorithm",
            "genetic algorithm",
            "particle swarm",
            "simulated annealing",
            "tabu search",
            "local search",
            "global optimization",
            "convex optimization",
            "gradient descent",
            "newton method",
            "quasi-newton",
            "interior point",
            "simplex method",
            "branch and bound",
            "cutting plane",
            "lagrangian",
            "dual problem",
        ],
        # Economic evaluation methods
        "ECONOMIC_EVALUATION": [
            "cost-effectiveness",
            "cost-benefit",
            "cost-utility",
            "cost-minimization",
            "economic evaluation",
            "health economics",
            "pharmacoeconomics",
            "budget impact",
            "return on investment",
            "net present value",
            "internal rate of return",
            "cost per qaly",
            "quality adjusted life years",
            "disability adjusted life years",
            "incremental cost-effectiveness",
            "willingness to pay",
            "contingent valuation",
            "discrete choice experiment",
            "conjoint analysis",
            "stated preference",
            "revealed preference",
            "hedonic pricing",
            "travel cost method",
            "benefit transfer",
            "value transfer",
            "meta-analysis",
            "systematic review",
        ],
        # Game theory and strategic analysis
        "GAME_THEORY": [
            "game theory",
            "strategic",
            "nash equilibrium",
            "dominant strategy",
            "prisoner dilemma",
            "coordination game",
            "bargaining",
            "negotiation",
            "auction theory",
            "mechanism design",
            "cooperative game",
            "coalition",
            "conflict analysis",
            "strategic interaction",
            "behavioral game theory",
            "experimental game theory",
            "evolutionary game theory",
            "repeated game",
            "signaling game",
            "screening model",
            "moral hazard",
            "adverse selection",
        ],
        # Behavioral and psychological factors
        "BEHAVIORAL_PSYCHOLOGY": [
            "behavioral",
            "behaviour",
            "psychology",
            "cognitive",
            "heuristic",
            "bias",
            "prospect theory",
            "bounded rationality",
            "satisficing",
            "anchoring",
            "availability heuristic",
            "representativeness",
            "framing effect",
            "loss aversion",
            "endowment effect",
            "status quo bias",
            "confirmation bias",
            "overconfidence",
            "optimism bias",
            "planning fallacy",
            "mental accounting",
            "social psychology",
            "group psychology",
            "decision psychology",
            "judgment and decision making",
            "human factors",
            "usability",
        ],
        # Systems analysis and complexity
        "SYSTEMS_COMPLEXITY": [
            "systems analysis",
            "systems thinking",
            "systems approach",
            "complex system",
            "system of systems",
            "socio-technical system",
            "socio-ecological system",
            "coupled system",
            "feedback",
            "emergence",
            "complexity science",
            "network analysis",
            "social network",
            "organizational network",
            "supply chain",
            "value chain",
            "ecosystem",
            "resilience",
            "adaptability",
            "vulnerability",
            "sustainability",
            "adaptive management",
            "adaptive capacity",
            "tipping point",
            "phase transition",
            "bifurcation",
            "chaos theory",
        ],
        # Technology assessment and innovation
        "TECHNOLOGY_INNOVATION": [
            "technology assessment",
            "health technology assessment",
            "hta",
            "innovation",
            "diffusion",
            "adoption",
            "implementation",
            "scaling up",
            "technology transfer",
            "knowledge transfer",
            "translational research",
            "research and development",
            "r&d",
            "innovation system",
            "innovation policy",
            "disruptive innovation",
            "incremental innovation",
            "radical innovation",
            "technology roadmap",
            "foresight",
            "horizon scanning",
            "early warning",
        ],
        # Environmental and sustainability assessment
        "ENVIRONMENTAL_SUSTAINABILITY": [
            "environmental assessment",
            "environmental impact",
            "life cycle assessment",
            "lca",
            "carbon footprint",
            "water footprint",
            "ecological footprint",
            "environmental management",
            "sustainability",
            "sustainable development",
            "circular economy",
            "green technology",
            "renewable energy",
            "climate change",
            "ecosystem services",
            "biodiversity",
            "conservation",
            "natural resource management",
            "environmental economics",
            "environmental valuation",
            "contingent valuation",
        ],
        # Quality improvement and performance measurement
        "QUALITY_PERFORMANCE": [
            "quality improvement",
            "performance measurement",
            "performance indicator",
            "key performance indicator",
            "kpi",
            "balanced scorecard",
            "dashboard",
            "benchmarking",
            "best practice",
            "process improvement",
            "continuous improvement",
            "total quality management",
            "six sigma",
            "lean",
            "kaizen",
            "plan-do-check-act",
            "quality assurance",
            "quality control",
            "performance monitoring",
            "outcome measurement",
            "impact evaluation",
            "program evaluation",
        ],
        # Risk management and safety
        "RISK_SAFETY": [
            "risk management",
            "risk assessment",
            "hazard analysis",
            "safety analysis",
            "fault tree analysis",
            "event tree analysis",
            "failure mode",
            "reliability analysis",
            "probabilistic risk assessment",
            "quantitative risk assessment",
            "safety management",
            "occupational safety",
            "patient safety",
            "food safety",
            "environmental safety",
            "security",
            "cybersecurity",
            "information security",
            "business continuity",
            "disaster management",
            "emergency management",
            "crisis management",
        ],
        # Forecasting and prediction
        "FORECASTING_PREDICTION": [
            "forecasting",
            "prediction",
            "predictive",
            "forecast",
            "projection",
            "scenario",
            "time series",
            "trend analysis",
            "extrapolation",
            "interpolation",
            "regression",
            "autoregressive",
            "moving average",
            "exponential smoothing",
            "neural network",
            "machine learning",
            "ensemble forecasting",
            "judgmental forecasting",
            "expert forecasting",
            "delphi forecasting",
            "forecast combination",
            "forecast accuracy",
            "forecast evaluation",
        ],
        # Evaluation and assessment methods
        "EVALUATION_ASSESSMENT": [
            "evaluation",
            "assessment",
            "appraisal",
            "review",
            "audit",
            "inspection",
            "monitoring",
            "surveillance",
            "screening",
            "diagnosis",
            "testing",
            "measurement",
            "metric",
            "indicator",
            "index",
            "score",
            "rating",
            "ranking",
            "classification",
            "categorization",
            "benchmarking",
            "comparative analysis",
            "before-after",
            "with-without",
            "control group",
            "randomized controlled trial",
            "quasi-experimental",
            "observational study",
        ],
    }

    # Expanded uncertainty patterns
    UNCERTAINTY_PATTERNS = [
        r"uncertain(ty)?",
        r"risk\b",
        r"variability",
        r"ambiguity",
        r"imprecis",
        r"confidence interval",
        r"credible interval",
        r"prediction interval",
        r"standard error",
        r"standard deviation",
        r"variance",
        r"volatility",
        r"sensitivity",
        r"robust(ness)?",
        r"what.?if",
        r"scenario",
        r"vague",
        r"incomplete information",
        r"limited information",
        r"missing data",
        r"parameter uncertainty",
        r"model uncertainty",
        r"structural uncertainty",
        r"epistemic",
        r"aleatory",
        r"deep uncertainty",
        r"severe uncertainty",
        r"error propagation",
        r"measurement error",
        r"observation error",
        r"sampling error",
        r"bias",
        r"noise",
        r"random error",
        r"systematic error",
        r"uncertainty analysis",
        r"uncertainty assessment",
        r"uncertainty quantification",
        r"monte carlo",
        r"bootstrap",
        r"probabilistic",
        r"stochastic",
        r"distribution",
        r"probability",
        r"likelihood",
        r"confidence",
        r"unreliable",
        r"questionable",
        r"doubt",
        r"approximate",
    ]

    def __init__(self, bib_raw_directory: str = "bib/bib_raw"):
        self.bib_raw_directory = Path(bib_raw_directory)
        self.results = []

    def clean_bibtex_text(self, text: str) -> str:
        """Clean BibTeX text by removing braces and LaTeX commands"""
        if not text:
            return ""

        # Remove curly braces
        text = text.strip("{}")

        # Remove common LaTeX commands
        text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)
        text = re.sub(r"[\{\}]", "", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def extract_methods_comprehensive(self, text: str) -> Dict:
        """Extract all methods with binary indicators and confidence scores"""
        if not text:
            return self._empty_methods_dict()

        text_lower = text.lower()
        results = {}
        detected_methods = []
        total_confidence = 0.0

        # Check each method category
        for category, keywords in self.METHOD_CATEGORIES.items():
            matches = 0
            keyword_occurrences = 0
            matched_keywords = []

            for keyword in keywords:
                if keyword in text_lower:
                    matches += 1
                    keyword_occurrences += text_lower.count(keyword)
                    matched_keywords.append(keyword)

            # Binary indicator
            has_method = matches > 0
            results[category] = 1 if has_method else 0

            # Add to detected methods list if found
            if has_method:
                # Calculate confidence based on matches and frequency
                base_confidence = min(
                    (matches * 0.15) + (keyword_occurrences * 0.05), 0.9
                )
                # Boost confidence for multiple different keywords
                diversity_bonus = min(len(set(matched_keywords)) * 0.1, 0.3)
                confidence = min(base_confidence + diversity_bonus, 1.0)

                detected_methods.append(f"{category}({confidence:.2f})")
                total_confidence += confidence

        # Overall indicators
        results["DETECTED_METHODS"] = (
            "; ".join(detected_methods) if detected_methods else "NONE"
        )
        results["HAS_METHODS"] = 1 if detected_methods else 0
        results["CONFIDENCE"] = (
            round(total_confidence / len(self.METHOD_CATEGORIES), 3)
            if detected_methods
            else 0.0
        )

        # Count uncertainty statements with expanded patterns
        uncertainty_count = 0
        for pattern in self.UNCERTAINTY_PATTERNS:
            uncertainty_count += len(re.findall(pattern, text_lower, re.IGNORECASE))
        results["UNCERTAINTY_STATEMENTS"] = uncertainty_count

        return results

    def _empty_methods_dict(self) -> Dict:
        """Return empty methods dictionary with all categories set to 0"""
        results = {category: 0 for category in self.METHOD_CATEGORIES.keys()}
        results.update(
            {
                "DETECTED_METHODS": "NONE",
                "HAS_METHODS": 0,
                "CONFIDENCE": 0.0,
                "UNCERTAINTY_STATEMENTS": 0,
            }
        )
        return results

    def process_bibtex_entry(self, entry: Dict) -> Dict:
        """Process a single BibTeX entry comprehensively"""
        # Extract basic information
        bibref = entry.get("ID", "unknown")
        title = self.clean_bibtex_text(entry.get("title", ""))
        authors = self.clean_bibtex_text(entry.get("author", ""))
        year_str = entry.get("year", "")
        abstract = self.clean_bibtex_text(entry.get("abstract", ""))
        keywords_str = self.clean_bibtex_text(entry.get("keywords", ""))
        journal = self.clean_bibtex_text(
            entry.get("journal", entry.get("booktitle", ""))
        )

        # Parse year
        try:
            year = int(year_str) if year_str else None
        except (ValueError, TypeError):
            year = None

        # Parse keywords
        keywords = []
        if keywords_str:
            for sep in [",", ";", "\\n", "\n", "|"]:
                if sep in keywords_str:
                    keywords = [k.strip() for k in keywords_str.split(sep) if k.strip()]
                    break
            if not keywords and keywords_str:
                keywords = [keywords_str.strip()]

        # Combine all available text for analysis
        # Weight title more heavily, then abstract, then keywords
        title_weighted = f"{title} {title} {title}"  # Title appears 3 times
        abstract_weighted = f"{abstract} {abstract}"  # Abstract appears 2 times
        keywords_weighted = " ".join(keywords)  # Keywords appear once

        analysis_text = f"{title_weighted}. {abstract_weighted}. {keywords_weighted}. {journal}".strip()

        # Extract methods comprehensively
        methods_results = self.extract_methods_comprehensive(analysis_text)

        # Create comprehensive result
        result = {
            "TITLE": title,
            "YEAR": year or "",
            "BIBREF": bibref,
            "AUTHORS": authors,
            "JOURNAL": journal,
            "ABSTRACT": abstract,
            "KEYWORDS": "; ".join(keywords),
            **methods_results,
        }

        return result

    def process_bibtex_file(self, file_path: Path) -> List[Dict]:
        """Process a single BibTeX file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bib_database = bibtexparser.load(f)

            logger.info(
                f"Processing {file_path.name}: {len(bib_database.entries)} entries"
            )

            results = []
            for entry in bib_database.entries:
                result = self.process_bibtex_entry(entry)
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []

    def process_all_files(self) -> List[Dict]:
        """Process all BibTeX files"""
        bib_files = list(self.bib_raw_directory.glob("*.bib"))
        logger.info(f"Found {len(bib_files)} BibTeX files")

        all_results = []
        for bib_file in sorted(bib_files):
            results = self.process_bibtex_file(bib_file)
            all_results.extend(results)

        self.results = all_results
        logger.info(f"Processed {len(all_results)} total entries")
        return all_results

    def save_expanded_csv(self, output_file: str = "expanded_methods_analysis.csv"):
        """Save expanded CSV with all method indicators"""
        if not self.results:
            logger.warning("No results to save")
            return

        # Sort by year, then by title
        sorted_results = sorted(
            self.results, key=lambda x: (x["YEAR"] or 0, x["TITLE"])
        )

        # Define column order for clarity
        columns = [
            "TITLE",
            "YEAR",
            "BIBREF",
            "AUTHORS",
            "JOURNAL",
            "DETECTED_METHODS",
            "CONFIDENCE",
            "HAS_METHODS",
            "UNCERTAINTY_STATEMENTS",
            # Core categories from original search
            "DECISION_ANALYSIS",
            "POLICY_INTERVENTION",
            "UNCERTAINTY_ANALYSIS",
            "STAKEHOLDER_EXPERT",
            "MODELING_SIMULATION",
            "BAYESIAN_PROBABILISTIC",
            "COMPUTER_ASSISTED",
            "VALUE_INFORMATION",
            # Additional comprehensive categories
            "MULTI_CRITERIA",
            "OPTIMIZATION",
            "ECONOMIC_EVALUATION",
            "GAME_THEORY",
            "BEHAVIORAL_PSYCHOLOGY",
            "SYSTEMS_COMPLEXITY",
            "TECHNOLOGY_INNOVATION",
            "ENVIRONMENTAL_SUSTAINABILITY",
            "QUALITY_PERFORMANCE",
            "RISK_SAFETY",
            "FORECASTING_PREDICTION",
            "EVALUATION_ASSESSMENT",
            # Text fields
            "ABSTRACT",
            "KEYWORDS",
        ]

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for result in sorted_results:
                # Ensure all columns exist
                row = {col: result.get(col, "") for col in columns}
                writer.writerow(row)

        logger.info(f"Expanded CSV saved to {output_file}")

    def generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report"""
        if not self.results:
            return {}

        total_papers = len(self.results)
        papers_with_methods = sum(1 for r in self.results if r["HAS_METHODS"] == 1)

        # Method category statistics
        method_stats = {}
        for category in self.METHOD_CATEGORIES.keys():
            count = sum(1 for r in self.results if r[category] == 1)
            method_stats[category] = {
                "count": count,
                "percentage": (count / total_papers) * 100 if total_papers > 0 else 0,
            }

        # Year distribution
        year_dist = defaultdict(int)
        for result in self.results:
            if result["YEAR"]:
                decade = f"{(result['YEAR'] // 10) * 10}s"
                year_dist[decade] += 1

        # High confidence papers
        high_confidence = [r for r in self.results if r["CONFIDENCE"] > 0.3]

        # Papers with multiple methods
        multi_method_papers = []
        for result in self.results:
            method_count = sum(
                1 for cat in self.METHOD_CATEGORIES.keys() if result[cat] == 1
            )
            if method_count >= 3:
                multi_method_papers.append(result)

        summary = {
            "total_papers": total_papers,
            "papers_with_methods": papers_with_methods,
            "percentage_with_methods": (papers_with_methods / total_papers) * 100
            if total_papers > 0
            else 0,
            "method_statistics": method_stats,
            "year_distribution": dict(year_dist),
            "high_confidence_papers": len(high_confidence),
            "multi_method_papers": len(multi_method_papers),
            "average_confidence": sum(r["CONFIDENCE"] for r in self.results)
            / total_papers
            if total_papers > 0
            else 0,
            "average_uncertainty_statements": sum(
                r["UNCERTAINTY_STATEMENTS"] for r in self.results
            )
            / total_papers
            if total_papers > 0
            else 0,
        }

        return summary

    def print_summary(self):
        """Print comprehensive analysis summary"""
        summary = self.generate_summary_report()

        print("\n" + "=" * 90)
        print("EXPANDED COMPREHENSIVE BIBTEX METHODS ANALYSIS SUMMARY")
        print("=" * 90)

        if not summary:
            print("No results to summarize.")
            return

        print(f"Total Papers: {summary['total_papers']:,}")
        print(
            f"Papers with Methods: {summary['papers_with_methods']:,} ({summary['percentage_with_methods']:.1f}%)"
        )
        print(f"High Confidence Papers (>0.3): {summary['high_confidence_papers']:,}")
        print(f"Multi-Method Papers (≥3 methods): {summary['multi_method_papers']:,}")
        print(f"Average Confidence Score: {summary['average_confidence']:.3f}")
        print(
            f"Average Uncertainty Statements: {summary['average_uncertainty_statements']:.1f}"
        )

        print("\nMethod Category Distribution (Top 15):")
        sorted_methods = sorted(
            summary["method_statistics"].items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )
        for method, stats in sorted_methods[:15]:
            print(
                f"  {method:25}: {stats['count']:5,} papers ({stats['percentage']:5.1f}%)"
            )

        if len(sorted_methods) > 15:
            remaining = len(sorted_methods) - 15
            print(f"  ... and {remaining} more categories")

        print(f"\nDecade Distribution:")
        for decade in sorted(summary["year_distribution"].keys()):
            count = summary["year_distribution"][decade]
            print(f"  {decade}: {count:,} papers")

        print("=" * 90)


def main():
    """Main execution function"""
    extractor = ExpandedMethodsExtractor()

    # Process all files
    results = extractor.process_all_files()

    if not results:
        print("No results found. Please check your BibTeX files in bib/bib_raw/")
        return

    # Save expanded CSV
    extractor.save_expanded_csv("expanded_methods_analysis.csv")

    # Print summary
    extractor.print_summary()

    # Save detailed summary as JSON
    summary = extractor.generate_summary_report()
    with open("expanded_methods_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nOutput files created:")
    print(
        f"  - expanded_methods_analysis.csv (comprehensive CSV with expanded method detection)"
    )
    print(f"  - expanded_methods_summary.json (detailed summary statistics)")

    # Show some example high-confidence detections
    high_conf_examples = [r for r in results if r["CONFIDENCE"] > 0.5][:5]
    if high_conf_examples:
        print(f"\nExample high-confidence detections:")
        for example in high_conf_examples:
            print(f"  • {example['TITLE'][:60]}...")
            print(f"    Methods: {example['DETECTED_METHODS'][:100]}...")
            print(f"    Confidence: {example['CONFIDENCE']:.3f}")
            print()


if __name__ == "__main__":
    main()
