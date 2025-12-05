#!/usr/bin/env python3
"""
Methods Sankey Plot Creator
Following the structure and logic of plot_sankey.R for decision analysis methods

This creates Sankey diagrams showing the flow of papers from decades into different
method categories, with proper scaling and labeling following the R function structure.
"""

import json
import math
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


class MethodsSankeyPlotter:
    """Creates Sankey plots for methods analysis following R plot_sankey structure"""

    def __init__(self):
        self.fig = None
        self.ax = None

    def plot_methods_sankey(
        self,
        decade_data: Dict,
        decade: str,
        format_type: str = "png",
        filename: str = None,
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create Sankey plot for a specific decade's methods

        Args:
            decade_data: Dictionary with 'total_papers' and 'methods'
            decade: Decade string (e.g., '2010s')
            format_type: Output format ('plot', 'png', 'pdf', 'svg')
            filename: Output filename (optional)
        """

        total_papers = decade_data["total_papers"]
        methods = decade_data["methods"]

        if total_papers == 0:
            print(f"No papers found for {decade}")
            return None, None

        # Prepare data following R function structure
        # Input: total papers in decade
        inputs = [total_papers]

        # Sort methods by count (descending)
        sorted_methods = sorted(methods.items(), key=lambda x: x[1], reverse=True)

        # Take top methods that represent significant portion
        top_methods = []
        total_method_papers = 0

        for method, count in sorted_methods:
            if count > 0 and len(top_methods) < 8:  # Limit to top 8 for clarity
                top_methods.append((method, count))
                total_method_papers += count

        # Calculate remaining papers (no specific methods or other methods)
        remaining_papers = total_papers - total_method_papers

        # Losses: method counts + remaining
        losses = [count for _, count in top_methods]
        if remaining_papers > 0:
            losses.append(remaining_papers)

        # Labels following R function convention
        labels = [f"{decade} ({total_papers} papers)"]  # Input label
        labels.extend([method for method, _ in top_methods])  # Method labels
        if remaining_papers > 0:
            labels.append("No specific methods")  # Remaining label

        # Create Sankey following R function logic
        return self._create_sankey_plot(
            inputs=inputs,
            losses=losses,
            unit="papers",
            labels=labels,
            title=f"Decision Analysis Methods - {decade}",
            format_type=format_type,
            filename=filename or f"methods_sankey_{decade.lower()}",
        )

    def _create_sankey_plot(
        self,
        inputs: List[float],
        losses: List[float],
        unit: str,
        labels: List[str],
        title: str,
        format_type: str = "png",
        filename: str = "sankey",
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Create Sankey plot following R plot_sankey structure"""

        # Calculate fractional values
        total_inputs = sum(inputs)
        fr_losses = [loss / total_inputs for loss in losses]
        fr_inputs = [inp / total_inputs for inp in inputs]

        # Calculate plot dimensions following R logic
        lim_top, pos_top, max_y, lim_bot, pos_bot = self._calculate_dimensions(
            fr_inputs, fr_losses
        )

        # Determine plot boundaries
        max_x = self._calculate_max_x(pos_top, pos_bot, lim_top, fr_losses)
        min_y = (lim_top - fr_losses[-1]) - max(0.015, abs(fr_losses[-1] / 4))
        max_y = max_y * 2

        # Create figure with appropriate size
        fig_width = max(14, (max_x + 3) * 1.5)
        fig_height = max(10, fig_width * 0.7)

        self.fig, self.ax = plt.subplots(1, 1, figsize=(fig_width, fig_height))
        self.ax.set_xlim(-2, max_x + 2)
        self.ax.set_ylim(min_y - 0.1, max_y + 0.1)
        self.ax.axis("off")

        # Draw Sankey following R structure
        self._draw_sankey_elements(
            inputs,
            losses,
            fr_inputs,
            fr_losses,
            labels,
            unit,
            lim_top,
            pos_top,
            lim_bot,
            pos_bot,
        )

        # Add title
        self.ax.set_title(title, fontsize=18, fontweight="bold", pad=20)

        # Save or display
        plt.tight_layout()

        if format_type != "plot":
            if format_type == "png":
                plt.savefig(
                    f"{filename}.png",
                    dpi=300,
                    bbox_inches="tight",
                    facecolor="white",
                    edgecolor="none",
                )
            elif format_type == "pdf":
                plt.savefig(
                    f"{filename}.pdf",
                    bbox_inches="tight",
                    facecolor="white",
                    edgecolor="none",
                )
            elif format_type == "svg":
                plt.savefig(
                    f"{filename}.svg",
                    bbox_inches="tight",
                    facecolor="white",
                    edgecolor="none",
                )

        return self.fig, self.ax

    def _calculate_dimensions(
        self, fr_inputs: List[float], fr_losses: List[float]
    ) -> Tuple:
        """Calculate plot dimensions following R logic"""
        lim_top = fr_inputs[0]
        pos_top = 0.4
        max_y = 0
        lim_bot = 0
        pos_bot = 0.1

        # Handle multiple inputs (if any)
        if len(fr_inputs) > 1:
            for j in range(1, len(fr_inputs)):
                r_i = max(0.07, abs(fr_inputs[j] / 2))
                r_e = r_i + abs(fr_inputs[j])
                new_pos_b = pos_bot + r_e * math.sin(math.pi / 4) + 0.01
                pos_bot = new_pos_b
                lim_bot = lim_bot - fr_inputs[j]

        pos_top = pos_bot + 0.4

        # Calculate positions for losses
        for i in range(len(fr_losses) - 1):
            r_i = max(0.07, abs(fr_losses[i] / 2))
            r_e = r_i + abs(fr_losses[i])
            ar_top = max(0.04, 0.8 * fr_losses[i])
            if ar_top > max_y:
                max_y = ar_top
            lim_top = lim_top - fr_losses[i]
            new_pos = pos_top + r_e + 0.01
            pos_top = new_pos

        return lim_top, pos_top, max_y, lim_bot, pos_bot

    def _calculate_max_x(
        self, pos_top: float, pos_bot: float, lim_top: float, fr_losses: List[float]
    ) -> float:
        """Calculate maximum x dimension"""
        new_pos = max(pos_top, pos_bot) + max(0.05 * lim_top, 0.05)
        new_pos = new_pos + 0.8 * (lim_top - fr_losses[-1])
        return new_pos

    def _draw_sankey_elements(
        self,
        inputs: List[float],
        losses: List[float],
        fr_inputs: List[float],
        fr_losses: List[float],
        labels: List[str],
        unit: str,
        lim_top: float,
        pos_top: float,
        lim_bot: float,
        pos_bot: float,
    ):
        """Draw all Sankey elements following R structure"""

        lw = 3  # Line width

        # Reset positions for drawing
        lim_top = fr_inputs[0]
        lim_bot = 0

        # Draw main input arrow (first input)
        self._draw_main_input_arrow(fr_inputs[0], labels[0], inputs[0], unit, lw)

        # Calculate middle position
        pos_mid = pos_bot + (pos_top - pos_bot) / 2

        # Draw connection lines
        self._draw_connection_lines(
            pos_top, pos_bot, pos_mid, fr_inputs[0], lim_bot, fr_losses[-1], lw
        )

        # Draw loss arrows
        self._draw_loss_arrows(
            pos_top, lim_top, fr_losses, losses, labels, inputs, unit, lw
        )

        # Draw final output arrow
        self._draw_final_arrow(
            pos_top,
            pos_bot,
            pos_mid,
            lim_top,
            fr_losses,
            losses[-1],
            labels[-1],
            unit,
            lw,
        )

        # Draw center reference line
        self._draw_center_line(
            pos_mid, fr_inputs[0], lim_bot, lim_top, fr_losses[-1], lw
        )

    def _draw_main_input_arrow(
        self, fr_input: float, label: str, input_val: float, unit: str, lw: int
    ):
        """Draw the main input arrow"""
        # Arrow shape
        arrow_x = [0.1, 0, 0.05, 0, 0.4]
        arrow_y = [0, 0, fr_input / 2, fr_input, fr_input]
        self.ax.plot(arrow_x, arrow_y, "k-", linewidth=lw)

        # Label
        input_label = f"{label}: {input_val:,} {unit} ({round(100 * fr_input, 1)}%)"
        fontsize = max(10, min(14, fr_input * 25))
        self.ax.text(
            0,
            fr_input / 2,
            input_label,
            fontsize=fontsize,
            ha="right",
            va="center",
            fontweight="bold",
        )

    def _draw_connection_lines(
        self,
        pos_top: float,
        pos_bot: float,
        pos_mid: float,
        fr_input: float,
        lim_bot: float,
        fr_loss_last: float,
        lw: int,
    ):
        """Draw connection lines between input and outputs"""
        # Top line
        self.ax.plot([0.4, pos_top], [fr_input, fr_input], "k-", linewidth=lw)

        # Bottom line
        self.ax.plot([pos_bot, pos_mid], [lim_bot, lim_bot], "k-", linewidth=lw)

    def _draw_loss_arrows(
        self,
        pos_top: float,
        lim_top: float,
        fr_losses: List[float],
        losses: List[float],
        labels: List[str],
        inputs: List[float],
        unit: str,
        lw: int,
    ):
        """Draw arrows for each loss/output method"""

        current_lim_top = lim_top
        current_pos_top = pos_top

        for i in range(len(losses) - 1):  # Exclude final loss
            r_i = max(0.07, abs(fr_losses[i] / 2))
            r_e = r_i + abs(fr_losses[i])

            # Draw curved connection
            self._draw_output_arc(current_pos_top, current_lim_top, r_i, r_e, lw)

            # Draw arrow tip
            ar_edge = max(0.02, r_i / 3)
            ar_top = max(0.05, 0.9 * fr_losses[i])

            tip_x = [
                current_pos_top + r_i,
                current_pos_top + r_i - ar_edge,
                current_pos_top + r_i + fr_losses[i] / 2,
                current_pos_top + r_i + fr_losses[i] + ar_edge,
                current_pos_top + r_i + fr_losses[i],
            ]
            tip_y = [
                current_lim_top + r_i,
                current_lim_top + r_i,
                current_lim_top + r_i + ar_top,
                current_lim_top + r_i,
                current_lim_top + r_i,
            ]
            self.ax.plot(tip_x, tip_y, "k-", linewidth=lw)

            # Add label
            txt_x = current_pos_top + r_i + fr_losses[i] / 2
            txt_y = current_lim_top + r_i + ar_top + 0.03

            # Create method label
            method_label = labels[i + len(inputs)]
            if len(method_label) > 25:  # Truncate long labels
                method_label = method_label[:22] + "..."

            full_label = f"{method_label}\n{losses[i]:,} {unit}\n({round(100 * fr_losses[i], 1)}%)"
            fontsize = max(8, min(12, fr_losses[i] * 20))

            self.ax.text(
                txt_x,
                txt_y,
                full_label,
                fontsize=fontsize,
                ha="center",
                va="bottom",
                rotation=0,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
            )

            # Update positions
            current_lim_top = current_lim_top - fr_losses[i]
            new_pos = current_pos_top + r_e + 0.02

            # Draw connection to next position
            self.ax.plot(
                [current_pos_top, new_pos],
                [current_lim_top, current_lim_top],
                "k-",
                linewidth=lw,
            )
            current_pos_top = new_pos

    def _draw_output_arc(
        self, pos_top: float, lim_top: float, r_i: float, r_e: float, lw: int
    ):
        """Draw curved arc for output connection"""
        angles = np.linspace(0, math.pi / 2, 50)

        # Inner arc
        arc_ix = pos_top + r_i * np.sin(angles)
        arc_iy = lim_top + r_i * (1 - np.cos(angles))
        self.ax.plot(arc_ix, arc_iy, "k-", linewidth=lw)

        # Outer arc
        arc_ex = pos_top + r_e * np.sin(angles)
        arc_ey = (lim_top + r_i) - r_e * np.cos(angles)
        self.ax.plot(arc_ex, arc_ey, "k-", linewidth=lw)

    def _draw_final_arrow(
        self,
        pos_top: float,
        pos_bot: float,
        pos_mid: float,
        lim_top: float,
        fr_losses: List[float],
        final_loss: float,
        final_label: str,
        unit: str,
        lw: int,
    ):
        """Draw the final output arrow"""
        # Calculate final position
        new_pos = max(pos_top, pos_bot) + max(0.05 * lim_top, 0.05)

        # Draw connection lines
        current_lim_top = lim_top
        for fl in fr_losses[:-1]:
            current_lim_top -= fl

        self.ax.plot(
            [pos_top, new_pos], [current_lim_top, current_lim_top], "k-", linewidth=lw
        )
        self.ax.plot(
            [pos_mid, new_pos],
            [current_lim_top - fr_losses[-1], current_lim_top - fr_losses[-1]],
            "k-",
            linewidth=lw,
        )

        # Draw final arrowhead
        arrow_size = max(0.04, 0.8 * fr_losses[-1])
        arrow_x = [new_pos, new_pos, new_pos + arrow_size, new_pos, new_pos]
        arrow_y = [
            current_lim_top,
            current_lim_top + max(0.02, abs(fr_losses[-1] / 6)),
            current_lim_top - fr_losses[-1] / 2,
            current_lim_top - fr_losses[-1] - max(0.02, abs(fr_losses[-1] / 6)),
            current_lim_top - fr_losses[-1],
        ]
        self.ax.plot(arrow_x, arrow_y, "k-", linewidth=lw)

        # Final label
        final_pos = new_pos + arrow_size
        loss_label = (
            f"{final_label}\n{final_loss:,} {unit}\n({round(100 * fr_losses[-1], 1)}%)"
        )
        fontsize = max(10, min(14, fr_losses[-1] * 20))

        self.ax.text(
            final_pos + 0.05,
            current_lim_top - fr_losses[-1] / 2,
            loss_label,
            fontsize=fontsize,
            ha="left",
            va="center",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7),
        )

    def _draw_center_line(
        self,
        pos_mid: float,
        fr_input: float,
        lim_bot: float,
        lim_top: float,
        fr_loss_last: float,
        lw: int,
    ):
        """Draw center reference line"""
        current_lim_top = lim_top - sum([fl for fl in [fr_loss_last]]) + fr_loss_last

        if lim_bot < (current_lim_top - fr_loss_last):
            y_end = lim_bot
        else:
            y_end = current_lim_top - fr_loss_last

        self.ax.plot(
            [pos_mid, pos_mid], [fr_input, y_end], "k--", linewidth=lw - 1, alpha=0.5
        )


