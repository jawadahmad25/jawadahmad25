"""
Data alignment engine for synchronizing measured and simulated antenna data.

Handles:
- Different frequency steps (e.g., 0.01 vs 0.001 GHz)
- Different frequency ranges (e.g., 26-30 vs 25-31 GHz)
- Interpolation onto a common grid
- Before/after comparison data
"""
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


class DataAlignmentEngine:
    """Aligns two datasets onto a common frequency grid."""

    def align(
        self,
        reference_df: pd.DataFrame,
        target_df: pd.DataFrame,
        ref_freq_col: str = "Frequency_GHz",
        target_freq_col: str = "Frequency_GHz",
        value_columns: Optional[list[str]] = None,
        method: str = "cubic",
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Align target data onto the reference frequency grid.

        Always interpolates higher-resolution data onto lower-resolution grid.
        Uses scipy.interpolate.interp1d with configurable interpolation method.
        """
        ref_freq = reference_df[ref_freq_col].values.astype(float)
        target_freq = target_df[target_freq_col].values.astype(float)

        # Determine overlapping frequency range
        freq_min = max(ref_freq.min(), target_freq.min())
        freq_max = min(ref_freq.max(), target_freq.max())

        if freq_min >= freq_max:
            raise ValueError(
                f"No overlapping frequency range. "
                f"Reference: {ref_freq.min():.4f}-{ref_freq.max():.4f} GHz, "
                f"Target: {target_freq.min():.4f}-{target_freq.max():.4f} GHz"
            )

        # Use reference grid within overlap
        ref_mask = (ref_freq >= freq_min) & (ref_freq <= freq_max)
        common_freq = ref_freq[ref_mask]

        # Determine which columns to interpolate
        if value_columns is None:
            target_data_cols = [c for c in target_df.columns if c != target_freq_col]
        else:
            target_data_cols = value_columns

        # Interpolate target onto reference grid
        aligned_data = {"Frequency_GHz": common_freq}

        # Add reference data columns
        ref_data_cols = [c for c in reference_df.columns if c != ref_freq_col]
        ref_mask_df = reference_df[ref_mask] if len(reference_df) == len(ref_freq) else reference_df
        for col in ref_data_cols:
            if len(ref_mask_df) == len(common_freq):
                aligned_data[f"ref_{col}"] = ref_mask_df[col].values
            else:
                # Interpolate reference too if needed
                interp_func = interp1d(
                    ref_freq, reference_df[col].values,
                    kind=method, fill_value="extrapolate", bounds_error=False,
                )
                aligned_data[f"ref_{col}"] = interp_func(common_freq)

        # Interpolate target data
        for col in target_data_cols:
            try:
                values = target_df[col].values.astype(float)
                interp_func = interp1d(
                    target_freq, values,
                    kind=method, fill_value="extrapolate", bounds_error=False,
                )
                aligned_data[f"target_{col}"] = interp_func(common_freq)
            except (ValueError, TypeError):
                continue

        aligned_df = pd.DataFrame(aligned_data)

        # Save if output path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            aligned_df.to_csv(output_path, index=False)

        # Generate comparison stats
        stats = self._compute_alignment_stats(
            ref_freq, target_freq, common_freq, ref_data_cols, target_data_cols, aligned_df
        )

        return {
            "aligned_df": aligned_df,
            "output_path": output_path,
            "stats": stats,
            "preview": self._generate_preview(aligned_df),
        }

    def align_from_files(
        self,
        reference_path: str,
        target_path: str,
        ref_parser_result: dict,
        target_parser_result: dict,
        method: str = "cubic",
        output_path: Optional[str] = None,
    ) -> dict:
        """Align two files using pre-parsed data."""
        ref_df = ref_parser_result["data"]
        target_df = target_parser_result["data"]

        ref_freq_col = ref_parser_result.get("freq_column", "Frequency_GHz")
        target_freq_col = target_parser_result.get("freq_column", "Frequency_GHz")

        return self.align(
            ref_df, target_df,
            ref_freq_col=ref_freq_col,
            target_freq_col=target_freq_col,
            method=method,
            output_path=output_path,
        )

    def _compute_alignment_stats(
        self,
        ref_freq: np.ndarray,
        target_freq: np.ndarray,
        common_freq: np.ndarray,
        ref_cols: list[str],
        target_cols: list[str],
        aligned_df: pd.DataFrame,
    ) -> dict:
        """Compute statistics about the alignment."""
        ref_step = float(np.median(np.diff(ref_freq))) if len(ref_freq) > 1 else 0
        target_step = float(np.median(np.diff(target_freq))) if len(target_freq) > 1 else 0
        common_step = float(np.median(np.diff(common_freq))) if len(common_freq) > 1 else 0

        return {
            "reference": {
                "num_points": len(ref_freq),
                "freq_min": float(ref_freq.min()),
                "freq_max": float(ref_freq.max()),
                "freq_step": ref_step,
            },
            "target": {
                "num_points": len(target_freq),
                "freq_min": float(target_freq.min()),
                "freq_max": float(target_freq.max()),
                "freq_step": target_step,
            },
            "aligned": {
                "num_points": len(common_freq),
                "freq_min": float(common_freq.min()),
                "freq_max": float(common_freq.max()),
                "freq_step": common_step,
                "num_ref_columns": len(ref_cols),
                "num_target_columns": len(target_cols),
            },
        }

    def _generate_preview(self, aligned_df: pd.DataFrame, max_rows: int = 50) -> dict:
        """Generate preview data for visualization."""
        step = max(1, len(aligned_df) // max_rows)
        preview = aligned_df.iloc[::step]

        return {
            "columns": list(preview.columns),
            "data": preview.to_dict(orient="records"),
            "total_rows": len(aligned_df),
            "preview_rows": len(preview),
        }
