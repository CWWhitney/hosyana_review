#!/usr/bin/env python3
"""
Test Full-Text PDF Analyzer
Tests PDF extraction and web scraping on a small subset of papers

This is a test version to verify:
1. PDF path extraction from BibTeX
2. PDF text extraction
3. Web scraping fallback
4. Method detection on full text

Requirements:
    pip install PyPDF2 pdfplumber requests beautifulsoup4 bibtexparser
"""

import os
import re
import time
from pathlib import Path

import bibtexparser
import pdfplumber
import PyPDF2
import requests
from bs4 import BeautifulSoup


def clean_bibtex_text(text):
    """Clean BibTeX text"""
    if not text:
        return ""
    text = text.strip("{}")
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r"[\{\}]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_pdf_path_from_entry(entry):
    """Extract PDF path from BibTeX entry"""
    file_field = entry.get("file", "")
    if not file_field:
        return None

    # Parse the file field
    file_parts = file_field.split(":")
    if file_parts:
        pdf_path = file_parts[0].strip("{}")
        if pdf_path and not pdf_path.startswith("Attachment"):
            return pdf_path
    return None


def extract_pdf_text(pdf_path):
    """Extract text from PDF using multiple methods"""
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return ""

    print(f"Attempting to extract from: {pdf_path}")

    # Try pdfplumber first
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            max_pages = min(5, len(pdf.pages))  # First 5 pages for testing
            for i in range(max_pages):
                try:
                    page = pdf.pages[i]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    print(f"Error reading page {i}: {e}")

        if text and len(text.strip()) > 100:
            print(f"Successfully extracted {len(text)} characters with pdfplumber")
            return text
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    # Fallback to PyPDF2
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            max_pages = min(5, len(pdf_reader.pages))
            for i in range(max_pages):
                try:
                    page_text = pdf_reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    print(f"Error reading page {i}: {e}")

        if text and len(text.strip()) > 100:
            print(f"Successfully extracted {len(text)} characters with PyPDF2")
            return text
    except Exception as e:
        print(f"PyPDF2 failed: {e}")

    print("No usable text extracted from PDF")
    return ""


def get_urls_from_entry(entry):
    """Extract URLs from BibTeX entry"""
    urls = []

    # Check various URL fields
    url_fields = ["url", "doi"]
    for field in url_fields:
        url = entry.get(field, "")
        if url:
            url = clean_bibtex_text(url)
            if url.startswith("http"):
                urls.append(url)
            elif field == "doi" and not url.startswith("http"):
                urls.append(f"https://doi.org/{url}")

    return urls


def scrape_web_content(url):
    """Scrape content from web URL"""
    if not url or not url.startswith(("http://", "https://")):
        return ""

    try:
        print(f"Attempting to scrape: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to find main content
        content_selectors = [
            "article",
            "main",
            ".content",
            "#content",
            ".abstract",
            ".summary",
            ".article-body",
            "p",
        ]

        text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                element_text = element.get_text()
                if len(element_text) > 50:
                    text += element_text + "\n"

        # Clean up text
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 200:
            print(f"Successfully scraped {len(text)} characters")
            return text[:5000]  # Limit for testing

    except Exception as e:
        print(f"Web scraping failed: {e}")

    return ""


def test_method_detection(text):
    """Simple method detection test"""
    if not text:
        return []

    text_lower = text.lower()
    found_methods = []

    # Test a few key method categories
    test_methods = {
        "Decision Analysis": ["decision analysis", "decision tree", "decision support"],
        "Bayesian": ["bayesian", "bayes", "posterior", "prior", "mcmc"],
        "Monte Carlo": ["monte carlo", "simulation", "stochastic"],
        "Uncertainty": ["uncertainty", "risk analysis", "sensitivity analysis"],
        "Stakeholder": ["stakeholder", "expert", "participatory"],
    }

    for category, keywords in test_methods.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_methods.append(f"{category}:{keyword}")
                break

    return found_methods


def main():
    """Test the full-text analyzer on a few entries"""
    print("Testing Full-Text PDF Analyzer")
    print("=" * 50)

    # Load a small BibTeX file for testing
    bib_files = list(Path("bib/bib_raw").glob("*.bib"))
    if not bib_files:
        print("No BibTeX files found in bib/bib_raw/")
        return

    # Test with first file, limited entries
    test_file = bib_files[0]
    print(f"Testing with: {test_file}")

    try:
        with open(test_file, "r", encoding="utf-8") as f:
            bib_database = bibtexparser.load(f)

        # Test first 5 entries
        test_entries = bib_database.entries[:5]
        print(f"Testing {len(test_entries)} entries\n")

        for i, entry in enumerate(test_entries):
            bibref = entry.get("ID", "unknown")
            title = clean_bibtex_text(entry.get("title", ""))

            print(f"\n--- Entry {i + 1}: {bibref} ---")
            print(f"Title: {title[:80]}...")

            # Test PDF extraction
            pdf_path = get_pdf_path_from_entry(entry)
            if pdf_path:
                print(f"PDF path found: {pdf_path}")
                pdf_text = extract_pdf_text(pdf_path)
                if pdf_text:
                    print(f"PDF text extracted: {len(pdf_text)} characters")
                    methods = test_method_detection(pdf_text)
                    print(f"Methods found: {methods}")
                    continue
            else:
                print("No PDF path found")

            # Test web scraping
            urls = get_urls_from_entry(entry)
            if urls:
                print(f"URLs found: {urls}")
                for url in urls[:1]:  # Test first URL only
                    web_text = scrape_web_content(url)
                    if web_text:
                        print(f"Web text scraped: {len(web_text)} characters")
                        methods = test_method_detection(web_text)
                        print(f"Methods found: {methods}")
                        break
                    time.sleep(2)  # Be respectful
            else:
                print("No URLs found")

            # Fallback to metadata
            abstract = clean_bibtex_text(entry.get("abstract", ""))
            if abstract:
                print(f"Using abstract: {len(abstract)} characters")
                methods = test_method_detection(title + " " + abstract)
                print(f"Methods found: {methods}")
            else:
                print("No abstract available")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
