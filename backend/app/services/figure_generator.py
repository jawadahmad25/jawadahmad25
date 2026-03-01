"""
Publication-quality figure generator for antenna research.

Generates IEEE/Elsevier compliant plots:
- S-parameter plots (S11, S21 vs frequency)
- Radiation patterns (polar)
- Gain vs angle (Cartesian)
- ML model comparison charts
- Actual vs predicted scatter plots
- RSSI vs distance
- Rain attenuation curves
- Channel capacity analysis
"""
import io
import base64
from pathlib import Path
from typing import Optional, Any

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import plotly.graph_objects as go
import plotly.io as pio


# IEEE-compliant defaults
IEEE_STYLE = {
    "width_inches": 3.5,
    "height_inches": 2.625,
    "dpi": 600,
    "font_family": "serif",
    "font_size": 10,
    "line_width": 1.5,
    "grid": True,
    "grid_alpha": 0.3,
    "marker_size": 4,
}

DEFAULT_COLORS = [
    "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
]

DEFAULT_MARKERS = ["o", "s", "^", "D", "v", "<", ">", "p"]


class FigureGenerator:
    """Generate publication-quality figures for antenna research."""

    def __init__(self, style: str = "ieee"):
        self.style = IEEE_STYLE.copy()
        self._setup_matplotlib()

    def _setup_matplotlib(self):
        """Configure matplotlib for publication quality."""
        plt.rcParams.update({
            "font.family": self.style["font_family"],
            "font.size": self.style["font_size"],
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.minor.width": 0.5,
            "ytick.minor.width": 0.5,
            "lines.linewidth": self.style["line_width"],
            "lines.markersize": self.style["marker_size"],
            "legend.fontsize": 8,
            "legend.framealpha": 0.9,
            "figure.dpi": 150,
            "savefig.dpi": self.style["dpi"],
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        })

    def generate(
        self,
        plot_type: str,
        data: dict[str, Any],
        config: Optional[dict] = None,
        output_path: Optional[str] = None,
        export_format: str = "png",
    ) -> dict:
        """Generate a figure based on plot type and data."""
        cfg = {**self.style, **(config or {})}

        generators = {
            "s_parameter": self._plot_s_parameter,
            "radiation_pattern": self._plot_radiation_pattern,
            "gain_vs_angle": self._plot_gain_vs_angle,
            "ml_comparison": self._plot_ml_comparison,
            "scatter": self._plot_scatter,
            "actual_vs_predicted": self._plot_actual_vs_predicted,
            "rssi_distance": self._plot_rssi_distance,
            "rain_attenuation": self._plot_rain_attenuation,
            "channel_capacity": self._plot_channel_capacity,
            "feature_importance": self._plot_feature_importance,
            "training_curves": self._plot_training_curves,
        }

        generator = generators.get(plot_type)
        if generator is None:
            raise ValueError(f"Unknown plot type: {plot_type}. Available: {list(generators.keys())}")

        fig = generator(data, cfg)

        # Save or encode
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, format=export_format, dpi=cfg["dpi"])
            preview = self._fig_to_base64(fig)
            plt.close(fig)
            return {"file_path": output_path, "preview_base64": preview}
        else:
            preview = self._fig_to_base64(fig)
            plt.close(fig)
            return {"preview_base64": preview}

    def generate_plotly(
        self,
        plot_type: str,
        data: dict[str, Any],
        config: Optional[dict] = None,
    ) -> dict:
        """Generate an interactive Plotly figure (for frontend)."""
        cfg = {**self.style, **(config or {})}

        generators = {
            "s_parameter": self._plotly_s_parameter,
            "scatter": self._plotly_scatter,
            "ml_comparison": self._plotly_ml_comparison,
        }

        generator = generators.get(plot_type, self._plotly_s_parameter)
        fig = generator(data, cfg)

        return {"plotly_json": pio.to_json(fig)}

    # ── Matplotlib generators ──

    def _plot_s_parameter(self, data: dict, cfg: dict) -> plt.Figure:
        """S-parameter plot (S11, S21 vs frequency)."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        freq = np.array(data["frequency"])
        colors = data.get("colors", DEFAULT_COLORS)
        markers = data.get("markers", DEFAULT_MARKERS)
        labels = data.get("labels", [])

        for i, (key, values) in enumerate(data.get("traces", {}).items()):
            label = labels[i] if i < len(labels) else key
            color = colors[i % len(colors)]
            marker = markers[i % len(markers)] if data.get("show_markers", False) else None
            ax.plot(freq, values, color=color, label=label,
                    marker=marker, markevery=max(1, len(freq) // 10))

        ax.set_xlabel(data.get("x_label", "Frequency (GHz)"))
        ax.set_ylabel(data.get("y_label", "Magnitude (dB)"))
        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.yaxis.set_minor_locator(AutoMinorLocator())

        if len(data.get("traces", {})) > 1:
            ax.legend(loc=data.get("legend_position", "best"))

        fig.tight_layout()
        return fig

    def _plot_radiation_pattern(self, data: dict, cfg: dict) -> plt.Figure:
        """Polar radiation pattern plot."""
        fig, ax = plt.subplots(
            figsize=(cfg["width_inches"], cfg["width_inches"]),
            subplot_kw={"projection": "polar"},
        )

        colors = data.get("colors", DEFAULT_COLORS)

        for i, (key, trace) in enumerate(data.get("traces", {}).items()):
            theta = np.radians(np.array(trace["angles"]))
            r = np.array(trace["values"])
            ax.plot(theta, r, color=colors[i % len(colors)], label=key)

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        if data.get("title"):
            ax.set_title(data["title"], va="bottom", fontsize=cfg["font_size"])

        if len(data.get("traces", {})) > 1:
            ax.legend(loc="lower right", bbox_to_anchor=(1.3, 0))

        fig.tight_layout()
        return fig

    def _plot_gain_vs_angle(self, data: dict, cfg: dict) -> plt.Figure:
        """Gain vs angle Cartesian plot."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        angles = np.array(data["angles"])
        colors = data.get("colors", DEFAULT_COLORS)

        for i, (key, values) in enumerate(data.get("traces", {}).items()):
            ax.plot(angles, values, color=colors[i % len(colors)], label=key)

        ax.set_xlabel(data.get("x_label", "Angle (degrees)"))
        ax.set_ylabel(data.get("y_label", "Gain (dBi)"))
        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])
        if len(data.get("traces", {})) > 1:
            ax.legend(loc=data.get("legend_position", "best"))

        fig.tight_layout()
        return fig

    def _plot_ml_comparison(self, data: dict, cfg: dict) -> plt.Figure:
        """ML model comparison bar chart."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        models = data["models"]
        metrics = data["metrics"]  # e.g., {"MSE": [...], "R²": [...]}
        x = np.arange(len(models))
        width = 0.8 / len(metrics)
        colors = data.get("colors", DEFAULT_COLORS)

        for i, (metric_name, values) in enumerate(metrics.items()):
            offset = (i - len(metrics) / 2 + 0.5) * width
            ax.bar(x + offset, values, width, label=metric_name,
                   color=colors[i % len(colors)], alpha=0.85)

        ax.set_xlabel("Model")
        ax.set_ylabel(data.get("y_label", "Score"))
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=30, ha="right", fontsize=8)
        ax.legend(fontsize=8)

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"], axis="y")

        fig.tight_layout()
        return fig

    def _plot_scatter(self, data: dict, cfg: dict) -> plt.Figure:
        """Generic scatter plot."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        ax.scatter(data["x"], data["y"], s=15, alpha=0.7,
                   color=data.get("color", DEFAULT_COLORS[0]))

        ax.set_xlabel(data.get("x_label", "X"))
        ax.set_ylabel(data.get("y_label", "Y"))
        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])

        fig.tight_layout()
        return fig

    def _plot_actual_vs_predicted(self, data: dict, cfg: dict) -> plt.Figure:
        """Actual vs Predicted scatter plot with ideal line."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        y_actual = np.array(data["actual"])
        y_pred = np.array(data["predicted"])

        ax.scatter(y_actual, y_pred, s=15, alpha=0.6, color=DEFAULT_COLORS[0])

        # Ideal line
        limits = [min(y_actual.min(), y_pred.min()), max(y_actual.max(), y_pred.max())]
        margin = (limits[1] - limits[0]) * 0.05
        limits = [limits[0] - margin, limits[1] + margin]
        ax.plot(limits, limits, "r--", linewidth=1, label="Ideal")

        # R² annotation
        if "r2" in data:
            ax.annotate(f'R² = {data["r2"]:.4f}', xy=(0.05, 0.92),
                        xycoords="axes fraction", fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7))

        ax.set_xlabel(data.get("x_label", "Actual"))
        ax.set_ylabel(data.get("y_label", "Predicted"))
        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        ax.set_xlim(limits)
        ax.set_ylim(limits)
        ax.set_aspect("equal")

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])

        fig.tight_layout()
        return fig

    def _plot_rssi_distance(self, data: dict, cfg: dict) -> plt.Figure:
        """RSSI vs distance plot for V2V communications."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        distances = np.array(data["distances"])
        colors = data.get("colors", DEFAULT_COLORS)

        for i, (key, values) in enumerate(data.get("traces", {}).items()):
            ax.plot(distances, values, color=colors[i % len(colors)], label=key, marker="o",
                    markevery=max(1, len(distances) // 8), markersize=4)

        ax.set_xlabel(data.get("x_label", "Distance (m)"))
        ax.set_ylabel(data.get("y_label", "RSSI (dBm)"))
        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])
        if len(data.get("traces", {})) > 1:
            ax.legend(loc="best", fontsize=8)

        fig.tight_layout()
        return fig

    def _plot_rain_attenuation(self, data: dict, cfg: dict) -> plt.Figure:
        """Rain attenuation curves."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        rain_rates = np.array(data.get("rain_rates", []))
        colors = data.get("colors", DEFAULT_COLORS)

        for i, (key, values) in enumerate(data.get("traces", {}).items()):
            ax.plot(rain_rates, values, color=colors[i % len(colors)], label=key)

        ax.set_xlabel(data.get("x_label", "Rain Rate (mm/h)"))
        ax.set_ylabel(data.get("y_label", "Attenuation (dB/km)"))
        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])
        ax.legend(loc="best", fontsize=8)

        fig.tight_layout()
        return fig

    def _plot_channel_capacity(self, data: dict, cfg: dict) -> plt.Figure:
        """Channel capacity analysis plot."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        snr = np.array(data["snr_db"])
        colors = data.get("colors", DEFAULT_COLORS)

        for i, (key, values) in enumerate(data.get("traces", {}).items()):
            ax.plot(snr, values, color=colors[i % len(colors)], label=key)

        ax.set_xlabel(data.get("x_label", "SNR (dB)"))
        ax.set_ylabel(data.get("y_label", "Capacity (bps/Hz)"))
        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])
        ax.legend(loc="best", fontsize=8)

        fig.tight_layout()
        return fig

    def _plot_feature_importance(self, data: dict, cfg: dict) -> plt.Figure:
        """Feature importance horizontal bar chart."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        features = list(data["importance"].keys())
        values = list(data["importance"].values())

        # Sort by importance
        sorted_idx = np.argsort(values)
        features = [features[i] for i in sorted_idx]
        values = [values[i] for i in sorted_idx]

        ax.barh(features, values, color=DEFAULT_COLORS[0], alpha=0.85)
        ax.set_xlabel("Importance")

        if data.get("title"):
            ax.set_title(data["title"], fontsize=cfg["font_size"])

        fig.tight_layout()
        return fig

    def _plot_training_curves(self, data: dict, cfg: dict) -> plt.Figure:
        """Neural network training loss curves."""
        fig, ax = plt.subplots(figsize=(cfg["width_inches"], cfg["height_inches"]))

        if "train_loss" in data:
            epochs_t = [p["epoch"] for p in data["train_loss"]]
            losses_t = [p["loss"] for p in data["train_loss"]]
            ax.plot(epochs_t, losses_t, color=DEFAULT_COLORS[0], label="Train Loss")

        if "val_loss" in data:
            epochs_v = [p["epoch"] for p in data["val_loss"]]
            losses_v = [p["loss"] for p in data["val_loss"]]
            ax.plot(epochs_v, losses_v, color=DEFAULT_COLORS[1], label="Val Loss")

        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss (MSE)")
        ax.set_yscale("log")

        if cfg["grid"]:
            ax.grid(True, alpha=cfg["grid_alpha"])
        ax.legend(loc="best", fontsize=8)

        fig.tight_layout()
        return fig

    # ── Plotly generators ──

    def _plotly_s_parameter(self, data: dict, cfg: dict) -> go.Figure:
        """Interactive S-parameter plot."""
        fig = go.Figure()
        freq = data["frequency"]
        colors = data.get("colors", DEFAULT_COLORS)

        for i, (key, values) in enumerate(data.get("traces", {}).items()):
            fig.add_trace(go.Scatter(
                x=freq, y=values, name=key, mode="lines",
                line=dict(color=colors[i % len(colors)], width=2),
            ))

        fig.update_layout(
            xaxis_title=data.get("x_label", "Frequency (GHz)"),
            yaxis_title=data.get("y_label", "Magnitude (dB)"),
            title=data.get("title"),
            template="plotly_white",
            font=dict(size=12),
            legend=dict(x=0.01, y=0.01),
        )
        return fig

    def _plotly_scatter(self, data: dict, cfg: dict) -> go.Figure:
        """Interactive scatter plot."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data["x"], y=data["y"], mode="markers",
            marker=dict(size=6, opacity=0.7),
        ))
        fig.update_layout(
            xaxis_title=data.get("x_label", "X"),
            yaxis_title=data.get("y_label", "Y"),
            title=data.get("title"),
            template="plotly_white",
        )
        return fig

    def _plotly_ml_comparison(self, data: dict, cfg: dict) -> go.Figure:
        """Interactive ML comparison chart."""
        fig = go.Figure()
        colors = data.get("colors", DEFAULT_COLORS)

        for i, (metric_name, values) in enumerate(data["metrics"].items()):
            fig.add_trace(go.Bar(
                name=metric_name, x=data["models"], y=values,
                marker_color=colors[i % len(colors)],
            ))

        fig.update_layout(
            barmode="group",
            yaxis_title=data.get("y_label", "Score"),
            title=data.get("title", "Model Comparison"),
            template="plotly_white",
        )
        return fig

    def _fig_to_base64(self, fig: plt.Figure) -> str:
        """Convert matplotlib figure to base64 PNG."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
