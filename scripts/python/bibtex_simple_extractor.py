#!/usr/bin/env python3
"""
Simple BibTeX Methods Extractor

A lightweight version that extracts decision analysis methods from BibTeX files
without requiring PDF processing. Uses only the metadata available in BibTeX entries.

Requirements:
    pip install bibtexparser pydantic

Usage:
    python bibtex_simple_extractor.py
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import bibtexparser
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DecisionPaper(BaseModel):
    """Pydantic model for structured decision paper analysis"""

    paper_id: str = Field(description="Unique identifier from BibTeX")
    title: str = Field(description="Paper title")
    authors: str = Field(description="Paper authors")
    year: Optional[int] = Field(description="Publication year")
    journal: Optional[str] = Field(description="Journal or venue")
    is_probabilistic: bool = Field(
        description="Indicates if the method is probabilistic"
    )
    is_bayesian: bool = Field(description="Indicates if the method is Bayesian")
    methods_category: str = Field(
        description="Category of the methods used in the decision paper"
    )
    keeney_decision_category: str = Field(
        description="Keeney decision analysis category"
    )
    number_of_statements_about_uncertainty: int = Field(
        description="Number of statements about uncertainty in the decision paper"
    )
    extracted_methods: List[str] = Field(
        default=[], description="List of identified methods"
    )
    abstract: Optional[str] = Field(default=None, description="Paper abstract")
    keywords: List[str] = Field(default=[], description="Paper keywords")
    confidence_score: float = Field(
        default=0.0, description="Confidence in method extraction (metadata only)"
    )
    doi: Optional[str] = Field(default=None, description="DOI if available")
    url: Optional[str] = Field(default=None, description="URL if available")


class SimpleBibTeXExtractor:
    """Lightweight BibTeX methods extractor using only metadata"""

    # Decision analysis method keywords
    PROBABILISTIC_KEYWORDS = [
        "monte carlo",
        "simulation",
        "probability",
        "stochastic",
        "random",
        "sampling",
        "likelihood",
        "probabilistic",
        "uncertain",
        "risk analysis",
        "sensitivity analysis",
        "variance",
        "distribution",
    ]

    BAYESIAN_KEYWORDS = [
        "bayesian",
        "bayes",
        "posterior",
        "prior",
        "mcmc",
        "gibbs",
        "metropolis",
        "belief network",
        "bayesian network",
        "credible interval",
        "bayesian inference",
        "bayesian analysis",
        "hierarchical",
    ]

    KEENEY_CATEGORIES = {
        "value_focused": [
            "value focused",
            "value-focused",
            "value model",
            "utility function",
            "multi-attribute utility",
            "multiattribute utility",
            "maut",
            "value tree",
            "objective hierarchy",
        ],
        "alternative_focused": [
            "alternative focused",
            "alternative-focused",
            "decision tree",
            "influence diagram",
            "decision network",
            "fault tree",
        ],
        "prescriptive": [
            "prescriptive",
            "decision analysis",
            "decision support",
            "decision aid",
            "normative",
            "optimal decision",
            "rational choice",
        ],
        "descriptive": [
            "descriptive",
            "behavioral",
            "cognitive bias",
            "heuristic",
            "bounded rationality",
            "prospect theory",
            "behavioral economics",
        ],
    }

    DECISION_METHODS = [
        "decision tree",
        "influence diagram",
        "multi-criteria decision analysis",
        "multicriteria decision analysis",
        "mcda",
        "mcdm",
        "analytic hierarchy process",
        "analytical hierarchy process",
        "ahp",
        "topsis",
        "electre",
        "promethee",
        "value function",
        "utility theory",
        "expected utility",
        "prospect theory",
        "fuzzy logic",
        "rough set",
        "delphi method",
        "expert judgment",
        "expert elicitation",
        "scenario analysis",
        "robust decision making",
        "real options",
        "decision support system",
        "multi-objective optimization",
        "multiobjective optimization",
        "pareto optimal",
        "compromise programming",
        "goal programming",
        "outranking",
        "concordance analysis",
        "preference modeling",
        "swing weighting",
        "direct rating",
        "pairwise comparison",
    ]

    UNCERTAINTY_PATTERNS = [
        r"uncertain(ty)?",
        r"risk\b",
        r"variability",
        r"ambiguity",
        r"confidence interval",
        r"standard error",
        r"variance",
        r"sensitivity",
        r"robust(ness)?",
        r"what.?if",
        r"scenario",
        r"volatility",
        r"imprecis",
        r"vague",
        r"incomplete information",
    ]

    def __init__(self, bib_directory: str = "bib"):
        self.bib_directory = Path(bib_directory)
        self.results: List[DecisionPaper] = []

    def find_bibtex_files(self) -> List[Path]:
        """Find all BibTeX files in the directory and subdirectories"""
        bib_files = []
        for path in self.bib_directory.rglob("*.bib"):
            bib_files.append(path)
        logger.info(f"Found {len(bib_files)} BibTeX files")
        return bib_files

    def parse_bibtex_file(self, file_path: Path) -> List[Dict]:
        """Parse a single BibTeX file and return entries"""
        try:
            with open(file_path, "r", encoding="utf-8") as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
            logger.info(f"Parsed {len(bib_database.entries)} entries from {file_path}")
            return bib_database.entries
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return []

    def clean_bibtex_text(self, text: str) -> str:
        """Clean BibTeX text by removing braces and LaTeX commands"""
        if not text:
            return ""

        # Remove curly braces
        text = text.strip("{}")

        # Remove common LaTeX commands
        text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def analyze_metadata_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content for decision analysis methods (metadata only)"""
        text_lower = text.lower()

        # Check for probabilistic methods
        is_probabilistic = any(
            keyword in text_lower for keyword in self.PROBABILISTIC_KEYWORDS
        )

        # Check for Bayesian methods
        is_bayesian = any(keyword in text_lower for keyword in self.BAYESIAN_KEYWORDS)

        # Determine Keeney category
        keeney_category = "unknown"
        keeney_scores = {}

        for category, keywords in self.KEENEY_CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            keeney_scores[category] = score

        # Get category with highest score
        if any(score > 0 for score in keeney_scores.values()):
            keeney_category = max(keeney_scores, key=keeney_scores.get)

        # Extract specific methods
        extracted_methods = []
        method_scores = {}

        for method in self.DECISION_METHODS:
            if method in text_lower:
                method_scores[method] = text_lower.count(method)
                extracted_methods.append(method)

        # Count uncertainty statements
        uncertainty_count = 0
        for pattern in self.UNCERTAINTY_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            uncertainty_count += len(matches)

        # Determine methods category
        methods_category = self._categorize_methods(
            extracted_methods, is_probabilistic, is_bayesian
        )

        # Calculate confidence score (lower for metadata-only analysis)
        confidence_score = self._calculate_confidence_metadata(
            extracted_methods, is_probabilistic, is_bayesian, uncertainty_count, text
        )

        return {
            "is_probabilistic": is_probabilistic,
            "is_bayesian": is_bayesian,
            "keeney_decision_category": keeney_category,
            "extracted_methods": extracted_methods,
            "number_of_statements_about_uncertainty": uncertainty_count,
            "methods_category": methods_category,
            "confidence_score": confidence_score,
        }

    def _categorize_methods(
        self, methods: List[str], is_prob: bool, is_bayes: bool
    ) -> str:
        """Categorize the overall approach based on identified methods"""
        if is_bayes:
            return "Bayesian Decision Analysis"
        elif is_prob:
            return "Probabilistic Decision Analysis"
        elif any("multi" in method and "criteria" in method for method in methods):
            return "Multi-Criteria Decision Analysis"
        elif any("tree" in method or "influence" in method for method in methods):
            return "Decision Trees/Influence Diagrams"
        elif any("utility" in method or "value" in method for method in methods):
            return "Utility/Value-Based Analysis"
        elif any("fuzzy" in method or "rough" in method for method in methods):
            return "Fuzzy/Rough Set Methods"
        elif methods:
            return "Structured Decision Analysis"
        else:
            return "Unknown/Other"

    def _calculate_confidence_metadata(
        self,
        methods: List[str],
        is_prob: bool,
        is_bayes: bool,
        uncertainty_count: int,
        full_text: str,
    ) -> float:
        """Calculate confidence score for metadata-only analysis"""
        score = 0.0

        # Base score for found methods (lower weight since no full text)
        score += min(len(methods) * 0.15, 0.4)

        # Bonus for specific method types
        if is_bayes:
            score += 0.25
        elif is_prob:
            score += 0.15

        # Bonus for uncertainty mentions
        score += min(uncertainty_count * 0.03, 0.2)

        # Bonus for having abstract/keywords (more content to analyze)
        if len(full_text) > 200:
            score += 0.1
        elif len(full_text) > 100:
            score += 0.05

        # Penalty for metadata-only analysis
        score *= 0.8

        return min(score, 1.0)

    def process_entry(self, entry: Dict) -> Optional[DecisionPaper]:
        """Process a single BibTeX entry"""
        try:
            # Extract and clean basic information
            paper_id = entry.get("ID", "unknown")
            title = self.clean_bibtex_text(entry.get("title", ""))
            authors = self.clean_bibtex_text(entry.get("author", ""))
            year = entry.get("year")
            journal = self.clean_bibtex_text(
                entry.get("journal", entry.get("booktitle", ""))
            )
            abstract = self.clean_bibtex_text(entry.get("abstract", ""))
            keywords_str = self.clean_bibtex_text(entry.get("keywords", ""))
            doi = entry.get("doi", "")
            url = entry.get("url", "")

            # Parse keywords
            keywords = []
            if keywords_str:
                # Handle different keyword separators
                for sep in [",", ";", "\\n", "\n"]:
                    if sep in keywords_str:
                        keywords = [
                            k.strip() for k in keywords_str.split(sep) if k.strip()
                        ]
                        break
                if not keywords and keywords_str:
                    keywords = [keywords_str.strip()]

            # Try to convert year to int
            try:
                year = int(year) if year else None
            except (ValueError, TypeError):
                year = None

            # Combine available text for analysis
            analysis_text_parts = [title, abstract, " ".join(keywords)]
            analysis_text = " ".join(part for part in analysis_text_parts if part)

            # If very little text, skip or mark as low confidence
            if len(analysis_text.strip()) < 20:
                logger.warning(f"Very little text for analysis: {paper_id}")

            # Analyze the combined text
            analysis_results = self.analyze_metadata_content(analysis_text)

            # Create DecisionPaper object
            decision_paper = DecisionPaper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                keywords=keywords,
                doi=doi,
                url=url,
                **analysis_results,
            )

            return decision_paper

        except Exception as e:
            logger.error(f"Error processing entry {entry.get('ID', 'unknown')}: {e}")
            return None

    def process_all_files(self) -> List[DecisionPaper]:
        """Process all BibTeX files in the directory"""
        all_files = self.find_bibtex_files()
        all_results = []

        for bib_file in all_files:
            logger.info(f"Processing {bib_file}")
            entries = self.parse_bibtex_file(bib_file)

            for entry in entries:
                result = self.process_entry(entry)
                if result:
                    all_results.append(result)

        self.results = all_results
        logger.info(f"Processed {len(all_results)} total entries")
        return all_results

    def save_results(self, output_file: str = "extracted_methods_simple.json"):
        """Save results to JSON file"""
        results_dict = [result.dict() for result in self.results]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")

    def save_csv_results(self, output_file: str = "extracted_methods_simple.csv"):
        """Save results to CSV file for easy viewing in Excel"""
        try:
            import pandas as pd

            # Convert results to DataFrame
            df = pd.DataFrame([result.dict() for result in self.results])

            # Convert lists to strings for CSV
            if "extracted_methods" in df.columns:
                df["extracted_methods"] = df["extracted_methods"].apply(
                    lambda x: "; ".join(x) if isinstance(x, list) else str(x)
                )
            if "keywords" in df.columns:
                df["keywords"] = df["keywords"].apply(
                    lambda x: "; ".join(x) if isinstance(x, list) else str(x)
                )

            df.to_csv(output_file, index=False, encoding="utf-8")
            logger.info(f"CSV results saved to {output_file}")

        except ImportError:
            logger.warning("pandas not available - CSV export skipped")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of the analysis"""
        if not self.results:
            return {}

        total_papers = len(self.results)
        probabilistic_count = sum(1 for r in self.results if r.is_probabilistic)
        bayesian_count = sum(1 for r in self.results if r.is_bayesian)

        # Category distribution
        category_dist = {}
        for result in self.results:
            cat = result.methods_category
            category_dist[cat] = category_dist.get(cat, 0) + 1

        # Keeney category distribution
        keeney_dist = {}
        for result in self.results:
            cat = result.keeney_decision_category
            keeney_dist[cat] = keeney_dist.get(cat, 0) + 1

        # Most common methods
        method_count = {}
        for result in self.results:
            for method in result.extracted_methods:
                method_count[method] = method_count.get(method, 0) + 1

        # Year distribution
        year_dist = {}
        for result in self.results:
            if result.year:
                decade = f"{(result.year // 10) * 10}s"
                year_dist[decade] = year_dist.get(decade, 0) + 1

        summary = {
            "total_papers": total_papers,
            "probabilistic_papers": probabilistic_count,
            "bayesian_papers": bayesian_count,
            "probabilistic_percentage": round(
                (probabilistic_count / total_papers) * 100, 1
            )
            if total_papers > 0
            else 0,
            "bayesian_percentage": round((bayesian_count / total_papers) * 100, 1)
            if total_papers > 0
            else 0,
            "methods_category_distribution": category_dist,
            "keeney_category_distribution": keeney_dist,
            "top_methods": dict(
                sorted(method_count.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "year_distribution": dict(sorted(year_dist.items())),
            "average_uncertainty_statements": round(
                sum(r.number_of_statements_about_uncertainty for r in self.results)
                / total_papers,
                1,
            )
            if total_papers > 0
            else 0,
            "average_confidence_score": round(
                sum(r.confidence_score for r in self.results) / total_papers, 2
            )
            if total_papers > 0
            else 0,
            "papers_with_abstracts": sum(
                1 for r in self.results if r.abstract and len(r.abstract) > 50
            ),
            "papers_with_keywords": sum(
                1 for r in self.results if r.keywords and len(r.keywords) > 0
            ),
        }

        return summary

    def print_summary(self):
        """Print a summary of the analysis results"""
        summary = self.generate_summary_report()

        print("\n" + "=" * 70)
        print("SIMPLE BIBTEX METHODS EXTRACTION SUMMARY")
        print("=" * 70)

        if not summary:
            print("No results to summarize.")
            return

        print(f"Total Papers Analyzed: {summary['total_papers']}")
        print(f"Papers with Abstracts: {summary['papers_with_abstracts']}")
        print(f"Papers with Keywords: {summary['papers_with_keywords']}")
        print()
        print(
            f"Probabilistic Papers: {summary['probabilistic_papers']} ({summary['probabilistic_percentage']}%)"
        )
        print(
            f"Bayesian Papers: {summary['bayesian_papers']} ({summary['bayesian_percentage']}%)"
        )
        print(
            f"Average Uncertainty Statements: {summary['average_uncertainty_statements']}"
        )
        print(f"Average Confidence Score: {summary['average_confidence_score']}")

        print("\nMethods Category Distribution:")
        for category, count in sorted(
            summary["methods_category_distribution"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            percentage = round((count / summary["total_papers"]) * 100, 1)
            print(f"  {category}: {count} ({percentage}%)")

        print("\nKeeney Decision Analysis Categories:")
        for category, count in sorted(
            summary["keeney_category_distribution"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            percentage = round((count / summary["total_papers"]) * 100, 1)
            print(f"  {category}: {count} ({percentage}%)")

        if summary["top_methods"]:
            print("\nTop Methods Identified:")
            for method, count in list(summary["top_methods"].items())[:8]:
                print(f"  {method}: {count}")

        if summary["year_distribution"]:
            print("\nPublication Year Distribution:")
            for decade, count in summary["year_distribution"].items():
                print(f"  {decade}: {count}")

        print("=" * 70)


def main():
    """Main execution function"""
    # Initialize the extractor
    extractor = SimpleBibTeXExtractor("bib")

    # Process all files
    results = extractor.process_all_files()

    if not results:
        print("No results found. Please check your BibTeX files.")
        return

    # Save results in multiple formats
    extractor.save_results("extracted_methods_simple.json")
    extractor.save_csv_results("extracted_methods_simple.csv")

    # Print summary
    extractor.print_summary()

    # Save summary report
    summary = extractor.generate_summary_report()
    with open("methods_summary_report_simple.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: extracted_methods_simple.json")
    print(f"CSV results saved to: extracted_methods_simple.csv")
    print(f"Summary report saved to: methods_summary_report_simple.json")


if __name__ == "__main__":
    main()
