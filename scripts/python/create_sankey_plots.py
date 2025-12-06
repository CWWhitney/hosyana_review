#!/usr/bin/env python3
"""
Sankey Plot Generator for Decision Analysis Methods

This script creates Sankey diagrams showing the evolution of decision analysis
methods across decades using data from the BibTeX methods extractor.

Requirements:
    pip install plotly pandas

Usage:
    python create_sankey_plots.py

The script expects sankey_data.json to exist (created by bibtex_csv_generator.py)
"""

import json
import logging
from collections import defaultdict
from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SankeyPlotGenerator:
    """Generate Sankey plots for method evolution across decades"""

    def __init__(self, data_file: str = "sankey_data.json"):
        self.data_file = data_file
        self.sankey_data = self.load_data()

    def load_data(self) -> Dict:
        """Load Sankey data from JSON file"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded data for {len(data)} decades")
            return data
        except FileNotFoundError:
            logger.error(
                f"Data file {self.data_file} not found. Run bibtex_csv_generator.py first."
            )
            return {}
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {}

    def prepare_decade_to_method_sankey(self):
        """Prepare data for decade -> method Sankey diagram"""
        if not self.sankey_data:
            return [], []

        # Collect all unique decades and methods
        decades = sorted(self.sankey_data.keys())
        all_methods = set()

        for decade_data in self.sankey_data.values():
            all_methods.update(decade_data["methods"].keys())

        methods = sorted(list(all_methods))

        # Create nodes
        nodes = []
        node_colors = []

        # Decade colors (left side)
        decade_colors = px.colors.qualitative.Set3
        for i, decade in enumerate(decades):
            total_papers = self.sankey_data[decade]["total_papers"]
            nodes.append(f"{decade}<br>({total_papers} papers)")
            node_colors.append(decade_colors[i % len(decade_colors)])

        # Method colors (right side)
        method_colors = px.colors.qualitative.Plotly
        for i, method in enumerate(methods):
            nodes.append(method)
            node_colors.append(method_colors[i % len(method_colors)])

        # Create links
        links = []
        for decade_idx, decade in enumerate(decades):
            decade_methods = self.sankey_data[decade]["methods"]

            for method, count in decade_methods.items():
                if count > 0:  # Only include if there are instances
                    method_idx = len(decades) + methods.index(method)
                    links.append(
                        {"source": decade_idx, "target": method_idx, "value": count}
                    )

        return nodes, links, node_colors

    def create_decade_method_sankey(
        self, output_file: str = "decade_method_sankey.html"
    ):
        """Create Sankey diagram showing flow from decades to methods"""
        nodes, links, node_colors = self.prepare_decade_to_method_sankey()

        if not nodes or not links:
            logger.warning("No data available for Sankey diagram")
            return

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
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="Evolution of Decision Analysis Methods by Decade<br>"
            + "<sub>Flow from decades (left) to method categories (right)</sub>",
            font_size=12,
            width=1400,
            height=800,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        fig.write_html(output_file)
        logger.info(f"Decade-to-method Sankey plot saved to {output_file}")

    def prepare_method_evolution_sankey(self):
        """Prepare data for method evolution across consecutive decades"""
        if not self.sankey_data:
            return [], []

        decades = sorted(self.sankey_data.keys())

        # Get all methods
        all_methods = set()
        for decade_data in self.sankey_data.values():
            all_methods.update(decade_data["methods"].keys())
        methods = sorted(list(all_methods))

        # Create nodes for each decade-method combination
        nodes = []
        node_colors = []
        decade_method_to_index = {}

        colors = px.colors.qualitative.Set3

        for decade_idx, decade in enumerate(decades):
            decade_methods = self.sankey_data[decade]["methods"]

            for method_idx, method in enumerate(methods):
                count = decade_methods.get(method, 0)
                if count > 0:  # Only create nodes for methods that exist
                    node_label = f"{method}<br>{decade} ({count})"
                    nodes.append(node_label)
                    node_colors.append(colors[method_idx % len(colors)])
                    decade_method_to_index[(decade, method)] = len(nodes) - 1

        # Create links between consecutive decades
        links = []
        for i in range(len(decades) - 1):
            current_decade = decades[i]
            next_decade = decades[i + 1]

            current_methods = self.sankey_data[current_decade]["methods"]
            next_methods = self.sankey_data[next_decade]["methods"]

            for method in methods:
                if (
                    method in current_methods
                    and current_methods[method] > 0
                    and method in next_methods
                    and next_methods[method] > 0
                ):
                    source_idx = decade_method_to_index.get((current_decade, method))
                    target_idx = decade_method_to_index.get((next_decade, method))

                    if source_idx is not None and target_idx is not None:
                        # Use average of counts as flow value
                        flow_value = (
                            current_methods[method] + next_methods[method]
                        ) / 2
                        links.append(
                            {
                                "source": source_idx,
                                "target": target_idx,
                                "value": flow_value,
                            }
                        )

        return nodes, links, node_colors

    def create_method_evolution_sankey(
        self, output_file: str = "method_evolution_sankey.html"
    ):
        """Create Sankey diagram showing method evolution across decades"""
        nodes, links, node_colors = self.prepare_method_evolution_sankey()

        if not nodes or not links:
            logger.warning("No data available for method evolution Sankey diagram")
            return

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
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="Evolution of Decision Analysis Methods Across Decades<br>"
            + "<sub>Tracking method continuity and emergence over time</sub>",
            font_size=10,
            width=1600,
            height=900,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        fig.write_html(output_file)
        logger.info(f"Method evolution Sankey plot saved to {output_file}")

    def create_summary_bar_chart(self, output_file: str = "methods_by_decade_bar.html"):
        """Create bar chart showing method distribution by decade"""
        if not self.sankey_data:
            return

        # Prepare data for bar chart
        chart_data = []

        for decade, data in self.sankey_data.items():
            total_papers = data["total_papers"]
            methods = data["methods"]

            for method, count in methods.items():
                chart_data.append(
                    {
                        "Decade": decade,
                        "Method": method,
                        "Count": count,
                        "Percentage": (count / total_papers) * 100
                        if total_papers > 0
                        else 0,
                    }
                )

        df = pd.DataFrame(chart_data)

        if df.empty:
            logger.warning("No data for bar chart")
            return

        # Create stacked bar chart
        fig = px.bar(
            df,
            x="Decade",
            y="Count",
            color="Method",
            title="Distribution of Decision Analysis Methods by Decade",
            labels={"Count": "Number of Papers", "Method": "Method Category"},
        )

        fig.update_layout(
            width=1200,
            height=600,
            xaxis_title="Decade",
            yaxis_title="Number of Papers",
            legend_title="Method Categories",
            margin=dict(l=50, r=50, t=80, b=50),
        )

        fig.write_html(output_file)
        logger.info(f"Bar chart saved to {output_file}")

    def create_method_trend_lines(self, output_file: str = "method_trends_lines.html"):
        """Create line plot showing trends of top methods over decades"""
        if not self.sankey_data:
            return

        # Get method counts by decade
        method_trends = defaultdict(dict)

        for decade, data in self.sankey_data.items():
            for method, count in data["methods"].items():
                method_trends[method][decade] = count

        # Find top methods (by total occurrences)
        method_totals = {
            method: sum(decade_counts.values())
            for method, decade_counts in method_trends.items()
        }

        top_methods = sorted(method_totals.items(), key=lambda x: x[1], reverse=True)[
            :8
        ]

        # Prepare data for line plot
        chart_data = []
        decades = sorted(self.sankey_data.keys())

        for method, _ in top_methods:
            for decade in decades:
                count = method_trends[method].get(decade, 0)
                chart_data.append({"Decade": decade, "Method": method, "Count": count})

        df = pd.DataFrame(chart_data)

        if df.empty:
            logger.warning("No data for trend lines")
            return

        fig = px.line(
            df,
            x="Decade",
            y="Count",
            color="Method",
            title="Trends of Top Decision Analysis Methods Over Decades",
            markers=True,
        )

        fig.update_layout(
            width=1200,
            height=600,
            xaxis_title="Decade",
            yaxis_title="Number of Papers",
            legend_title="Method Categories",
            margin=dict(l=50, r=50, t=80, b=50),
        )

        fig.write_html(output_file)
        logger.info(f"Trend lines plot saved to {output_file}")

    def generate_all_plots(self):
        """Generate all visualization types"""
        logger.info("Generating all Sankey plots and visualizations...")

        # Main Sankey diagrams
        self.create_decade_method_sankey("decade_method_sankey.html")
        self.create_method_evolution_sankey("method_evolution_sankey.html")

        # Additional visualizations
        self.create_summary_bar_chart("methods_by_decade_bar.html")
        self.create_method_trend_lines("method_trends_lines.html")

        logger.info("All plots generated successfully!")

    def print_data_summary(self):
        """Print summary of the data"""
        if not self.sankey_data:
            print("No data loaded")
            return

        print("\n" + "=" * 70)
        print("SANKEY DATA SUMMARY")
        print("=" * 70)

        total_papers = sum(data["total_papers"] for data in self.sankey_data.values())
        print(f"Total papers across all decades: {total_papers}")
        print(f"Decades covered: {len(self.sankey_data)}")

        print("\nDecade breakdown:")
        for decade in sorted(self.sankey_data.keys()):
            data = self.sankey_data[decade]
            total = data["total_papers"]
            method_count = len(data["methods"])
            method_instances = sum(data["methods"].values())

            print(
                f"  {decade}: {total} papers, {method_count} method types, {method_instances} method instances"
            )

        # Top methods overall
        all_methods = defaultdict(int)
        for data in self.sankey_data.values():
            for method, count in data["methods"].items():
                all_methods[method] += count

        print(f"\nTop methods overall:")
        top_methods = sorted(all_methods.items(), key=lambda x: x[1], reverse=True)[:8]
        for method, count in top_methods:
            print(f"  {method}: {count}")

        print("=" * 70)


def main():
    """Main execution function"""
    generator = SankeyPlotGenerator()

    # Print summary of data
    generator.print_data_summary()

    if not generator.sankey_data:
        print(
            "\nNo data available. Please run bibtex_csv_generator.py first to create sankey_data.json"
        )
        return

    # Generate all plots
    generator.generate_all_plots()

    print(f"\nVisualization files created:")
    print(f"  - decade_method_sankey.html (main Sankey: decades → methods)")
    print(f"  - method_evolution_sankey.html (method evolution across decades)")
    print(f"  - methods_by_decade_bar.html (stacked bar chart)")
    print(f"  - method_trends_lines.html (trend lines for top methods)")


if __name__ == "__main__":
    main()
