#!/usr/bin/env python3
"""
Full-Text PDF Analyzer with Web Fallback
Extracts decision support methods from PDF files and web sources

This script:
1. Reads BibTeX files to get PDF paths and metadata
2. Attempts to extract text from local PDF files
3. Falls back to web scraping if PDF is missing
4. Performs comprehensive method detection on full text
5. Generates detailed CSV with confidence scores

Requirements:
    pip install PyPDF2 pdfplumber requests beautifulsoup4 selenium webdriver-manager
"""

import csv
import json
import logging
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import bibtexparser
import pdfplumber
import PyPDF2
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("pdf_analysis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class FullTextAnalyzer:
    """Comprehensive full-text analysis with PDF and web access"""

    # Comprehensive method categories with extensive keywords
    METHOD_CATEGORIES = {
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
            "decision support system",
            "DSS",
            "MCDM",
            "MCDA",
        ],
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
            "regulatory impact",
            "evidence-based policy",
        ],
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
            "probabilistic risk",
            "quantitative risk",
            "variability analysis",
            "sensitivity analysis",
            "scenario analysis",
            "what-if analysis",
            "robustness analysis",
            "confidence interval",
            "prediction interval",
            "error propagation",
            "measurement uncertainty",
            "forecast uncertainty",
        ],
        "STAKEHOLDER_EXPERT": [
            "stakeholder analysis",
            "stakeholder engagement",
            "stakeholder involvement",
            "stakeholder participation",
            "stakeholder consultation",
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
            "collaborative decision",
            "group decision",
            "consensus building",
            "multi-stakeholder",
            "delphi method",
            "nominal group",
            "focus group",
            "structured interview",
            "knowledge elicitation",
            "preference elicitation",
            "participatory research",
            "co-design",
        ],
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
            "dynamic model",
            "optimization model",
            "network model",
            "spatial model",
            "integrated model",
            "ensemble model",
            "meta-model",
            "surrogate model",
            "model validation",
            "model calibration",
        ],
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
            "probabilistic",
            "probability",
            "stochastic",
            "probability distribution",
            "probability model",
            "stochastic process",
            "random variable",
            "likelihood function",
            "maximum likelihood",
            "bootstrap",
            "statistical inference",
            "hypothesis testing",
        ],
        "COMPUTER_ASSISTED": [
            "computer assisted",
            "computer-assisted",
            "computer aided",
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
            "web-based",
            "online",
            "cloud-based",
            "dashboard",
            "visualization",
            "interactive",
            "software tool",
            "digital platform",
        ],
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
            "prediction accuracy",
            "forecast accuracy",
            "diagnostic accuracy",
            "sensitivity",
            "specificity",
            "area under curve",
            "receiver operating characteristic",
        ],
        "MULTI_CRITERIA": [
            "multi-criteria",
            "multicriteria",
            "multiple criteria",
            "mcda",
            "mcdm",
            "analytic hierarchy process",
            "ahp",
            "analytic network process",
            "anp",
            "topsis",
            "electre",
            "promethee",
            "vikor",
            "outranking",
            "concordance",
            "preference ranking",
            "multi-attribute",
            "multi-objective",
            "goal programming",
            "compromise programming",
            "utility function",
            "value function",
            "scoring method",
        ],
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
            "dynamic programming",
            "stochastic programming",
            "robust optimization",
            "multi-objective optimization",
            "pareto optimal",
            "evolutionary algorithm",
            "genetic algorithm",
            "particle swarm",
            "simulated annealing",
            "tabu search",
            "gradient descent",
            "simplex method",
            "branch and bound",
        ],
        "ECONOMIC_EVALUATION": [
            "cost-effectiveness",
            "cost-benefit",
            "cost-utility",
            "economic evaluation",
            "health economics",
            "budget impact",
            "return on investment",
            "net present value",
            "cost per qaly",
            "quality adjusted life years",
            "incremental cost-effectiveness",
            "willingness to pay",
            "contingent valuation",
            "discrete choice experiment",
            "conjoint analysis",
            "benefit transfer",
            "meta-analysis",
        ],
        "GAME_THEORY": [
            "game theory",
            "strategic",
            "nash equilibrium",
            "dominant strategy",
            "prisoner dilemma",
            "bargaining",
            "negotiation",
            "auction theory",
            "mechanism design",
            "cooperative game",
            "behavioral game theory",
            "evolutionary game theory",
            "strategic interaction",
        ],
        "BEHAVIORAL_PSYCHOLOGY": [
            "behavioral",
            "behaviour",
            "psychology",
            "cognitive",
            "heuristic",
            "bias",
            "prospect theory",
            "bounded rationality",
            "anchoring",
            "availability heuristic",
            "framing effect",
            "loss aversion",
            "overconfidence",
            "cognitive bias",
            "decision psychology",
            "human factors",
        ],
        "SYSTEMS_COMPLEXITY": [
            "systems analysis",
            "systems thinking",
            "complex system",
            "socio-technical system",
            "socio-ecological system",
            "feedback",
            "emergence",
            "complexity science",
            "network analysis",
            "resilience",
            "adaptability",
            "sustainability",
            "adaptive management",
            "ecosystem",
            "supply chain",
        ],
        "FORECASTING_PREDICTION": [
            "forecasting",
            "prediction",
            "predictive",
            "forecast",
            "projection",
            "scenario",
            "time series",
            "trend analysis",
            "regression",
            "neural network forecasting",
            "ensemble forecasting",
            "judgmental forecasting",
            "forecast accuracy",
        ],
        "EVALUATION_ASSESSMENT": [
            "evaluation",
            "assessment",
            "appraisal",
            "review",
            "audit",
            "monitoring",
            "performance measurement",
            "impact evaluation",
            "program evaluation",
            "comparative analysis",
            "benchmarking",
            "effectiveness",
            "efficacy",
        ],
    }

    def __init__(self, bib_raw_directory: str = "bib/bib_raw"):
        self.bib_raw_directory = Path(bib_raw_directory)
        self.results = []
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def clean_bibtex_text(self, text: str) -> str:
        """Clean BibTeX text by removing braces and LaTeX commands"""
        if not text:
            return ""
        text = text.strip("{}")
        text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)
        text = re.sub(r"[\{\}]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_pdf_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                max_pages = min(20, len(pdf_reader.pages))  # First 20 pages
                for i in range(max_pages):
                    try:
                        page_text = pdf_reader.pages[i].extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.debug(f"Error reading page {i}: {e}")
                return text
        except Exception as e:
            logger.debug(f"PyPDF2 extraction failed: {e}")
            return ""

    def extract_pdf_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (better for complex layouts)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                max_pages = min(20, len(pdf.pages))  # First 20 pages
                for i in range(max_pages):
                    try:
                        page = pdf.pages[i]
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.debug(f"Error reading page {i} with pdfplumber: {e}")
            return text
        except Exception as e:
            logger.debug(f"pdfplumber extraction failed: {e}")
            return ""

    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        if not os.path.exists(pdf_path):
            logger.debug(f"PDF not found: {pdf_path}")
            return ""

        # Try pdfplumber first (usually better)
        text = self.extract_pdf_text_pdfplumber(pdf_path)
        if text and len(text.strip()) > 100:
            logger.info(
                f"Successfully extracted {len(text)} characters with pdfplumber"
            )
            return text

        # Fallback to PyPDF2
        text = self.extract_pdf_text_pypdf2(pdf_path)
        if text and len(text.strip()) > 100:
            logger.info(f"Successfully extracted {len(text)} characters with PyPDF2")
            return text

        logger.warning(f"No usable text extracted from PDF: {pdf_path}")
        return ""

    def scrape_web_content(self, url: str) -> str:
        """Scrape content from web URL"""
        if not url or not url.startswith(("http://", "https://")):
            return ""

        try:
            logger.info(f"Attempting to scrape: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find main content areas
            content_selectors = [
                "article",
                "main",
                ".content",
                "#content",
                ".abstract",
                ".summary",
                ".article-body",
                "p",
                "div.text",
                "section",
            ]

            text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    element_text = element.get_text()
                    if len(element_text) > 50:  # Skip very short elements
                        text += element_text + "\n"

            # Clean up the text
            text = re.sub(r"\s+", " ", text)
            text = text.strip()

            if len(text) > 200:
                logger.info(f"Successfully scraped {len(text)} characters from web")
                return text[:10000]  # Limit to first 10k characters

        except Exception as e:
            logger.warning(f"Web scraping failed for {url}: {e}")

        return ""

    def get_pdf_path_from_entry(self, entry: Dict) -> Optional[str]:
        """Extract PDF path from BibTeX entry"""
        file_field = entry.get("file", "")
        if not file_field:
            return None

        # Parse the file field (format: path:type or just path)
        file_parts = file_field.split(":")
        if file_parts:
            pdf_path = file_parts[0].strip("{}")
            if pdf_path and not pdf_path.startswith("Attachment"):
                # Convert relative paths or handle different formats
                if pdf_path.startswith("/"):
                    return pdf_path
                elif "Zotero" in pdf_path or "storage" in pdf_path:
                    return pdf_path

        return None

    def get_urls_from_entry(self, entry: Dict) -> List[str]:
        """Extract URLs from BibTeX entry for web scraping"""
        urls = []

        # Check various URL fields
        url_fields = ["url", "doi", "link"]
        for field in url_fields:
            url = entry.get(field, "")
            if url:
                url = self.clean_bibtex_text(url)
                if url.startswith("http"):
                    urls.append(url)
                elif field == "doi":
                    # Convert DOI to URL
                    if not url.startswith("http"):
                        urls.append(f"https://doi.org/{url}")

        return urls

    def analyze_text_for_methods(self, text: str) -> Dict:
        """Analyze text for decision support methods"""
        if not text:
            return self._empty_methods_dict()

        text_lower = text.lower()
        results = {}
        detected_methods = []
        method_details = []
        total_confidence = 0.0

        # Analyze each method category
        for category, keywords in self.METHOD_CATEGORIES.items():
            matches = 0
            keyword_occurrences = 0
            matched_keywords = []
            example_sentences = []

            for keyword in keywords:
                if keyword in text_lower:
                    matches += 1
                    keyword_count = text_lower.count(keyword)
                    keyword_occurrences += keyword_count
                    matched_keywords.append(keyword)

                    # Find example sentences containing this keyword
                    sentences = re.split(r"[.!?]+", text)
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 20:
                            example_sentences.append(sentence.strip())
                            if len(example_sentences) >= 2:  # Limit examples
                                break

            # Binary indicator
            has_method = matches > 0
            results[category] = 1 if has_method else 0

            if has_method:
                # Calculate confidence with full-text bonus
                base_confidence = min(
                    (matches * 0.15) + (keyword_occurrences * 0.05), 0.8
                )
                diversity_bonus = min(len(set(matched_keywords)) * 0.1, 0.3)
                fulltext_bonus = 0.2  # Bonus for having full text
                confidence = min(
                    base_confidence + diversity_bonus + fulltext_bonus, 1.0
                )

                detected_methods.append(f"{category}({confidence:.2f})")
                method_details.append(
                    {
                        "category": category,
                        "confidence": confidence,
                        "keywords_found": matched_keywords[:5],  # Top 5 keywords
                        "example_sentences": example_sentences[:2],  # Top 2 examples
                    }
                )
                total_confidence += confidence

        # Count uncertainty statements with expanded patterns
        uncertainty_patterns = [
            r"uncertain(ty)?",
            r"risk\b",
            r"variability",
            r"confidence interval",
            r"monte carlo",
            r"simulation",
            r"probability",
            r"stochastic",
            r"sensitivity",
            r"robust",
            r"scenario",
            r"what.?if",
        ]

        uncertainty_count = 0
        for pattern in uncertainty_patterns:
            uncertainty_count += len(re.findall(pattern, text_lower, re.IGNORECASE))

        # Overall results
        results.update(
            {
                "DETECTED_METHODS": "; ".join(detected_methods)
                if detected_methods
                else "NONE",
                "HAS_METHODS": 1 if detected_methods else 0,
                "CONFIDENCE": round(total_confidence / len(self.METHOD_CATEGORIES), 3)
                if detected_methods
                else 0.0,
                "UNCERTAINTY_STATEMENTS": uncertainty_count,
                "TEXT_LENGTH": len(text),
                "METHOD_DETAILS": json.dumps(method_details) if method_details else "",
            }
        )

        return results

    def _empty_methods_dict(self) -> Dict:
        """Return empty methods dictionary"""
        results = {category: 0 for category in self.METHOD_CATEGORIES.keys()}
        results.update(
            {
                "DETECTED_METHODS": "NONE",
                "HAS_METHODS": 0,
                "CONFIDENCE": 0.0,
                "UNCERTAINTY_STATEMENTS": 0,
                "TEXT_LENGTH": 0,
                "METHOD_DETAILS": "",
            }
        )
        return results

    def process_bibtex_entry(self, entry: Dict) -> Dict:
        """Process a single BibTeX entry with full-text analysis"""
        # Extract basic metadata
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
            for sep in [",", ";", "|", "\n"]:
                if sep in keywords_str:
                    keywords = [k.strip() for k in keywords_str.split(sep) if k.strip()]
                    break
            if not keywords and keywords_str:
                keywords = [keywords_str.strip()]

        # Start with metadata
        metadata_text = f"{title} {title} {title}. {abstract} {abstract}. {' '.join(keywords)}. {journal}"

        # Try to get full text from PDF
        full_text = ""
        pdf_status = "no_pdf"

        pdf_path = self.get_pdf_path_from_entry(entry)
        if pdf_path:
            full_text = self.extract_pdf_text(pdf_path)
            if full_text:
                pdf_status = "pdf_success"
                logger.info(f"PDF extracted for {bibref}: {len(full_text)} chars")
            else:
                pdf_status = "pdf_failed"

        # If no PDF text, try web scraping
        if not full_text:
            urls = self.get_urls_from_entry(entry)
            for url in urls[:2]:  # Try up to 2 URLs
                web_text = self.scrape_web_content(url)
                if web_text:
                    full_text = web_text
                    pdf_status = "web_scraped"
                    logger.info(f"Web scraped for {bibref}: {len(full_text)} chars")
                    break
                time.sleep(1)  # Be respectful to servers

        # Combine metadata with full text (weight metadata heavily)
        if full_text:
            analysis_text = metadata_text + " " + full_text
        else:
            analysis_text = metadata_text
            pdf_status = "metadata_only"

        # Analyze for methods
        methods_results = self.analyze_text_for_methods(analysis_text)

        # Create comprehensive result
        result = {
            "TITLE": title,
            "YEAR": year or "",
            "BIBREF": bibref,
            "AUTHORS": authors,
            "JOURNAL": journal,
            "ABSTRACT": abstract,
            "KEYWORDS": "; ".join(keywords),
            "PDF_STATUS": pdf_status,
            "PDF_PATH": pdf_path or "",
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
            for i, entry in enumerate(bib_database.entries):
                logger.info(
                    f"Processing entry {i + 1}/{len(bib_database.entries)}: {entry.get('ID', 'unknown')}"
                )
                result = self.process_bibtex_entry(entry)
                results.append(result)

                # Progress logging
                if (i + 1) % 50 == 0:
                    logger.info(
                        f"Completed {i + 1}/{len(bib_database.entries)} entries"
                    )

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

    def save_comprehensive_csv(
        self, output_file: str = "fulltext_methods_analysis.csv"
    ):
        """Save comprehensive CSV with full-text analysis results"""
        if not self.results:
            logger.warning("No results to save")
            return

        # Sort by year, then by confidence (highest first)
        sorted_results = sorted(
            self.results, key=lambda x: (x["YEAR"] or 0, -x["CONFIDENCE"], x["TITLE"])
        )

        # Define columns
        columns = (
            [
                "TITLE",
                "YEAR",
                "BIBREF",
                "AUTHORS",
                "JOURNAL",
                "PDF_STATUS",
                "TEXT_LENGTH",
                "DETECTED_METHODS",
                "CONFIDENCE",
                "HAS_METHODS",
                "UNCERTAINTY_STATEMENTS",
            ]
            + list(self.METHOD_CATEGORIES.keys())
            + ["ABSTRACT", "KEYWORDS", "PDF_PATH", "METHOD_DETAILS"]
        )

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for result in sorted_results:
                row = {col: result.get(col, "") for col in columns}
                writer.writerow(row)

        logger.info(f"Full-text CSV saved to {output_file}")

    def generate_analysis_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        if not self.results:
            return {}

        total_papers = len(self.results)
        papers_with_methods = sum(1 for r in self.results if r["HAS_METHODS"] == 1)

        # PDF access statistics
        pdf_stats = defaultdict(int)
        for result in self.results:
            pdf_stats[result["PDF_STATUS"]] += 1

        # High confidence papers
        high_confidence = [r for r in self.results if r["CONFIDENCE"] > 0.5]

        # Method statistics
        method_stats = {}
        for category in self.METHOD_CATEGORIES.keys():
            count = sum(1 for r in self.results if r[category] == 1)
            method_stats[category] = {
                "count": count,
                "percentage": (count / total_papers) * 100 if total_papers > 0 else 0,
            }

        # Text length statistics
        text_lengths = [r["TEXT_LENGTH"] for r in self.results if r["TEXT_LENGTH"] > 0]
        avg_text_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0

        report = {
            "total_papers": total_papers,
            "papers_with_methods": papers_with_methods,
            "detection_rate": (papers_with_methods / total_papers) * 100
            if total_papers > 0
            else 0,
            "pdf_access_stats": dict(pdf_stats),
            "high_confidence_papers": len(high_confidence),
            "method_statistics": method_stats,
            "average_text_length": int(avg_text_length),
            "papers_with_fulltext": len(
                [r for r in self.results if r["TEXT_LENGTH"] > 1000]
            ),
        }

        return report

    def print_analysis_summary(self):
        """Print analysis summary"""
        report = self.generate_analysis_report()

        print("\n" + "=" * 80)
        print("FULL-TEXT PDF ANALYSIS SUMMARY")
        print("=" * 80)

        if not report:
            print("No results to summarize.")
            return

        print(f"Total Papers Processed: {report['total_papers']:,}")
        print(
            f"Papers with Methods Detected: {report['papers_with_methods']:,} ({report['detection_rate']:.1f}%)"
        )
        print(
            f"High Confidence Detections (>0.5): {report['high_confidence_papers']:,}"
        )
        print(f"Average Text Length: {report['average_text_length']:,} characters")
        print(
            f"Papers with Full Text (>1000 chars): {report['papers_with_fulltext']:,}"
        )

        print(f"\nPDF Access Statistics:")
        for status, count in sorted(report["pdf_access_stats"].items()):
            percentage = (count / report["total_papers"]) * 100
            print(f"  {status:15}: {count:4,} papers ({percentage:5.1f}%)")

        print(f"\nTop Method Categories (Full-Text Analysis):")
        sorted_methods = sorted(
            report["method_statistics"].items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )

        for method, stats in sorted_methods[:12]:
            print(
                f"  {method:25}: {stats['count']:5,} papers ({stats['percentage']:5.1f}%)"
            )

        print("=" * 80)


def main():
    """Main execution function"""
    analyzer = FullTextAnalyzer()

    # Process all files
    logger.info("Starting full-text PDF analysis...")
    results = analyzer.process_all_files()

    if not results:
        print("No results found. Please check your BibTeX files.")
        return

    # Save comprehensive CSV
    analyzer.save_comprehensive_csv("fulltext_methods_analysis.csv")

    # Print summary
    analyzer.print_analysis_summary()

    # Save detailed report
    report = analyzer.generate_analysis_report()
    with open("fulltext_analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nOutput files created:")
    print(
        f"  - fulltext_methods_analysis.csv (comprehensive CSV with full-text analysis)"
    )
    print(f"  - fulltext_analysis_report.json (detailed analysis report)")
    print(f"  - pdf_analysis.log (detailed processing log)")

    # Show examples of successful extractions
    pdf_successes = [r for r in results if r["PDF_STATUS"] == "pdf_success"][:3]
    if pdf_successes:
        print(f"\nExample successful PDF extractions:")
        for example in pdf_successes:
            print(f"  • {example['TITLE'][:60]}...")
            print(
                f"    Text length: {example['TEXT_LENGTH']:,} chars, Confidence: {example['CONFIDENCE']:.3f}"
            )

    web_successes = [r for r in results if r["PDF_STATUS"] == "web_scraped"][:3]
    if web_successes:
        print(f"\nExample successful web scraping:")
        for example in web_successes:
            print(f"  • {example['TITLE'][:60]}...")
            print(
                f"    Text length: {example['TEXT_LENGTH']:,} chars, Confidence: {example['CONFIDENCE']:.3f}"
            )


if __name__ == "__main__":
    main()
