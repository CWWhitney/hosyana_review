#!/usr/bin/env python3
"""
BibTeX to CSV Methods Extractor

This script processes raw BibTeX files to create a CSV with:
- date: publication year
- bibref: bibliography reference key (e.g. whitneyReviewMethodsSupporting2023)
- method_category: categorized decision analysis method
- sentence: sentence containing the method description

Requirements:
    pip install bibtexparser pandas

Usage:
    python bibtex_csv_generator.py
"""

import csv
import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import bibtexparser
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BibTeXMethodsExtractor:
    """Extract decision analysis methods from BibTeX files for CSV output"""

    # Method categories with keywords
    METHOD_CATEGORIES = {
        "Probabilistic Methods": [
            "monte carlo",
            "simulation",
            "probability distribution",
            "stochastic",
            "random variable",
            "sampling",
            "likelihood",
            "probabilistic",
            "uncertainty quantification",
            "risk analysis",
            "sensitivity analysis",
            "bootstrap",
            "markov chain",
            "stochastic process",
        ],
        "Bayesian Methods": [
            "bayesian",
            "bayes",
            "posterior",
            "prior",
            "mcmc",
            "gibbs sampling",
            "metropolis",
            "belief network",
            "bayesian network",
            "credible interval",
            "bayesian inference",
            "hierarchical model",
            "conjugate prior",
            "posterior distribution",
            "bayes factor",
        ],
        "Multi-Criteria Decision Analysis": [
            "multi-criteria",
            "multicriteria",
            "mcda",
            "mcdm",
            "analytic hierarchy process",
            "analytic network process",
            "ahp",
            "anp",
            "topsis",
            "electre",
            "promethee",
            "outranking",
            "concordance analysis",
            "compromise programming",
            "goal programming",
            "weighted sum",
            "preference ranking",
        ],
        "Utility and Value Theory": [
            "utility theory",
            "expected utility",
            "multi-attribute utility",
            "multiattribute utility",
            "maut",
            "value function",
            "utility function",
            "von neumann",
            "morgenstern",
            "risk attitude",
            "certainty equivalent",
            "risk premium",
            "preference elicitation",
            "swing weighting",
            "direct rating",
        ],
        "Decision Trees and Networks": [
            "decision tree",
            "influence diagram",
            "decision network",
            "fault tree",
            "event tree",
            "bow-tie analysis",
            "decision node",
            "chance node",
            "value node",
            "rollback analysis",
            "decision analysis",
        ],
        "Game Theory": [
            "game theory",
            "nash equilibrium",
            "prisoner's dilemma",
            "zero-sum game",
            "cooperative game",
            "non-cooperative game",
            "strategic interaction",
            "minimax",
            "maximin",
            "dominant strategy",
            "auction theory",
        ],
        "Fuzzy Methods": [
            "fuzzy logic",
            "fuzzy set",
            "linguistic variable",
            "membership function",
            "fuzzy inference",
            "fuzzy rule",
            "defuzzification",
            "fuzzy number",
            "possibility theory",
            "fuzzy topsis",
            "fuzzy ahp",
        ],
        "Robust Decision Making": [
            "robust decision",
            "minimax regret",
            "robust optimization",
            "scenario planning",
            "worst-case analysis",
            "regret theory",
            "ambiguity aversion",
            "knightian uncertainty",
            "robust control",
            "info-gap",
        ],
        "Expert Systems and AI": [
            "expert system",
            "artificial intelligence",
            "machine learning",
            "neural network",
            "genetic algorithm",
            "evolutionary algorithm",
            "knowledge-based system",
            "rule-based system",
            "decision support system",
            "intelligent system",
        ],
        "Behavioral Decision Theory": [
            "behavioral economics",
            "prospect theory",
            "cognitive bias",
            "heuristic",
            "bounded rationality",
            "framing effect",
            "anchoring",
            "availability heuristic",
            "representativeness",
            "overconfidence",
            "loss aversion",
        ],
        "Real Options": [
            "real options",
            "option pricing",
            "black-scholes",
            "binomial tree",
            "option value",
            "investment timing",
            "flexibility value",
            "abandonment option",
            "expansion option",
            "switching option",
        ],
        "Delphi and Expert Judgment": [
            "delphi method",
            "expert judgment",
            "expert elicitation",
            "consensus building",
            "structured expert",
            "expert panel",
            "judgmental forecasting",
            "subjective probability",
            "expert opinion",
        ],
        "Optimization Methods": [
            "linear programming",
            "nonlinear programming",
            "integer programming",
            "dynamic programming",
            "multi-objective optimization",
            "pareto optimal",
            "optimization",
            "mathematical programming",
            "constraint programming",
        ],
    }

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

    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        if not text:
            return []

        # Split on sentence endings
        sentences = re.split(r"[.!?]+", text)

        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only keep substantial sentences
                clean_sentences.append(sentence)

        return clean_sentences

    def find_method_sentences(
        self, text: str, method_keywords: List[str]
    ) -> List[Tuple[str, int]]:
        """Find sentences containing method keywords with match scores"""
        sentences = self.extract_sentences(text)
        method_sentences = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = 0

            # Count keyword matches
            for keyword in method_keywords:
                if keyword in sentence_lower:
                    score += 1

            # Also look for general method indicators
            method_indicators = [
                "method",
                "approach",
                "technique",
                "model",
                "framework",
                "analysis",
                "algorithm",
                "procedure",
                "system",
                "process",
            ]

            for indicator in method_indicators:
                if indicator in sentence_lower:
                    score += 0.5

            if score > 0:
                method_sentences.append((sentence, score))

        # Sort by score and return
        method_sentences.sort(key=lambda x: x[1], reverse=True)
        return method_sentences

    def categorize_text(self, text: str) -> List[Tuple[str, str, float]]:
        """Categorize methods in text and return category, best sentence, confidence"""
        if not text:
            return []

        text_lower = text.lower()
        results = []

        for category, keywords in self.METHOD_CATEGORIES.items():
            # Check if any keywords from this category are present
            matches = sum(1 for keyword in keywords if keyword in text_lower)

            if matches > 0:
                # Find best sentence for this category
                method_sentences = self.find_method_sentences(text, keywords)

                if method_sentences:
                    best_sentence = method_sentences[0][0]  # Highest scoring sentence
                    confidence = min(matches * 0.2, 1.0)  # Simple confidence score
                    results.append((category, best_sentence, confidence))

        return results

    def process_bibtex_entry(self, entry: Dict) -> List[Dict]:
        """Process a single BibTeX entry"""
        bibref = entry.get("ID", "unknown")

        # Extract year
        year_str = entry.get("year", "")
        try:
            year = int(year_str)
        except (ValueError, TypeError):
            year = None

        # Extract and clean text fields
        title = self.clean_bibtex_text(entry.get("title", ""))
        abstract = self.clean_bibtex_text(entry.get("abstract", ""))
        keywords = self.clean_bibtex_text(entry.get("keywords", ""))

        # Combine text for analysis
        full_text = f"{title}. {abstract}. {keywords}".strip()

        # Categorize methods
        method_results = self.categorize_text(full_text)

        # Create output entries
        entries = []
        if method_results:
            for category, sentence, confidence in method_results:
                entries.append(
                    {
                        "date": year,
                        "bibref": bibref,
                        "method_category": category,
                        "sentence": sentence,
                        "confidence": confidence,
                        "title": title,
                    }
                )
        else:
            # If no methods found, still include entry with title
            entries.append(
                {
                    "date": year,
                    "bibref": bibref,
                    "method_category": "No specific method identified",
                    "sentence": title or "No description available",
                    "confidence": 0.0,
                    "title": title,
                }
            )

        return entries

    def process_bibtex_file(self, file_path: Path) -> List[Dict]:
        """Process a single BibTeX file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bib_database = bibtexparser.load(f)

            logger.info(
                f"Processing {file_path.name}: {len(bib_database.entries)} entries"
            )

            all_entries = []
            for entry in bib_database.entries:
                processed_entries = self.process_bibtex_entry(entry)
                all_entries.extend(processed_entries)

            return all_entries

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []

    def process_all_files(self) -> List[Dict]:
        """Process all BibTeX files in the raw directory"""
        bib_files = list(self.bib_raw_directory.glob("*.bib"))
        logger.info(f"Found {len(bib_files)} BibTeX files")

        all_results = []
        for bib_file in sorted(bib_files):
            results = self.process_bibtex_file(bib_file)
            all_results.extend(results)

        self.results = all_results
        logger.info(f"Total processed entries: {len(all_results)}")
        return all_results

    def save_csv(self, output_file: str = "methods_analysis.csv"):
        """Save results to CSV file with requested columns"""
        if not self.results:
            logger.warning("No results to save")
            return

        # Sort by date (year)
        sorted_results = sorted(self.results, key=lambda x: x["date"] or 0)

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            # Write CSV with exact columns requested
            fieldnames = ["date", "bibref", "method_category", "sentence"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for result in sorted_results:
                writer.writerow(
                    {
                        "date": result["date"] or "",
                        "bibref": result["bibref"],
                        "method_category": result["method_category"],
                        "sentence": result["sentence"],
                    }
                )

        logger.info(f"CSV saved to {output_file}")

    def generate_decade_summary(self) -> Dict:
        """Generate summary data for Sankey plot creation"""
        if not self.results:
            return {}

        # Count papers and methods by decade
        decade_data = defaultdict(
            lambda: {"total_papers": set(), "method_counts": defaultdict(int)}
        )

        for result in self.results:
            year = result["date"]
            if year:
                decade = f"{(year // 10) * 10}s"
                bibref = result["bibref"]
                method = result["method_category"]

                decade_data[decade]["total_papers"].add(bibref)
                if method != "No specific method identified":
                    decade_data[decade]["method_counts"][method] += 1

        # Convert to final format
        summary = {}
        for decade, data in decade_data.items():
            summary[decade] = {
                "total_papers": len(data["total_papers"]),
                "methods": dict(data["method_counts"]),
            }

        return summary

    def save_sankey_data(self, output_file: str = "sankey_data.json"):
        """Save data for Sankey plot creation"""
        sankey_data = self.generate_decade_summary()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sankey_data, f, indent=2)

        logger.info(f"Sankey data saved to {output_file}")

    def print_summary(self):
        """Print analysis summary"""
        if not self.results:
            logger.warning("No results to summarize")
            return

        total_entries = len(self.results)
        unique_papers = len(set(result["bibref"] for result in self.results))

        # Method category distribution
        category_counts = defaultdict(int)
        for result in self.results:
            category_counts[result["method_category"]] += 1

        # Decade distribution
        decade_summary = self.generate_decade_summary()

        print("\n" + "=" * 70)
        print("BIBTEX METHODS EXTRACTION SUMMARY")
        print("=" * 70)

        print(f"Total method instances: {total_entries}")
        print(f"Unique papers: {unique_papers}")

        print("\nTop Method Categories:")
        sorted_categories = sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        )
        for category, count in sorted_categories[:10]:
            percentage = (count / total_entries) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")

        print("\nDecade Summary:")
        for decade in sorted(decade_summary.keys()):
            data = decade_summary[decade]
            total = data["total_papers"]
            methods = len(data["methods"])
            print(f"  {decade}: {total} papers, {methods} method categories")

        print("=" * 70)


def main():
    """Main execution function"""
    extractor = BibTeXMethodsExtractor()

    # Process all files
    results = extractor.process_all_files()

    if not results:
        print("No results found. Please check your BibTeX files in bib/bib_raw/")
        return

    # Save main CSV output
    extractor.save_csv("methods_analysis.csv")

    # Save data for Sankey plots
    extractor.save_sankey_data("sankey_data.json")

    # Print summary
    extractor.print_summary()

    # Save detailed results as JSON
    with open("detailed_methods_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nOutput files created:")
    print(
        f"  - methods_analysis.csv (main CSV with date, bibref, method_category, sentence)"
    )
    print(f"  - sankey_data.json (decade/method data for Sankey plots)")
    print(f"  - detailed_methods_results.json (complete analysis results)")


if __name__ == "__main__":
    main()
