#!/usr/bin/env python3
"""
Python Sankey Plot Generator - R Style
Based on plot_sankey.R function structure

This creates Sankey diagrams following the same logic as the R function,
showing inputs flowing through with losses/outputs at various stages.

Usage:
    python sankey_r_style.py
"""

import json
import math
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class RSankeyPlot:
    """Python implementation of R-style Sankey plot function"""

    def __init__(self):
        self.fig = None
        self.ax = None

    def plot_sankey(
        self,
        inputs: List[float],
        losses: List[float],
        unit: str,
        labels: List[str],
        format_type: str = "plot",
        filename: str = "sankey_plot",
    ):
        """
        Create Sankey diagram following R function logic

        Args:
            inputs: Vector of input values
            losses: Vector of loss/output values
            unit: String of the unit
            labels: Vector of labels for inputs and losses
            format_type: 'plot', 'png', 'pdf', 'svg'
            filename: Output filename (without extension)
        """

        # Calculate fractional losses and inputs
        total_inputs = sum(inputs)
        fr_losses = [loss / total_inputs for loss in losses]
        fr_inputs = [inp / total_inputs for inp in inputs]

        # Calculate plot boundaries following R logic
        lim_top = fr_inputs[0]
        pos_top = 0.4
        max_y = 0
        lim_bot = 0
        pos_bot = 0.1

        # Calculate positions for additional inputs
        if len(inputs) > 1:
            for j in range(1, len(inputs)):
                r_i = max(0.07, abs(fr_inputs[j] / 2))
                r_e = r_i + abs(fr_inputs[j])
                new_pos_b = pos_bot + r_e * math.sin(math.pi / 4) + 0.01
                pos_bot = new_pos_b
                lim_bot = lim_bot - fr_inputs[j]

        pos_top = pos_bot + 0.4

        # Calculate positions for losses
        for i in range(len(losses) - 1):
            r_i = max(0.07, abs(fr_losses[i] / 2))
            r_e = r_i + abs(fr_losses[i])
            ar_top = max(0.04, 0.8 * fr_losses[i])
            if ar_top > max_y:
                max_y = ar_top
            lim_top = lim_top - fr_losses[i]
            new_pos = pos_top + r_e + 0.01
            pos_top = new_pos

        # Final positioning
        new_pos = max(pos_top, pos_bot) + max(0.05 * lim_top, 0.05)
        new_pos = new_pos + 0.8 * (lim_top - lim_bot)

        max_x = new_pos
        min_y = (lim_top - fr_losses[-1]) - max(0.015, abs(fr_losses[-1] / 4))
        max_y = max_y * 2
        min_x = 0

        # Create figure
        fig_width = max(12, (max_x + 3 - min_x) * 2)
        fig_height = max(8, fig_width * (max_y - min_y) / ((max_x + 3) - min_x))

        self.fig, self.ax = plt.subplots(1, 1, figsize=(fig_width, fig_height))
        self.ax.set_xlim(-1.5, max_x + 1.5)
        self.ax.set_ylim(min_y, max_y)
        self.ax.axis("off")

        # Line width
        lw = 2

        # Recalculate for drawing
        fr_losses = [loss / total_inputs for loss in losses]
        fr_inputs = [inp / total_inputs for inp in inputs]

        # Draw first input arrow
        self._draw_line(
            [0.1, 0, 0.05, 0, 0.4],
            [0, 0, fr_inputs[0] / 2, fr_inputs[0], fr_inputs[0]],
            lw,
        )

        # First input label
        input_label = (
            f"{labels[0]}: {inputs[0]} {unit} ({round(100 * fr_inputs[0], 1)}%)"
        )
        fontsize = max(8, fr_inputs[0] * 20)
        self.ax.text(
            0, fr_inputs[0] / 2, input_label, fontsize=fontsize, ha="right", va="center"
        )

        # Reset positions
        lim_top = fr_inputs[0]
        pos_top = 0.4
        lim_bot = 0
        pos_bot = 0.1

        # Draw additional input arrows
        if len(inputs) > 1:
            for j in range(1, len(inputs)):
                r_i = max(0.07, abs(fr_inputs[j] / 2))
                r_e = r_i + abs(fr_inputs[j])
                new_pos_b = pos_bot + r_e * math.sin(math.pi / 4) + 0.01

                # Draw connection line
                self._draw_line([pos_bot, new_pos_b], [lim_bot, lim_bot], lw)
                pos_bot = new_pos_b

                # Draw arcs
                self._draw_input_arc(pos_bot, lim_bot, r_i, r_e, fr_inputs[j], lw)

                # Draw label
                phi_text = math.pi / 2 - 2 * min(0.05, 0.8 * abs(fr_inputs[j])) / (
                    r_i + r_e
                )
                x_text = pos_bot - (r_e + r_i) * math.sin(phi_text) / 3
                y_text = lim_bot - r_e / 1.5 + (r_e + r_i) * math.cos(phi_text) / 2
                full_label = (
                    f"{labels[j]}: {inputs[j]} {unit} ({round(100 * fr_inputs[j], 1)}%)"
                )
                fontsize = max(8, fr_inputs[j] * 15)
                self.ax.text(
                    x_text,
                    y_text,
                    full_label,
                    fontsize=fontsize,
                    ha="right",
                    va="center",
                )

                lim_bot = lim_bot - fr_inputs[j]

            pos_top = pos_bot + 0.4
            self._draw_line([0.4, pos_top], [fr_inputs[0], fr_inputs[0]], lw)
            self._draw_line(
                [pos_bot, pos_bot + (pos_top - pos_bot) / 2], [lim_bot, lim_bot], lw
            )
            pos_mid = pos_bot + (pos_top - pos_bot) / 2
        else:
            self._draw_line(
                [pos_bot, pos_bot + (pos_top - pos_bot) / 2], [lim_bot, lim_bot], lw
            )
            pos_mid = pos_bot + (pos_top - pos_bot) / 2

        # Draw loss arrows
        lim_top = fr_inputs[0]
        for i in range(len(losses) - 1):
            r_i = max(0.07, abs(fr_losses[i] / 2))
            r_e = r_i + abs(fr_losses[i])

            # Draw arcs
            self._draw_loss_arc(pos_top, lim_top, r_i, r_e, fr_losses[i], lw)

            # Draw arrow tip
            ar_edge = max(0.015, r_i / 3)
            ar_top = max(0.04, 0.8 * fr_losses[i])
            ar_x = [
                pos_top + r_i + x
                for x in [
                    0,
                    -ar_edge,
                    fr_losses[i] / 2,
                    fr_losses[i] + ar_edge,
                    fr_losses[i],
                ]
            ]
            ar_y = [lim_top + r_i + y for y in [0, 0, ar_top, 0, 0]]
            self._draw_line(ar_x, ar_y, lw)

            # Draw label
            txt_x = pos_top + r_i + fr_losses[i] / 2
            txt_y = lim_top + r_i + ar_top + 0.05
            full_label = f"{labels[i + len(inputs)]}: {losses[i]} {unit} ({round(100 * fr_losses[i], 1)}%)"
            fontsize = max(8, fr_losses[i] * 20)
            self.ax.text(
                txt_x,
                txt_y,
                full_label,
                fontsize=fontsize,
                rotation=90,
                ha="left",
                va="bottom",
            )

            lim_top = lim_top - fr_losses[i]
            new_pos = pos_top + r_e + 0.01
            self._draw_line([pos_top, new_pos], [lim_top, lim_top], lw)
            pos_top = new_pos

        # Final arrow
        new_pos = max(pos_top, pos_bot) + max(0.05 * lim_top, 0.05)
        self._draw_line([pos_top, new_pos], [lim_top, lim_top], lw)
        self._draw_line(
            [pos_mid, new_pos], [lim_top - fr_losses[-1], lim_top - fr_losses[-1]], lw
        )

        # Final arrowhead
        final_arrow_x = [
            new_pos,
            new_pos,
            new_pos + max(0.04, 0.8 * fr_losses[-1]),
            new_pos,
            new_pos,
        ]
        final_arrow_y = [
            lim_top,
            lim_top + max(0.015, abs(fr_losses[-1] / 6)),
            lim_top - fr_losses[-1] / 2,
            (lim_top - fr_losses[-1]) - max(0.015, abs(fr_losses[-1] / 6)),
            lim_top - fr_losses[-1],
        ]
        self._draw_line(final_arrow_x, final_arrow_y, lw)

        new_pos = new_pos + 0.8 * fr_losses[-1]

        # Final label
        loss_label = (
            f"{labels[-1]}: {losses[-1]} {unit} ({round(100 * fr_losses[-1], 1)}%)"
        )
        fontsize = max(8, fr_losses[-1] * 20)
        self.ax.text(
            new_pos + 0.05,
            lim_top - fr_losses[-1] / 2,
            loss_label,
            fontsize=fontsize,
            ha="left",
            va="center",
        )

        # Draw midline
        if lim_bot < (lim_top - fr_losses[-1]):
            self._draw_line(
                [pos_mid, pos_mid],
                [fr_inputs[0], lim_bot],
                lw,
                linestyle="--",
                alpha=0.5,
            )
        else:
            self._draw_line(
                [pos_mid, pos_mid],
                [fr_inputs[0], lim_top - fr_losses[-1]],
                lw,
                linestyle="--",
                alpha=0.5,
            )

        plt.tight_layout()

        # Save or show
        if format_type != "plot":
            if format_type == "png":
                plt.savefig(f"{filename}.png", dpi=300, bbox_inches="tight")
            elif format_type == "pdf":
                plt.savefig(f"{filename}.pdf", bbox_inches="tight")
            elif format_type == "svg":
                plt.savefig(f"{filename}.svg", bbox_inches="tight")

        return self.fig, self.ax

    def _draw_line(self, x_coords, y_coords, linewidth, linestyle="-", alpha=1.0):
        """Draw line segments"""
        self.ax.plot(
            x_coords,
            y_coords,
            "k-",
            linewidth=linewidth,
            linestyle=linestyle,
            alpha=alpha,
        )

    def _draw_input_arc(self, pos_bot, lim_bot, r_i, r_e, fr_input, lw):
        """Draw input arc following R logic"""
        # External arc
        angles = np.linspace(0, math.pi / 4, 100)
        arc_ex = pos_bot - r_e * np.sin(angles)
        arc_ey = lim_bot - r_e * (1 - np.cos(angles))
        self.ax.plot(arc_ex, arc_ey, "k-", linewidth=lw)

        # Internal arc
        arc_ix = pos_bot - r_i * np.sin(angles)
        arc_iy = lim_bot - r_e + r_i * np.cos(angles)
        self.ax.plot(arc_ix, arc_iy, "k-", linewidth=lw)

        # Arrow tip
        phi_tip = math.pi / 4 - 2 * min(0.05, 0.8 * abs(fr_input)) / (r_i + r_e)
        x_tip = pos_bot - (r_e + r_i) * math.sin(phi_tip) / 2
        y_tip = lim_bot - r_e + (r_e + r_i) * math.cos(phi_tip) / 2

        tip_x = [min(arc_ex), x_tip, min(arc_ix)]
        tip_y = [min(arc_ey), y_tip, min(arc_iy)]
        self.ax.plot(tip_x, tip_y, "k-", linewidth=lw)

    def _draw_loss_arc(self, pos_top, lim_top, r_i, r_e, fr_loss, lw):
        """Draw loss arc following R logic"""
        # Internal arc
        angles = np.linspace(0, math.pi / 2, 100)
        arc_ix = pos_top + r_i * np.sin(angles)
        arc_iy = lim_top + r_i * (1 - np.cos(angles))
        self.ax.plot(arc_ix, arc_iy, "k-", linewidth=lw)

        # External arc
        arc_ex = pos_top + r_e * np.sin(angles)
        arc_ey = (lim_top + r_i) - r_e * np.cos(angles)
        self.ax.plot(arc_ex, arc_ey, "k-", linewidth=lw)


