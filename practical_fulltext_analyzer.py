#!/usr/bin/env python3
"""
Practical Full-Text Analyzer for Decision Support Methods
Focuses on accessible text sources with intelligent fallbacks

This script:
1. Extracts metadata from BibTeX files
2. Attempts web scraping from DOI/URL when available
3. Uses comprehensive keyword matching for method detection
4. Generates detailed CSV with confidence scores and source tracking
5. Handles rate limiting and respectful web access

Requirements:
    pip install bibtexparser requests beautifulsoup4 pandas
"""

import csv
import json
import logging
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import bibtexparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("practical_analysis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class PracticalFullTextAnalyzer:
    """Practical analyzer focusing on accessible text sources"""

    # Enhanced method categories based on decision support literature
    METHOD_CATEGORIES = {
        "DECISION_ANALYSIS": [
            "decision analysis",
            "decision tree",
            "decision support",
            "decision making",
            "decision model",
            "decision framework",
            "influence diagram",
            "decision network",
            "rollback analysis",
            "value of information",
            "expected value",
            "decision criterion",
            "alternative evaluation",
            "choice analysis",
            "prescriptive analytics",
        ],
        "POLICY_INTERVENTION": [
            "policy analysis",
            "policy evaluation",
            "policy assessment",
            "intervention analysis",
            "intervention evaluation",
            "policy support",
            "policy decision",
            "policy making",
            "regulatory analysis",
            "governance",
            "public policy",
            "program evaluation",
            "impact assessment",
            "cost-effectiveness",
            "cost-benefit",
            "policy option",
            "evidence-based policy",
            "policy implementation",
            "regulatory impact",
        ],
        "UNCERTAINTY_ANALYSIS": [
            "uncertainty analysis",
            "uncertainty assessment",
            "uncertainty quantification",
            "risk analysis",
            "risk assessment",
            "variability analysis",
            "sensitivity analysis",
            "scenario analysis",
            "what-if analysis",
            "robustness analysis",
            "error propagation",
            "confidence interval",
            "prediction interval",
            "measurement uncertainty",
            "model uncertainty",
            "epistemic uncertainty",
            "aleatory uncertainty",
        ],
        "STAKEHOLDER_EXPERT": [
            "stakeholder analysis",
            "stakeholder engagement",
            "expert judgment",
            "expert elicitation",
            "expert assessment",
            "expert opinion",
            "participatory",
            "collaborative decision",
            "group decision",
            "consensus building",
            "multi-stakeholder",
            "delphi method",
            "focus group",
            "structured interview",
            "knowledge elicitation",
            "participatory research",
        ],
        "MODELING_SIMULATION": [
            "mathematical model",
            "simulation model",
            "computer model",
            "predictive model",
            "monte carlo",
            "stochastic simulation",
            "agent-based model",
            "system dynamics",
            "discrete event simulation",
            "numerical model",
            "analytical model",
            "statistical model",
        ],
        "BAYESIAN_PROBABILISTIC": [
            "bayesian",
            "bayes",
            "posterior",
            "prior",
            "bayesian inference",
            "bayesian analysis",
            "bayesian network",
            "mcmc",
            "markov chain monte carlo",
            "gibbs sampling",
            "probabilistic",
            "probability",
            "stochastic",
            "likelihood",
            "bootstrap",
        ],
        "COMPUTER_ASSISTED": [
            "computer assisted",
            "computerized",
            "digital",
            "automated",
            "software",
            "algorithm",
            "machine learning",
            "artificial intelligence",
            "data mining",
            "analytics",
            "decision support system",
            "expert system",
            "web-based",
            "online platform",
        ],
        "VALUE_INFORMATION": [
            "value of information",
            "value of perfect information",
            "information value",
            "information accuracy",
            "information quality",
            "data quality",
            "precision",
            "reliability",
            "validity",
            "information theory",
            "measurement accuracy",
        ],
        "MULTI_CRITERIA": [
            "multi-criteria",
            "multicriteria",
            "mcda",
            "mcdm",
            "analytic hierarchy process",
            "ahp",
            "topsis",
            "electre",
            "promethee",
            "multi-attribute",
            "multi-objective",
        ],
        "OPTIMIZATION": [
            "optimization",
            "optimisation",
            "linear programming",
            "integer programming",
            "dynamic programming",
            "genetic algorithm",
            "evolutionary algorithm",
        ],
        "ECONOMIC_EVALUATION": [
            "cost-effectiveness",
            "cost-benefit",
            "economic evaluation",
            "health economics",
            "return on investment",
            "net present value",
            "willingness to pay",
        ],
        "BEHAVIORAL_PSYCHOLOGY": [
            "behavioral",
            "psychology",
            "cognitive",
            "heuristic",
            "bias",
            "prospect theory",
            "bounded rationality",
            "framing effect",
            "behavioral economics",
        ],
    }

    def __init__(self, bib_raw_directory: str = "bib/bib_raw"):
        self.bib_raw_directory = Path(bib_raw_directory)
        self.results = []
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; Academic Research Bot; +https://example.edu/bot)"
            }
        )
        self.request_delay = 2  # Seconds between requests
        self.last_request_time = 0

    def clean_bibtex_text(self, text: str) -> str:
        """Clean BibTeX text"""
        if not text:
            return ""
        text = text.strip("{}")
        text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)
        text = re.sub(r"[\{\}]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def get_web_urls(self, entry: Dict) -> List[str]:
        """Extract accessible web URLs from entry"""
        urls = []

        # Check DOI first (most reliable)
        doi = entry.get("doi", "")
        if doi:
            doi = self.clean_bibtex_text(doi)
            if doi and not doi.startswith("http"):
                urls.append(f"https://doi.org/{doi}")
            elif doi.startswith("http"):
                urls.append(doi)

        # Check URL field
        url = entry.get("url", "")
        if url:
            url = self.clean_bibtex_text(url)
            if url.startswith("http"):
                urls.append(url)

        return urls

    def respectful_request(self, url: str) -> requests.Response:
        """Make request with rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)

        response = self.session.get(url, timeout=15)
        self.last_request_time = time.time()
        return response

    def extract_web_content(self, url: str) -> Tuple[str, str]:
        """Extract content from web URL"""
        if not url or not url.startswith(("http://", "https://")):
            return "", "invalid_url"

        try:
            logger.info(f"Accessing: {url}")
            response = self.respectful_request(url)

            if response.status_code == 403:
                return "", "access_denied"
            elif response.status_code == 404:
                return "", "not_found"

            response.raise_for_status()

            # Check if it's HTML content
            content_type = response.headers.get("content-type", "").lower()
            if "html" not in content_type and "xml" not in content_type:
                return "", "not_html"

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Try different content extraction strategies
            content_text = ""

            # Strategy 1: Look for academic paper content
            academic_selectors = [
                'div[class*="abstract"]',
                'section[class*="abstract"]',
                'div[class*="content"]',
                "article",
                "main",
                'div[class*="article-body"]',
                'div[class*="fulltext"]',
            ]

            for selector in academic_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(separator=" ", strip=True)
                    if len(text) > 200:  # Substantial content
                        content_text += text + " "

            # Strategy 2: If no academic content, get paragraphs
            if len(content_text) < 500:
                paragraphs = soup.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 50:  # Skip short paragraphs
                        content_text += text + " "

            # Clean up text
            content_text = re.sub(r"\s+", " ", content_text).strip()

            if len(content_text) > 300:
                logger.info(f"Extracted {len(content_text)} characters from web")
                return content_text[:8000], "web_success"  # Limit length
            else:
                return "", "insufficient_content"

        except requests.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            return "", "request_failed"
        except Exception as e:
            logger.warning(f"Parsing failed for {url}: {e}")
            return "", "parsing_failed"

    def analyze_text_for_methods(self, text: str, source_type: str) -> Dict:
        """Analyze text for decision support methods"""
        if not text:
            return self._empty_methods_dict()

        text_lower = text.lower()
        results = {}
        detected_methods = []
        method_details = {}
        total_confidence = 0.0

        for category, keywords in self.METHOD_CATEGORIES.items():
            matches = 0
            keyword_occurrences = 0
            matched_keywords = []

            for keyword in keywords:
                if keyword in text_lower:
                    matches += 1
                    keyword_count = text_lower.count(keyword)
                    keyword_occurrences += keyword_count
                    matched_keywords.append(keyword)

            # Binary indicator
            has_method = matches > 0
            results[category] = 1 if has_method else 0

            if has_method:
                # Calculate confidence based on source and matches
                base_confidence = min(
                    (matches * 0.1) + (keyword_occurrences * 0.05), 0.7
                )
                diversity_bonus = min(len(set(matched_keywords)) * 0.08, 0.25)

                # Source-based confidence adjustment
                if source_type == "web_success":
                    source_bonus = 0.3
                elif source_type == "rich_metadata":
                    source_bonus = 0.2
                else:
                    source_bonus = 0.1

                confidence = min(base_confidence + diversity_bonus + source_bonus, 1.0)

                detected_methods.append(f"{category}({confidence:.2f})")
                method_details[category] = {
                    "confidence": confidence,
                    "keywords": matched_keywords[:3],
                }
                total_confidence += confidence

        # Count uncertainty-related terms
        uncertainty_patterns = [
            r"uncertain(ty)?",
            r"risk\b",
            r"variability",
            r"confidence",
            r"probability",
            r"stochastic",
            r"monte carlo",
            r"simulation",
            r"sensitivity",
            r"scenario",
            r"robust",
        ]

        uncertainty_count = 0
        for pattern in uncertainty_patterns:
            uncertainty_count += len(re.findall(pattern, text_lower, re.IGNORECASE))

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
                "SOURCE_TYPE": source_type,
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
                "SOURCE_TYPE": "no_text",
                "METHOD_DETAILS": "",
            }
        )
        return results

    def process_entry(self, entry: Dict) -> Dict:
        """Process a single BibTeX entry"""
        # Extract metadata
        bibref = entry.get("ID", "unknown")
        title = self.clean_bibtex_text(entry.get("title", ""))
        authors = self.clean_bibtex_text(entry.get("author", ""))
        year_str = entry.get("year", "")
        abstract = self.clean_bibtex_text(entry.get("abstract", ""))
        keywords_str = self.clean_bibtex_text(entry.get("keywords", ""))
        journal = self.clean_bibtex_text(
            entry.get("journal", entry.get("booktitle", ""))
        )

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

        # Start with metadata analysis
        metadata_text = f"{title} {title} {title}. {abstract} {abstract}. {' '.join(keywords)}. {journal}"

        # Determine if we have rich metadata
        source_type = "basic_metadata"
        if abstract and len(abstract) > 100:
            source_type = "rich_metadata"

        # Try web content extraction
        web_text = ""
        urls = self.get_web_urls(entry)

        for url in urls[:2]:  # Try up to 2 URLs
            content, status = self.extract_web_content(url)
            if content and status == "web_success":
                web_text = content
                source_type = "web_success"
                logger.info(f"Web content extracted for {bibref}: {len(content)} chars")
                break

        # Combine texts
        if web_text:
            analysis_text = metadata_text + " " + web_text
        else:
            analysis_text = metadata_text

        # Analyze for methods
        methods_results = self.analyze_text_for_methods(analysis_text, source_type)

        # Create result
        result = {
            "TITLE": title,
            "YEAR": year or "",
            "BIBREF": bibref,
            "AUTHORS": authors,
            "JOURNAL": journal,
            "ABSTRACT": abstract,
            "KEYWORDS": "; ".join(keywords),
            "WEB_URLS": "; ".join(urls),
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
                if (i + 1) % 20 == 0:
                    logger.info(
                        f"Processed {i + 1}/{len(bib_database.entries)} entries"
                    )

                result = self.process_entry(entry)
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

    def save_results(self, output_file: str = "practical_fulltext_analysis.csv"):
        """Save results to CSV"""
        if not self.results:
            logger.warning("No results to save")
            return

        # Sort by confidence and year
        sorted_results = sorted(
            self.results, key=lambda x: (x["YEAR"] or 0, -x["CONFIDENCE"], x["TITLE"])
        )

        columns = (
            [
                "TITLE",
                "YEAR",
                "BIBREF",
                "AUTHORS",
                "JOURNAL",
                "SOURCE_TYPE",
                "TEXT_LENGTH",
                "DETECTED_METHODS",
                "CONFIDENCE",
                "HAS_METHODS",
                "UNCERTAINTY_STATEMENTS",
            ]
            + list(self.METHOD_CATEGORIES.keys())
            + ["ABSTRACT", "KEYWORDS", "WEB_URLS", "METHOD_DETAILS"]
        )

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for result in sorted_results:
                row = {col: result.get(col, "") for col in columns}
                writer.writerow(row)

        logger.info(f"Results saved to {output_file}")

    def generate_report(self) -> Dict:
        """Generate analysis report"""
        if not self.results:
            return {}

        total_papers = len(self.results)
        papers_with_methods = sum(1 for r in self.results if r["HAS_METHODS"] == 1)

        # Source type distribution
        source_stats = defaultdict(int)
        for result in self.results:
            source_stats[result["SOURCE_TYPE"]] += 1

        # High confidence papers
        high_confidence = [r for r in self.results if r["CONFIDENCE"] > 0.4]

        # Method statistics
        method_stats = {}
        for category in self.METHOD_CATEGORIES.keys():
            count = sum(1 for r in self.results if r[category] == 1)
            method_stats[category] = {
                "count": count,
                "percentage": (count / total_papers) * 100 if total_papers > 0 else 0,
            }

        return {
            "total_papers": total_papers,
            "papers_with_methods": papers_with_methods,
            "detection_rate": (papers_with_methods / total_papers) * 100
            if total_papers > 0
            else 0,
            "source_distribution": dict(source_stats),
            "high_confidence_papers": len(high_confidence),
            "method_statistics": method_stats,
            "web_accessible_papers": source_stats.get("web_success", 0),
        }

    def print_summary(self):
        """Print analysis summary"""
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("PRACTICAL FULL-TEXT ANALYSIS SUMMARY")
        print("=" * 80)

        if not report:
            print("No results to summarize.")
            return

        print(f"Total Papers: {report['total_papers']:,}")
        print(
            f"Papers with Methods: {report['papers_with_methods']:,} ({report['detection_rate']:.1f}%)"
        )
        print(f"High Confidence (>0.4): {report['high_confidence_papers']:,}")
        print(f"Web Accessible: {report['web_accessible_papers']:,}")

        print(f"\nSource Distribution:")
        for source, count in sorted(report["source_distribution"].items()):
            percentage = (count / report["total_papers"]) * 100
            print(f"  {source:20}: {count:5,} papers ({percentage:5.1f}%)")

        print(f"\nTop Method Categories:")
        sorted_methods = sorted(
            report["method_statistics"].items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )

        for method, stats in sorted_methods[:10]:
            print(
                f"  {method:25}: {stats['count']:5,} papers ({stats['percentage']:5.1f}%)"
            )

        print("=" * 80)


def main():
    """Main execution function"""
    analyzer = PracticalFullTextAnalyzer()

    logger.info("Starting practical full-text analysis...")
    results = analyzer.process_all_files()

    if not results:
        print("No results found.")
        return

    # Save results
    analyzer.save_results("practical_fulltext_analysis.csv")

    # Print summary
    analyzer.print_summary()

    # Save report
    report = analyzer.generate_report()
    with open("practical_analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nFiles created:")
    print(f"  - practical_fulltext_analysis.csv")
    print(f"  - practical_analysis_report.json")
    print(f"  - practical_analysis.log")

    # Show examples
    web_successes = [r for r in results if r["SOURCE_TYPE"] == "web_success"][:3]
    if web_successes:
        print(f"\nSuccessful web extractions:")
        for example in web_successes:
            print(f"  • {example['TITLE'][:60]}...")
            print(f"    Methods: {example['DETECTED_METHODS'][:80]}...")


if __name__ == "__main__":
    main()
