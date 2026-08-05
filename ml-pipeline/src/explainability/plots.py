"""Generates SHAP summary/waterfall plots and saves them for the paper/dashboard."""

from pathlib import Path
import shap
import matplotlib.pyplot as plt

PLOT_DIR = Path(__file__).parent.parent / "models" / "model_registry"


def save_summary_plot(shap_values, X, filename: str = "shap_summary.png"):
    plt.figure()
    shap.summary_plot(shap_values, X, show=False)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()


def save_bar_plot(shap_values, X, filename: str = "shap_bar.png"):
    plt.figure()
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()


def save_waterfall_plot(explainer, shap_values_row, filename: str = "shap_waterfall.png"):
    plt.figure()
    shap.plots.waterfall(shap_values_row, show=False)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()