def create_methods_sankey_from_data():
    """Create Sankey plot using the BibTeX methods analysis data"""

    # Load the decade summary data
    try:
        with open("sankey_data.json", "r") as f:
            sankey_data = json.load(f)
    except FileNotFoundError:
        print("Error: sankey_data.json not found. Run bibtex_csv_generator.py first.")
        return

    # Create Sankey for each decade showing methods flow
    sankey_plotter = RSankeyPlot()

    decades = sorted(sankey_data.keys())

    for decade in decades[-3:]:  # Last 3 decades for example
        decade_info = sankey_data[decade]
        total_papers = decade_info["total_papers"]
        methods = decade_info["methods"]

        if not methods or total_papers == 0:
            continue

        # Prepare data for Sankey
        # Input: total papers in decade
        inputs = [total_papers]

        # Losses: papers using specific methods + papers with no specific methods
        method_counts = list(methods.values())
        papers_with_methods = sum(method_counts)
        papers_without_methods = total_papers - papers_with_methods

        losses = method_counts + [papers_without_methods]

        # Labels
        input_labels = [f"{decade} Total Papers"]
        method_labels = list(methods.keys())
        loss_labels = input_labels + method_labels + ["No Specific Methods"]

        # Create plot
        print(f"Creating Sankey for {decade}...")
        fig, ax = sankey_plotter.plot_sankey(
            inputs=inputs,
            losses=losses,
            unit="papers",
            labels=loss_labels,
            format_type="png",
            filename=f"sankey_{decade}",
        )

        plt.title(f"Decision Analysis Methods Flow - {decade}", fontsize=16, pad=20)
        plt.show()
        plt.close()