def create_all_decade_sankeys():
    """Create Sankey plots for all decades with methods data"""

    # Load data
    try:
        with open("sankey_data.json", "r") as f:
            sankey_data = json.load(f)
    except FileNotFoundError:
        print("Error: sankey_data.json not found. Run bibtex_csv_generator.py first.")
        return

    plotter = MethodsSankeyPlotter()

    # Create output directory
    os.makedirs("sankey_plots", exist_ok=True)

    decades_with_methods = {}

    # Filter decades with meaningful method data
    for decade, data in sankey_data.items():
        total_papers = data["total_papers"]
        methods = data["methods"]
        method_papers = sum(methods.values())

        if (
            total_papers > 50 and method_papers > 0
        ):  # Only decades with substantial data
            decades_with_methods[decade] = data

    print(f"Creating Sankey plots for {len(decades_with_methods)} decades...")

    for decade, data in sorted(decades_with_methods.items()):
        print(f"  Creating Sankey for {decade}...")

        fig, ax = plotter.plot_methods_sankey(
            decade_data=data,
            decade=decade,
            format_type="png",
            filename=f"sankey_plots/methods_flow_{decade.lower()}",
        )

        if fig:
            plt.show()
            plt.close()

    print(f"\nSankey plots saved in 'sankey_plots/' directory")

    # Create summary
    print(f"\nDecade Summary:")
    for decade in sorted(decades_with_methods.keys()):
        data = decades_with_methods[decade]
        total = data["total_papers"]
        method_count = len([m for m in data["methods"].values() if m > 0])
        method_papers = sum(data["methods"].values())

        print(
            f"  {decade}: {total:,} papers, {method_papers:,} with methods, {method_count} method types"
        )


