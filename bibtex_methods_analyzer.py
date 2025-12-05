#!/usr/bin/env python3
"""
BibTeX Methods Analyzer for Decision Analysis Research

This script processes raw BibTeX files to:
1. Extract method-related sentences and categorize them
2. Generate CSV with date, bibref, method category, and related sentences
3. Create data for Sankey plots showing method evolution by decade

Requirements:
    pip install bibtexparser pandas plotly kaleido

Usage:
    python bibtex_methods_analyzer.py
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
import plotly.express as px
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MethodsAnalyzer:
    """Analyzer for extracting decision analysis methods from BibTeX files"""

    # Enhanced method categories with specific keywords
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
            "variance",
            "bootstrap",
            "markov chain",
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
        ],
        "Multi-Criteria Decision Analysis": [
            "multi-criteria",
            "multicriteria",
            "mcda",
            "mcdm",
            "analytic hierarchy process",
            "ahp",
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
            "value function",
            "utility function",
            "von neumann",
            "morgenstern",
            "risk attitude",
            "certainty equivalent",
            "risk premium",
            "preference elicitation",
            "swing weighting",
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
        ],
        "Expert Systems and AI": [
            "expert system",
            "artificial intelligence",
            "machine learning",
            "neural network",
            "genetic algorithm",
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
        ],
    }

    # Sentence patterns that often contain method descriptions
    METHOD_SENTENCE_PATTERNS = [
        r"[^.!?]*(?:method|approach|technique|model|framework|analysis|algorithm)[^.!?]*[.!?]",
        r"[^.!?]*(?:we use|we apply|we employ|we implement|using|applying|based on)[^.!?]*[.!?]",
        r"[^.!?]*(?:decision|choice|selection|evaluation|assessment)[^.!?]*[.!?]",
        r"[^.!?]*(?:uncertainty|risk|probability|stochastic)[^.!?]*[.!?]",
        r"[^.!?]*(?:optimization|maximize|minimize|optimal)[^.!?]*[.!?]",
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

    def extract_bibref(self, entry: Dict) -> str:
        """Extract bibliography reference key (e.g., whitneyReviewMethodsSupporting2023)"""
        return entry.get("ID", "unknown")

    def extract_year_decade(self, entry: Dict) -> Tuple[Optional[int], Optional[str]]:
        """Extract year and decade from entry"""
        year_str = entry.get("year", "")
        try:
            year = int(year_str)
            decade = f"{(year // 10) * 10}s"
            return year, decade
        except (ValueError, TypeError):
            return None, None

    def find_method_sentences(self, text: str) -> List[str]:
        """Find sentences that likely contain method descriptions"""
        if not text:
            return []

        sentences = []
        text_lower = text.lower()

        # Split text into sentences
        sentence_endings = re.split(r"[.!?]+", text)

        for sentence in sentence_endings:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue

            sentence_lower = sentence.lower()

            # Check if sentence contains method-related keywords
            contains_method = False
            for category, keywords in self.METHOD_CATEGORIES.items():
                if any(keyword in sentence_lower for keyword in keywords):
                    contains_method = True
                    break

            # Also check for general method indicators
            method_indicators = [
                "method",
                "approach",
                "technique",
                "model",
                "framework",
                "analysis",
                "algorithm",
                "procedure",
                "process",
                "system",
                "we use",
                "we apply",
                "we employ",
                "using",
                "applying",
                "based on",
                "implemented",
                "developed",
            ]

            if not contains_method:
                contains_method = any(
                    indicator in sentence_lower for indicator in method_indicators
                )

            if contains_method:
                sentences.append(sentence.strip())

        return sentences

    def categorize_methods(self, text: str) -> List[Tuple[str, float]]:
        """Categorize methods found in text with confidence scores"""
        if not text:
            return []

        text_lower = text.lower()
        found_categories = []

        for category, keywords in self.METHOD_CATEGORIES.items():
            matches = 0
            total_keyword_occurrences = 0

            for keyword in keywords:
                keyword_count = text_lower.count(keyword)
                if keyword_count > 0:
                    matches += 1
                    total_keyword_occurrences += keyword_count

            if matches > 0:
                # Calculate confidence based on number of matching keywords and frequency
                confidence = min(
                    (matches * 0.2) + (total_keyword_occurrences * 0.1), 1.0
                )
                found_categories.append((category, confidence))

        # Sort by confidence
        found_categories.sort(key=lambda x: x[1], reverse=True)
        return found_categories

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
                bibref = self.extract_bibref(entry)
                year, decade = self.extract_year_decade(entry)

                # Combine title, abstract, and keywords for analysis
                title = self.clean_bibtex_text(entry.get("title", ""))
                abstract = self.clean_bibtex_text(entry.get("abstract", ""))
                keywords = self.clean_bibtex_text(entry.get("keywords", ""))

                full_text = f"{title}. {abstract}. {keywords}".strip()

                # Find method-related sentences
                method_sentences = self.find_method_sentences(full_text)

                # Categorize methods
                method_categories = self.categorize_methods(full_text)

                # Create entry for each found category
                if method_categories:
                    for category, confidence in method_categories:
                        # Find the most relevant sentence for this category
                        relevant_sentence = ""
                        best_score = 0

                        category_keywords = self.METHOD_CATEGORIES.get(category, [])

                        for sentence in method_sentences:
                            sentence_lower = sentence.lower()
                            score = sum(
                                1
                                for keyword in category_keywords
                                if keyword in sentence_lower
                            )
                            if score > best_score:
                                best_score = score
                                relevant_sentence = sentence

                        # If no specific sentence found, use the first method sentence
                        if not relevant_sentence and method_sentences:
                            relevant_sentence = method_sentences[0]

                        results.append(
                            {
                                "date": year,
                                "decade": decade,
                                "bibref": bibref,
                                "method_category": category,
                                "sentence": relevant_sentence,
                                "confidence": confidence,
                                "title": title,
                                "source_file": file_path.name,
                            }
                        )
                else:
                    # Even if no specific methods found, include the entry
                    results.append(
                        {
                            "date": year,
                            "decade": decade,
                            "bibref": bibref,
                            "method_category": "No specific method identified",
                            "sentence": method_sentences[0]
                            if method_sentences
                            else title,
                            "confidence": 0.0,
                            "title": title,
                            "source_file": file_path.name,
                        }
                    )

            return results

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []

    def process_all_files(self) -> List[Dict]:
        """Process all BibTeX files in the raw directory"""
        bib_files = list(self.bib_raw_directory.glob("*.bib"))
        logger.info(f"Found {len(bib_files)} BibTeX files")

        all_results = []
        for bib_file in bib_files:
            results = self.process_bibtex_file(bib_file)
            all_results.extend(results)

        self.results = all_results
        logger.info(f"Total processed entries: {len(all_results)}")
        return all_results

    def save_csv(self, output_file: str = "methods_analysis.csv"):
        """Save results to CSV file"""
        if not self.results:
            logger.warning("No results to save")
            return

        # Sort by date
        sorted_results = sorted(self.results, key=lambda x: x["date"] or 0)

        with open(output_file, "w", newline="", encoding="utf-8") as f:
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

    def prepare_sankey_data(self) -> Dict:
        """Prepare data for Sankey plots showing method evolution by decade"""
        if not self.results:
            return {}

        # Count papers by decade
        decade_counts = defaultdict(int)
        decade_method_counts = defaultdict(lambda: defaultdict(int))

        # Track unique papers per decade (to avoid double counting)
        decade_papers = defaultdict(set)

        for result in self.results:
            decade = result["decade"]
            bibref = result["bibref"]
            method_category = result["method_category"]

            if decade and decade != "None":
                decade_papers[decade].add(bibref)
                if method_category != "No specific method identified":
                    decade_method_counts[decade][method_category] += 1

        # Count total papers per decade
        for decade, papers in decade_papers.items():
            decade_counts[decade] = len(papers)

        # Prepare data for visualization
        sankey_data = {
            "decade_totals": dict(decade_counts),
            "decade_methods": dict(decade_method_counts),
            "method_categories": list(self.METHOD_CATEGORIES.keys()),
        }

        return sankey_data

    def create_sankey_plot(self, output_file: str = "methods_sankey.html"):
        """Create Sankey diagram showing method evolution"""
        sankey_data = self.prepare_sankey_data()

        if not sankey_data:
            logger.warning("No data available for Sankey plot")
            return

        # Prepare nodes and links for Sankey diagram
        nodes = []
        links = []
        node_colors = []

        # Color schemes
        decade_colors = px.colors.qualitative.Set3
        method_colors = px.colors.qualitative.Plotly

        # Add decade nodes
        decades = sorted(sankey_data["decade_totals"].keys())
        decade_to_index = {}

        for i, decade in enumerate(decades):
            nodes.append(f"{decade}<br>({sankey_data['decade_totals'][decade]} papers)")
            decade_to_index[decade] = i
            node_colors.append(decade_colors[i % len(decade_colors)])

        # Add method category nodes
        method_categories = sankey_data["method_categories"]
        method_to_index = {}

        for i, method in enumerate(method_categories):
            nodes.append(method)
            method_to_index[method] = len(decades) + i
            node_colors.append(method_colors[i % len(method_colors)])

        # Create links from decades to methods
        for decade in decades:
            decade_idx = decade_to_index[decade]
            methods_in_decade = sankey_data["decade_methods"].get(decade, {})

            for method, count in methods_in_decade.items():
                if method in method_to_index and count > 0:
                    method_idx = method_to_index[method]
                    links.append(
                        {
                            "source": decade_idx,
                            "target": method_idx,
                            "value": count,
                            "label": f"{decade} → {method}: {count}",
                        }
                    )

        # Create Sankey diagram
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=nodes,
                        color=node_colors,
                    ),
                    link=dict(
                        source=[link["source"] for link in links],
                        target=[link["target"] for link in links],
                        value=[link["value"] for link in links],
                        label=[link["label"] for link in links],
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="Evolution of Decision Analysis Methods by Decade",
            font_size=10,
            width=1200,
            height=800,
        )

        # Save HTML file
        fig.write_html(output_file)
        logger.info(f"Sankey plot saved to {output_file}")

        # Also save as JSON for further analysis
        with open("sankey_data.json", "w") as f:
            json.dump(sankey_data, f, indent=2)

    def create_summary_statistics(self) -> Dict:
        """Create summary statistics of the analysis"""
        if not self.results:
            return {}

        total_entries = len(self.results)
        unique_papers = len(set(result["bibref"] for result in self.results))

        # Method category distribution
        category_counts = defaultdict(int)
        for result in self.results:
            category_counts[result["method_category"]] += 1

        # Decade distribution
        decade_counts = defaultdict(int)
        decade_papers = defaultdict(set)
        for result in self.results:
            if result["decade"]:
                decade_counts[result["decade"]] += 1
                decade_papers[result["decade"]].add(result["bibref"])

        # High confidence methods
        high_confidence = [r for r in self.results if r["confidence"] > 0.5]

        summary = {
            "total_method_instances": total_entries,
            "unique_papers": unique_papers,
            "method_categories": dict(category_counts),
            "decade_distribution": {
                decade: len(papers) for decade, papers in decade_papers.items()
            },
            "high_confidence_methods": len(high_confidence),
            "average_confidence": sum(r["confidence"] for r in self.results)
            / total_entries
            if total_entries > 0
            else 0,
        }

        return summary

    def print_summary(self):
        """Print analysis summary"""
        summary = self.create_summary_statistics()

        print("\n" + "=" * 70)
        print("BIBTEX METHODS ANALYSIS SUMMARY")
        print("=" * 70)

        print(f"Total method instances found: {summary['total_method_instances']}")
        print(f"Unique papers analyzed: {summary['unique_papers']}")
        print(f"High confidence methods: {summary['high_confidence_methods']}")
        print(f"Average confidence score: {summary['average_confidence']:.2f}")

        print("\nMethod Categories Distribution:")
        sorted_categories = sorted(
            summary["method_categories"].items(), key=lambda x: x[1], reverse=True
        )
        for category, count in sorted_categories[:10]:
            percentage = (count / summary["total_method_instances"]) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")

        print("\nDecade Distribution (unique papers):")
        sorted_decades = sorted(summary["decade_distribution"].items())
        for decade, count in sorted_decades:
            print(f"  {decade}: {count} papers")

        print("=" * 70)


def main():
    """Main execution function"""
    analyzer = MethodsAnalyzer()

    # Process all files
    results = analyzer.process_all_files()

    if not results:
        print("No results found. Please check your BibTeX files.")
        return

    # Save CSV
    analyzer.save_csv("methods_analysis.csv")

    # Create Sankey plot
    analyzer.create_sankey_plot("methods_evolution_sankey.html")

    # Print summary
    analyzer.print_summary()

    # Save detailed results
    with open("detailed_methods_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nFiles created:")
    print(f"  - methods_analysis.csv (main results)")
    print(f"  - methods_evolution_sankey.html (interactive Sankey plot)")
    print(f"  - sankey_data.json (data for Sankey plot)")
    print(f"  - detailed_methods_analysis.json (full analysis results)")


if __name__ == "__main__":
    main()