def create_example_sankey():
    """Create example Sankey using the R function example data"""
    sankey_plotter = RSankeyPlot()

    # Example from R function: global carbon cycle
    inputs = [120, 92]
    losses = [45, 75, 90, 1, 6]
    unit = "GtC/yr"
    labels = [
        "GPP",
        "Ocean assimilation",
        "Ra",
        "Rh",
        "Ocean loss",
        "LULCC",
        "Fossil fuel emissions",
    ]

    fig, ax = sankey_plotter.plot_sankey(
        inputs=inputs,
        losses=losses,
        unit=unit,
        labels=labels,
        format_type="png",
        filename="example_carbon_cycle",
    )

    plt.title("Global Carbon Cycle - Example Sankey", fontsize=16, pad=20)
    plt.show()
    plt.close()


def create_methods_evolution_sankey():
    """Create overall methods evolution Sankey"""
    try:
        with open("sankey_data.json", "r") as f:
            sankey_data = json.load(f)
    except FileNotFoundError:
        print("Error: sankey_data.json not found. Run bibtex_csv_generator.py first.")
        return

    sankey_plotter = RSankeyPlot()

    # Aggregate all methods across all decades
    all_methods = {}
    total_papers = 0

    for decade, data in sankey_data.items():
        total_papers += data["total_papers"]
        for method, count in data["methods"].items():
            if method in all_methods:
                all_methods[method] += count
            else:
                all_methods[method] = count

    # Sort methods by frequency
    sorted_methods = sorted(all_methods.items(), key=lambda x: x[1], reverse=True)
    top_methods = sorted_methods[:8]  # Top 8 methods

    # Prepare Sankey data
    inputs = [total_papers]
    losses = [count for _, count in top_methods]

    # Add remaining papers
    papers_with_top_methods = sum(losses)
    remaining_papers = total_papers - papers_with_top_methods
    losses.append(remaining_papers)

    # Labels
    input_labels = ["All Papers (1900s-2020s)"]
    method_labels = [method for method, _ in top_methods]
    loss_labels = input_labels + method_labels + ["Other/No Methods"]

    fig, ax = sankey_plotter.plot_sankey(
        inputs=inputs,
        losses=losses,
        unit="papers",
        labels=loss_labels,
        format_type="png",
        filename="methods_evolution_sankey",
    )

    plt.title(
        "Decision Analysis Methods Distribution\nAcross All Decades (1900s-2020s)",
        fontsize=16,
        pad=20,
    )
    plt.show()
    plt.close()

    print(f"Created overall methods Sankey with {total_papers:,} total papers")
    print("Top methods:")
    for method, count in top_methods:
        percentage = (count / total_papers) * 100
        print(f"  {method}: {count:,} papers ({percentage:.1f}%)")


def main():
    """Main function to demonstrate different Sankey plots"""
    print("R-Style Sankey Plot Generator")
    print("=" * 40)

    # Check if we have data
    try:
        with open("sankey_data.json", "r") as f:
            data = json.load(f)
        print(f"Found data for {len(data)} decades")

        # Create methods evolution Sankey
        print("\n1. Creating overall methods evolution Sankey...")
        create_methods_evolution_sankey()

        # Create decade-specific Sankeys
        print("\n2. Creating decade-specific Sankeys...")
        create_methods_sankey_from_data()

    except FileNotFoundError:
        print("No methods data found. Creating example Sankey instead...")
        create_example_sankey()


if __name__ == "__main__":
    main()
