#!/usr/bin/env python3
"""
Automated Methods Extraction from BibTeX Collections

This script processes BibTeX files to extract decision analysis methods and categorize them
according to probabilistic, Bayesian, and Keeney decision analysis frameworks.

Requirements:
    pip install bibtexparser pydantic PyPDF2 python-docx requests beautifulsoup4

Usage:
    python bibtex_methods_extractor.py
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import bibtexparser
import PyPDF2
import requests
from bs4 import BeautifulSoup
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
    pdf_path: Optional[str] = Field(default=None, description="Path to full-text PDF")
    abstract: Optional[str] = Field(default=None, description="Paper abstract")
    keywords: List[str] = Field(default=[], description="Paper keywords")
    confidence_score: float = Field(
        default=0.0, description="Confidence in method extraction"
    )


@dataclass
class MethodsExtractor:
    """Main class for extracting methods from BibTeX collections"""

    # Decision analysis method keywords
    PROBABILISTIC_KEYWORDS = [
        "monte carlo",
        "simulation",
        "probability distribution",
        "stochastic",
        "random variable",
        "sampling",
        "likelihood",
        "probability",
        "uncertain",
        "risk analysis",
        "sensitivity analysis",
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
    ]

    KEENEY_CATEGORIES = {
        "value_focused": [
            "value focused",
            "value model",
            "utility function",
            "multi-attribute utility",
        ],
        "alternative_focused": [
            "alternative focused",
            "decision tree",
            "influence diagram",
        ],
        "prescriptive": ["prescriptive", "decision analysis", "decision support"],
        "descriptive": ["descriptive", "behavioral", "cognitive bias", "heuristic"],
    }

    DECISION_METHODS = [
        "decision tree",
        "influence diagram",
        "multi-criteria decision analysis",
        "mcda",
        "analytic hierarchy process",
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
        "scenario analysis",
        "robust decision making",
        "real options",
    ]

    UNCERTAINTY_PATTERNS = [
        r"uncertain(ty)?",
        r"risk",
        r"variability",
        r"ambiguity",
        r"confidence interval",
        r"standard error",
        r"variance",
        r"sensitivity",
        r"robust(ness)?",
        r"what.?if",
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

    def extract_pdf_path(self, entry: Dict) -> Optional[str]:
        """Extract PDF path from BibTeX entry"""
        if "file" in entry:
            file_string = entry["file"]
            path_part = file_string.split(":")[0].strip("{}")
            return (
                path_part
                if path_part and path_part != "No 'file' field found"
                else None
            )
        return None

    def read_pdf_content(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            if not os.path.exists(pdf_path):
                return ""

            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages[:10]:  # Read first 10 pages
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            return ""

    def analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content for decision analysis methods"""
        text_lower = text.lower()

        # Check for probabilistic methods
        is_probabilistic = any(
            keyword in text_lower for keyword in self.PROBABILISTIC_KEYWORDS
        )

        # Check for Bayesian methods
        is_bayesian = any(keyword in text_lower for keyword in self.BAYESIAN_KEYWORDS)

        # Determine Keeney category
        keeney_category = "unknown"
        for category, keywords in self.KEENEY_CATEGORIES.items():
            if any(keyword in text_lower for keyword in keywords):
                keeney_category = category
                break

        # Extract specific methods
        extracted_methods = []
        for method in self.DECISION_METHODS:
            if method in text_lower:
                extracted_methods.append(method)

        # Count uncertainty statements
        uncertainty_count = 0
        for pattern in self.UNCERTAINTY_PATTERNS:
            uncertainty_count += len(re.findall(pattern, text_lower, re.IGNORECASE))

        # Determine methods category
        methods_category = self._categorize_methods(
            extracted_methods, is_probabilistic, is_bayesian
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            extracted_methods, is_probabilistic, is_bayesian, uncertainty_count
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
        elif any("multi-criteria" in method or "mcda" in method for method in methods):
            return "Multi-Criteria Decision Analysis"
        elif any("tree" in method or "influence" in method for method in methods):
            return "Decision Trees/Influence Diagrams"
        elif methods:
            return "Structured Decision Analysis"
        else:
            return "Unknown/Other"

    def _calculate_confidence(
        self, methods: List[str], is_prob: bool, is_bayes: bool, uncertainty_count: int
    ) -> float:
        """Calculate confidence score for the analysis"""
        score = 0.0

        # Base score for found methods
        score += len(methods) * 0.1

        # Bonus for specific method types
        if is_bayes:
            score += 0.3
        elif is_prob:
            score += 0.2

        # Bonus for uncertainty mentions
        score += min(uncertainty_count * 0.05, 0.3)

        return min(score, 1.0)

    def process_entry(self, entry: Dict) -> Optional[DecisionPaper]:
        """Process a single BibTeX entry"""
        try:
            # Extract basic information
            paper_id = entry.get("ID", "unknown")
            title = entry.get("title", "").strip("{}")
            authors = entry.get("author", "").strip("{}")
            year = entry.get("year")
            journal = entry.get("journal", entry.get("booktitle", "")).strip("{}")
            abstract = entry.get("abstract", "").strip("{}")
            keywords_str = entry.get("keywords", "").strip("{}")
            keywords = (
                [k.strip() for k in keywords_str.split(",") if k.strip()]
                if keywords_str
                else []
            )

            # Try to convert year to int
            try:
                year = int(year) if year else None
            except (ValueError, TypeError):
                year = None

            # Get PDF path and content
            pdf_path = self.extract_pdf_path(entry)

            # Combine available text for analysis
            analysis_text = f"{title} {abstract} {' '.join(keywords)}"

            # If PDF is available, add its content
            if pdf_path:
                pdf_content = self.read_pdf_content(pdf_path)
                analysis_text += f" {pdf_content}"

            # Analyze the combined text
            analysis_results = self.analyze_text_content(analysis_text)

            # Create DecisionPaper object
            decision_paper = DecisionPaper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                keywords=keywords,
                pdf_path=pdf_path,
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

    def save_results(self, output_file: str = "extracted_methods.json"):
        """Save results to JSON file"""
        results_dict = [result.dict() for result in self.results]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")

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

        summary = {
            "total_papers": total_papers,
            "probabilistic_papers": probabilistic_count,
            "bayesian_papers": bayesian_count,
            "probabilistic_percentage": round(
                (probabilistic_count / total_papers) * 100, 1
            ),
            "bayesian_percentage": round((bayesian_count / total_papers) * 100, 1),
            "methods_category_distribution": category_dist,
            "keeney_category_distribution": keeney_dist,
            "top_methods": dict(
                sorted(method_count.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "average_uncertainty_statements": round(
                sum(r.number_of_statements_about_uncertainty for r in self.results)
                / total_papers,
                1,
            ),
            "average_confidence_score": round(
                sum(r.confidence_score for r in self.results) / total_papers, 2
            ),
        }

        return summary

    def print_summary(self):
        """Print a summary of the analysis results"""
        summary = self.generate_summary_report()

        print("\n" + "=" * 60)
        print("BIBTEX METHODS EXTRACTION SUMMARY")
        print("=" * 60)

        if not summary:
            print("No results to summarize.")
            return

        print(f"Total Papers Analyzed: {summary['total_papers']}")
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
        for category, count in summary["methods_category_distribution"].items():
            print(f"  {category}: {count}")

        print("\nKeeney Decision Analysis Categories:")
        for category, count in summary["keeney_category_distribution"].items():
            print(f"  {category}: {count}")

        print("\nTop Methods Identified:")
        for method, count in list(summary["top_methods"].items())[:5]:
            print(f"  {method}: {count}")

        print("=" * 60)


def main():
    """Main execution function"""
    # Initialize the extractor
    extractor = MethodsExtractor("bib")

    # Process all files
    results = extractor.process_all_files()

    # Save results
    extractor.save_results("extracted_methods.json")

    # Print summary
    extractor.print_summary()

    # Save summary report
    summary = extractor.generate_summary_report()
    with open("methods_summary_report.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: extracted_methods.json")
    print(f"Summary report saved to: methods_summary_report.json")


if __name__ == "__main__":
    main()
