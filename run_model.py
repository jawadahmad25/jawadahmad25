#!/usr/bin/env python3
"""
Run the analytical model for a 4-element uniform linear array at 28 GHz.

This script:
  1. Prints a full parameter/performance summary.
  2. Generates polar and rectangular radiation pattern plots.
  3. Compares broadside vs. scanned beam configurations.
  4. Saves all figures to the ``figures/`` directory.

Usage
-----
    python run_model.py            # default broadside array
    python run_model.py --scan 15  # steer the beam to 15° from broadside

Requirements
------------
    numpy, matplotlib  (pip install numpy matplotlib)
"""

import argparse
import os
import numpy as np

# Attempt to import matplotlib; allow headless execution
try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend for saving figures
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from array_model import ArrayModel


FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")


def ensure_figures_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_rectangular(model, theta, af_db, filename="rectangular_pattern.png"):
    """Save a rectangular (Cartesian) radiation pattern plot."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(theta, af_db, linewidth=1.5, color="#1f77b4")
    ax.set_xlabel("Angle from broadside (degrees)", fontsize=12)
    ax.set_ylabel("Normalized Array Factor (dB)", fontsize=12)
    ax.set_title(
        f"{model.num_elements}-Element ULA at {model.freq_hz/1e9:.0f} GHz "
        f"(d = λ/2, scan = {model.scan_angle_deg:.0f}°)",
        fontsize=13,
    )
    ax.set_xlim(-90, 90)
    ax.set_ylim(-40, 3)
    ax.axhline(-3, color="red", linestyle="--", linewidth=0.8, label="-3 dB (HPBW)")
    ax.axhline(-13.26, color="orange", linestyle="--", linewidth=0.8,
               label="-13.26 dB (theoretical SLL)")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_polar(model, theta_deg, af_db, filename="polar_pattern.png"):
    """Save a polar radiation pattern plot."""
    theta_rad = np.radians(theta_deg)
    # Clamp for polar display
    af_display = np.clip(af_db, -40, 0)

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"projection": "polar"})
    ax.plot(theta_rad, af_display + 40, linewidth=1.5, color="#d62728")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_thetamin(-90)
    ax.set_thetamax(90)
    ax.set_rlabel_position(45)
    ax.set_rticks([0, 10, 20, 30, 37, 40])
    ax.set_yticklabels(["-40", "-30", "-20", "-10", "-3", "0 dB"])
    ax.set_title(
        f"{model.num_elements}-Element ULA Polar Pattern\n"
        f"{model.freq_hz/1e9:.0f} GHz, d = λ/2",
        fontsize=13, pad=20,
    )
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_beam_steering_comparison(filename="beam_steering_comparison.png"):
    """Plot array factor for several scan angles on one figure."""
    scan_angles = [0, 15, 30, 45]
    theta = np.linspace(-90, 90, 3601)

    fig, ax = plt.subplots(figsize=(10, 5))
    for sa in scan_angles:
        m = ArrayModel(scan_angle_deg=sa)
        af_db = m.array_factor_db(theta)
        ax.plot(theta, af_db, linewidth=1.2, label=f"scan = {sa}°")

    ax.set_xlabel("Angle from broadside (degrees)", fontsize=12)
    ax.set_ylabel("Normalized AF (dB)", fontsize=12)
    ax.set_title("Beam Steering — 4-Element ULA at 28 GHz (d = λ/2)", fontsize=13)
    ax.set_xlim(-90, 90)
    ax.set_ylim(-40, 3)
    ax.axhline(-3, color="gray", linestyle=":", linewidth=0.7)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_element_spacing_study(filename="spacing_study.png"):
    """Compare radiation patterns for different d/lambda ratios."""
    spacings = [0.25, 0.5, 0.75, 1.0]
    theta = np.linspace(-90, 90, 3601)

    fig, ax = plt.subplots(figsize=(10, 5))
    for sf in spacings:
        m = ArrayModel(spacing_factor=sf)
        af_db = m.array_factor_db(theta)
        ax.plot(theta, af_db, linewidth=1.2, label=f"d = {sf}λ")

    ax.set_xlabel("Angle from broadside (degrees)", fontsize=12)
    ax.set_ylabel("Normalized AF (dB)", fontsize=12)
    ax.set_title("Element Spacing Study — 4-Element ULA at 28 GHz", fontsize=13)
    ax.set_xlim(-90, 90)
    ax.set_ylim(-40, 3)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="4-Element Array Analytical Model at 28 GHz",
    )
    parser.add_argument(
        "--scan", type=float, default=0.0,
        help="Main beam scan angle in degrees from broadside (default: 0)",
    )
    parser.add_argument(
        "--no-plots", action="store_true",
        help="Skip generating plots (useful if matplotlib is unavailable)",
    )
    args = parser.parse_args()

    # Build and summarize the model
    model = ArrayModel(
        freq_hz=28e9,
        num_elements=4,
        spacing_factor=0.5,
        scan_angle_deg=args.scan,
    )

    print(model.summary())

    # Generate plots
    if args.no_plots or not HAS_MPL:
        if not HAS_MPL:
            print("\n  [matplotlib not installed — skipping plots]")
        return

    ensure_figures_dir()
    theta = np.linspace(-90, 90, 3601)
    af_db = model.array_factor_db(theta)

    print("\nGenerating figures …")
    plot_rectangular(model, theta, af_db)
    plot_polar(model, theta, af_db)
    plot_beam_steering_comparison()
    plot_element_spacing_study()
    print("Done.\n")


if __name__ == "__main__":
    main()
