#!/usr/bin/env python3
"""Create publication figures from the frozen aggregate results."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

BLUE = "#1f4e79"
LIGHT_BLUE = "#dceaf7"
PALE = "#f4f6f8"
DARK = "#1f2933"
ORANGE = "#c65d21"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "DejaVu Serif"],
    "font.size": 8,
    "axes.titlesize": 8.5,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def box(ax, x, y, w, h, title, detail="", fill=PALE, edge=BLUE):
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.0, facecolor=fill, edgecolor=edge,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * (0.62 if detail else 0.5), title,
            ha="center", va="center", color=DARK, fontsize=7.4, weight="bold")
    if detail:
        ax.text(x + w / 2, y + h * 0.28, detail, ha="center", va="center",
                color=DARK, fontsize=6.3)
    return patch


def arrow(ax, start, end, color=BLUE):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=8,
                                 linewidth=0.9, color=color, shrinkA=2, shrinkB=2))


def architecture():
    fig, ax = plt.subplots(figsize=(3.35, 4.55))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    w, h, x = 0.78, 0.092, 0.11
    ys = [0.88, 0.745, 0.61, 0.475, 0.34, 0.205, 0.07]
    labels = [
        ("React / TypeScript interface", "case input, history, evidence drawer"),
        ("FastAPI service + SQLite", "validation, immutable versions, export"),
        ("Pinned Qwen3-4B target", "original + every omission + recheck"),
        ("Typed evidence contract", "spans, hashes, labels, counts, scope"),
        ("Qwen3-1.7B communicator", "simple and technical views"),
        ("Structural + NLI checks", "one repair, then complete recheck"),
        ("Explicit release status", "generated pair or labelled template"),
    ]
    fills = [LIGHT_BLUE, PALE, LIGHT_BLUE, "#e8f2e8", LIGHT_BLUE, "#fff0e6", "#e8f2e8"]
    for y, (title, detail), fill in zip(ys, labels, fills):
        box(ax, x, y, w, h, title, detail, fill=fill)
    for upper, lower in zip(ys[:-1], ys[1:]):
        arrow(ax, (0.5, upper), (0.5, lower + h))

    ax.text(0.02, 0.69, "local\nonly", rotation=90, ha="center", va="center",
            fontsize=6.4, color=BLUE, weight="bold")
    ax.plot([0.045, 0.045], [0.08, 0.96], color=BLUE, linewidth=0.8)
    ax.text(0.96, 0.25, "fail\nclosed", rotation=90, ha="center", va="center",
            fontsize=6.4, color=ORANGE, weight="bold")
    ax.plot([0.94, 0.94], [0.07, 0.39], color=ORANGE, linewidth=0.8)

    fig.tight_layout(pad=0.15)
    fig.savefig(FIGURES / "figure_1_architecture.png", dpi=400, bbox_inches="tight")
    fig.savefig(FIGURES / "figure_1_architecture.pdf", bbox_inches="tight")
    plt.close(fig)


def outcomes():
    fig, axes = plt.subplots(3, 1, figsize=(3.35, 4.65), gridspec_kw={"height_ratios": [1, 1, 1]})

    splits = ["Feasibility\n(n=24)", "Development\n(n=40)", "Held-out\n(n=60)"]
    accuracy = [66.67, 72.50, 78.33]
    axes[0].bar(splits, accuracy, color=["#9fbad0", "#5f8fb5", BLUE], width=0.58)
    axes[0].set_ylim(0, 100)
    axes[0].set_ylabel("Accuracy (%)")
    axes[0].set_title("(a) Diagnostic option accuracy", loc="left", weight="bold")
    axes[0].grid(axis="y", color="#d9dde1", linewidth=0.5)
    for i, value in enumerate(accuracy):
        axes[0].text(i, value + 2.2, f"{value:.2f}", ha="center", fontsize=7)

    categories = ["Changed\nomissions", "Cases with\nany change", "Selected\nrechecks"]
    values = [13.27, 53.33, 100.0]
    axes[1].bar(categories, values, color=[ORANGE, "#d89569", "#4f8a4f"], width=0.58)
    axes[1].set_ylim(0, 112)
    axes[1].set_ylabel("Held-out (%)")
    axes[1].set_title("(b) Omission audit outcomes", loc="left", weight="bold")
    axes[1].grid(axis="y", color="#d9dde1", linewidth=0.5)
    for i, value in enumerate(values):
        axes[1].text(i, value + 2.5, f"{value:.2f}", ha="center", fontsize=7)

    controls = ["Intended-supported\n(n=240)", "Intended-faulty\n(n=480)"]
    rejected = [100, 100]
    axes[2].barh(np.arange(2), rejected, color=[ORANGE, "#6b7280"], height=0.48)
    axes[2].set_yticks(np.arange(2), controls)
    axes[2].set_xlim(0, 108)
    axes[2].set_xlabel("Rejected by frozen checker (%)")
    axes[2].set_title("(c) Verifier collapse on construction controls", loc="left", weight="bold")
    axes[2].grid(axis="x", color="#d9dde1", linewidth=0.5)
    for i, value in enumerate(rejected):
        axes[2].text(value - 2, i, "100%", ha="right", va="center", color="white",
                     fontsize=7, weight="bold")

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_axisbelow(True)
    fig.tight_layout(h_pad=1.15, pad=0.25)
    fig.savefig(FIGURES / "figure_2_results.png", dpi=400, bbox_inches="tight")
    fig.savefig(FIGURES / "figure_2_results.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    outcomes()
    print(f"Wrote figures to {FIGURES}")