def create_evolution_summary_sankey():
    """Create overall evolution summary Sankey"""

    try:
        with open("sankey_data.json", "r") as f:
            sankey_data = json.load(f)
    except FileNotFoundError:
        print("Error: sankey_data.json not found.")
        return

    plotter = MethodsSankeyPlotter()

    # Aggregate data across all decades
    total_papers = sum(data["total_papers"] for data in sankey_data.values())
    all_methods = {}

    for data in sankey_data.values():
        for method, count in data["methods"].items():
            all_methods[method] = all_methods.get(method, 0) + count

    # Create summary data structure
    summary_data = {"total_papers": total_papers, "methods": all_methods}

    print("Creating evolution summary Sankey...")
    fig, ax = plotter.plot_methods_sankey(
        decade_data=summary_data,
        decade="All Decades (1900s-2020s)",
        format_type="png",
        filename="sankey_plots/methods_evolution_summary",
    )

    if fig:
        plt.show()
        plt.close()

    print(f"Evolution summary: {total_papers:,} total papers")
    print("Top methods across all decades:")
    for method, count in sorted(all_methods.items(), key=lambda x: x[1], reverse=True)[
        :8
    ]:
        percentage = (count / total_papers) * 100
        print(f"  {method}: {count:,} ({percentage:.1f}%)")


def main():
    """Main function to create all Sankey plots"""
    print("Methods Sankey Plot Creator")
    print("=" * 50)

    # Create decade-specific Sankeys
    create_all_decade_sankeys()

    print("\n" + "=" * 50)

    # Create evolution summary
    create_evolution_summary_sankey()

    print("\nAll Sankey plots completed!")
    print("Files saved in 'sankey_plots/' directory")


if __name__ == "__main__":
    main()
