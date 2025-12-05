#!/usr/bin/env python3
"""
Interactive Results Explorer for BibTeX Methods Analysis

This script provides interactive tools to explore the results from the BibTeX methods extraction.
It allows filtering, searching, and analyzing the extracted methods data.

Requirements:
    pip install pandas

Usage:
    python3 explore_results.py
"""

import json
from collections import defaultdict
from typing import Dict, List, Optional

import pandas as pd


class ResultsExplorer:
    """Interactive explorer for BibTeX methods analysis results"""

    def __init__(
        self, csv_file="methods_analysis.csv", json_file="detailed_methods_results.json"
    ):
        self.csv_file = csv_file
        self.json_file = json_file
        self.df = None
        self.detailed_data = None
        self.load_data()

    def load_data(self):
        """Load CSV and JSON data"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✓ Loaded {len(self.df)} entries from {self.csv_file}")
        except FileNotFoundError:
            print(
                f"✗ CSV file {self.csv_file} not found. Run bibtex_csv_generator.py first."
            )
            return

        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                self.detailed_data = json.load(f)
            print(f"✓ Loaded detailed data from {self.json_file}")
        except FileNotFoundError:
            print(
                f"⚠ Detailed JSON file {self.json_file} not found. Some features will be limited."
            )
            self.detailed_data = []

    def show_overview(self):
        """Display overview statistics"""
        if self.df is None:
            print("No data loaded.")
            return

        print("\n" + "=" * 60)
        print("METHODS ANALYSIS OVERVIEW")
        print("=" * 60)

        # Basic stats
        total_entries = len(self.df)
        unique_papers = self.df["bibref"].nunique()
        date_range = f"{self.df['date'].min():.0f}-{self.df['date'].max():.0f}"

        print(f"Total method instances: {total_entries:,}")
        print(f"Unique papers: {unique_papers:,}")
        print(f"Date range: {date_range}")

        # Method categories
        print(
            f"\nMethod Categories ({len(self.df['method_category'].unique())} total):"
        )
        method_counts = self.df["method_category"].value_counts()
        for category, count in method_counts.head(10).items():
            percentage = (count / total_entries) * 100
            print(f"  {category}: {count:,} ({percentage:.1f}%)")

        # Decade distribution
        print(f"\nDecade Distribution:")
        decades = self.df[self.df["date"].notna()]
        decade_groups = decades.groupby((decades["date"] // 10) * 10)[
            "bibref"
        ].nunique()
        for decade, count in decade_groups.items():
            print(f"  {int(decade)}s: {count:,} papers")

    def filter_by_category(self, category: str) -> pd.DataFrame:
        """Filter results by method category"""
        if self.df is None:
            return pd.DataFrame()

        filtered = self.df[
            self.df["method_category"].str.contains(category, case=False, na=False)
        ]
        print(f"\nFound {len(filtered)} entries for category containing '{category}'")
        return filtered

    def filter_by_decade(self, decade: int) -> pd.DataFrame:
        """Filter results by decade (e.g., 2010 for 2010s)"""
        if self.df is None:
            return pd.DataFrame()

        start_year = decade
        end_year = decade + 10
        filtered = self.df[
            (self.df["date"] >= start_year)
            & (self.df["date"] < end_year)
            & (self.df["date"].notna())
        ]
        print(f"\nFound {len(filtered)} entries from {decade}s")
        return filtered

    def search_sentences(self, keyword: str) -> pd.DataFrame:
        """Search for specific keywords in method sentences"""
        if self.df is None:
            return pd.DataFrame()

        filtered = self.df[
            self.df["sentence"].str.contains(keyword, case=False, na=False)
        ]
        print(f"\nFound {len(filtered)} entries containing '{keyword}' in sentences")
        return filtered

    def top_papers_by_methods(self, n: int = 10) -> pd.DataFrame:
        """Find papers with most method instances"""
        if self.df is None:
            return pd.DataFrame()

        # Count methods per paper (excluding "No specific method identified")
        methods_only = self.df[
            self.df["method_category"] != "No specific method identified"
        ]
        paper_counts = (
            methods_only.groupby("bibref")
            .agg(
                {
                    "method_category": "count",
                    "date": "first",
                    "sentence": lambda x: list(x)[:3],  # First 3 sentences
                }
            )
            .reset_index()
        )

        paper_counts.columns = ["bibref", "method_count", "date", "sample_sentences"]
        paper_counts = paper_counts.sort_values("method_count", ascending=False)

        print(f"\nTop {n} papers by number of identified methods:")
        return paper_counts.head(n)

    def method_evolution_summary(self) -> Dict:
        """Analyze how methods evolved over decades"""
        if self.df is None:
            return {}

        # Filter out "No specific method identified"
        methods_df = self.df[
            self.df["method_category"] != "No specific method identified"
        ]

        evolution = {}
        decades = sorted(methods_df["date"].dropna() // 10 * 10)

        for decade in decades.unique():
            decade_data = methods_df[
                (methods_df["date"] >= decade) & (methods_df["date"] < decade + 10)
            ]

            method_counts = decade_data["method_category"].value_counts().to_dict()
            paper_counts = decade_data["bibref"].nunique()

            evolution[f"{int(decade)}s"] = {
                "total_papers_with_methods": paper_counts,
                "method_distribution": method_counts,
            }

        return evolution

    def export_filtered_results(self, filtered_df: pd.DataFrame, filename: str):
        """Export filtered results to CSV"""
        if filtered_df.empty:
            print("No data to export.")
            return

        filtered_df.to_csv(filename, index=False)
        print(f"✓ Exported {len(filtered_df)} entries to {filename}")

    def interactive_menu(self):
        """Interactive menu for exploring results"""
        while True:
            print("\n" + "=" * 50)
            print("INTERACTIVE RESULTS EXPLORER")
            print("=" * 50)
            print("1. Show overview")
            print("2. Filter by method category")
            print("3. Filter by decade")
            print("4. Search in sentences")
            print("5. Top papers by method count")
            print("6. Method evolution summary")
            print("7. Export current results")
            print("0. Exit")

            choice = input("\nEnter your choice (0-7): ").strip()

            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                self.show_overview()
            elif choice == "2":
                category = input("Enter method category to search for: ").strip()
                if category:
                    filtered = self.filter_by_category(category)
                    if not filtered.empty:
                        print(f"\nSample results:")
                        print(
                            filtered[["date", "bibref", "method_category"]]
                            .head(10)
                            .to_string(index=False)
                        )
            elif choice == "3":
                try:
                    decade = int(input("Enter decade (e.g., 2010 for 2010s): ").strip())
                    filtered = self.filter_by_decade(decade)
                    if not filtered.empty:
                        methods_summary = (
                            filtered["method_category"].value_counts().head(8)
                        )
                        print(f"\nTop methods in {decade}s:")
                        for method, count in methods_summary.items():
                            print(f"  {method}: {count}")
                except ValueError:
                    print("Please enter a valid year.")
            elif choice == "4":
                keyword = input("Enter keyword to search in sentences: ").strip()
                if keyword:
                    filtered = self.search_sentences(keyword)
                    if not filtered.empty:
                        print(f"\nSample sentences containing '{keyword}':")
                        for i, row in filtered.head(5).iterrows():
                            print(f"  • {row['sentence'][:100]}...")
            elif choice == "5":
                try:
                    n = int(
                        input("How many top papers to show? (default 10): ").strip()
                        or "10"
                    )
                    top_papers = self.top_papers_by_methods(n)
                    if not top_papers.empty:
                        print(top_papers.to_string(index=False))
                except ValueError:
                    print("Please enter a valid number.")
            elif choice == "6":
                evolution = self.method_evolution_summary()
                print(f"\nMethod Evolution Across Decades:")
                for decade, data in evolution.items():
                    print(f"\n{decade}:")
                    print(f"  Papers with methods: {data['total_papers_with_methods']}")
                    print("  Top methods:")
                    for method, count in list(data["method_distribution"].items())[:5]:
                        print(f"    {method}: {count}")
            elif choice == "7":
                filename = input(
                    "Enter filename for export (e.g., filtered_results.csv): "
                ).strip()
                if filename and hasattr(self, "last_filtered"):
                    self.export_filtered_results(self.last_filtered, filename)
                else:
                    print(
                        "No filtered results to export. Run a filter operation first."
                    )
            else:
                print("Invalid choice. Please try again.")

    def quick_analysis(self):
        """Perform quick analysis and display key insights"""
        if self.df is None:
            print("No data available for analysis.")
            return

        print("\n" + "=" * 60)
        print("QUICK ANALYSIS - KEY INSIGHTS")
        print("=" * 60)

        # Growth trends
        methods_df = self.df[
            self.df["method_category"] != "No specific method identified"
        ]
        decades = methods_df.groupby(methods_df["date"] // 10 * 10).agg(
            {"bibref": "nunique", "method_category": "count"}
        )
        decades.columns = ["unique_papers", "method_instances"]

        print("Growth Trends:")
        for decade, row in decades.iterrows():
            if pd.notna(decade):
                print(
                    f"  {int(decade)}s: {row['unique_papers']} papers, {row['method_instances']} method instances"
                )

        # Most productive decades
        print(f"\nMost Productive Decades:")
        top_decades = decades.sort_values("unique_papers", ascending=False).head(3)
        for decade, row in top_decades.iterrows():
            if pd.notna(decade):
                print(f"  {int(decade)}s: {row['unique_papers']} papers")

        # Method diversity by decade
        print(f"\nMethod Diversity by Decade:")
        diversity = methods_df.groupby(methods_df["date"] // 10 * 10)[
            "method_category"
        ].nunique()
        for decade, count in diversity.items():
            if pd.notna(decade):
                print(f"  {int(decade)}s: {count} different method types")

        # Emerging vs established methods
        recent_methods = methods_df[methods_df["date"] >= 2010][
            "method_category"
        ].value_counts()
        older_methods = methods_df[methods_df["date"] < 2010][
            "method_category"
        ].value_counts()

        print(f"\nEmerging Methods (2010s+):")
        for method in recent_methods.head(5).index:
            recent_count = recent_methods.get(method, 0)
            older_count = older_methods.get(method, 0)
            if older_count == 0:
                print(f"  {method}: {recent_count} (new)")
            else:
                growth = (recent_count - older_count) / older_count * 100
                print(f"  {method}: {recent_count} ({growth:+.0f}% growth)")


def main():
    """Main function to run the explorer"""
    explorer = ResultsExplorer()

    if explorer.df is None:
        print("Cannot start explorer without data.")
        return

    print("Welcome to the BibTeX Methods Analysis Results Explorer!")
    print(
        "Run quick_analysis() for key insights, or interactive_menu() for detailed exploration."
    )

    # Show quick analysis first
    explorer.quick_analysis()

    # Ask if user wants interactive menu
    choice = (
        input("\nWould you like to use the interactive menu? (y/n): ").strip().lower()
    )
    if choice in ["y", "yes"]:
        explorer.interactive_menu()


if __name__ == "__main__":
    main()
