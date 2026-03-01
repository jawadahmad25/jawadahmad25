"""
Synthetic data generator using electromagnetic scaling laws.

Physics-informed scaling: f₁/f₂ = L₂/L₁
Generates data at target frequencies from base frequency measurements.
"""
import numpy as np
import pandas as pd
from typing import Optional


class SyntheticDataGenerator:
    """Generate synthetic antenna data using electromagnetic scaling laws."""

    def generate(
        self,
        base_df: pd.DataFrame,
        base_freq_ghz: float,
        target_freq_ghz: float,
        freq_column: str = "Frequency_GHz",
        scaling_method: str = "electromagnetic",
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Generate synthetic data at target frequency from base frequency data.

        Uses the electromagnetic scaling principle:
        f₁/f₂ = L₂/L₁ (inverse proportionality of frequency and dimensions)

        For S-parameters: frequency axis scales by f_target/f_base
        For impedance: scales proportionally
        For gain: adjusted by (f_target/f_base)² for aperture scaling
        """
        scaling_factor = target_freq_ghz / base_freq_ghz

        synthetic_df = pd.DataFrame()

        # Scale frequency axis
        synthetic_df[freq_column] = base_df[freq_column].values * scaling_factor

        # Scale each data column
        for col in base_df.columns:
            if col == freq_column:
                continue

            values = base_df[col].values.astype(float)
            col_lower = col.lower()

            if scaling_method == "electromagnetic":
                if any(kw in col_lower for kw in ["s11", "s21", "s12", "s22", "return_loss"]):
                    # S-parameters in dB: shape preserved, slight bandwidth scaling
                    synthetic_df[col] = values
                elif "gain" in col_lower:
                    # Gain scales with aperture: G_target = G_base + 20*log10(f_target/f_base)
                    gain_adjustment = 20 * np.log10(scaling_factor)
                    synthetic_df[col] = values + gain_adjustment
                elif "impedance" in col_lower or col_lower in ("z", "z_re", "z_im"):
                    # Impedance scales proportionally
                    synthetic_df[col] = values * scaling_factor
                elif "phase" in col_lower or "ang" in col_lower:
                    # Phase: scales with electrical length
                    synthetic_df[col] = values * scaling_factor
                else:
                    # Default: preserve values
                    synthetic_df[col] = values
            else:
                # Simple linear scaling
                synthetic_df[col] = values

        if output_path:
            synthetic_df.to_csv(output_path, index=False)

        return {
            "data": synthetic_df,
            "base_frequency_ghz": base_freq_ghz,
            "target_frequency_ghz": target_freq_ghz,
            "scaling_factor": scaling_factor,
            "scaling_method": scaling_method,
            "num_points": len(synthetic_df),
            "output_path": output_path,
        }

    def scale_geometry(
        self,
        geometry_params: dict[str, float],
        base_freq_ghz: float,
        target_freq_ghz: float,
    ) -> dict[str, float]:
        """
        Scale antenna geometry parameters from base to target frequency.

        Uses L_target = L_base * (f_base / f_target)
        """
        scaling_factor = base_freq_ghz / target_freq_ghz
        scaled = {}
        for param, value in geometry_params.items():
            scaled[param] = value * scaling_factor
        return scaled
