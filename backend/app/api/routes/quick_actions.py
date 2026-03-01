"""Quick actions API routes - frequently used tools."""
from fastapi import APIRouter

from app.services.publication_tools import UnitConverter
from app.services.synthetic_data import SyntheticDataGenerator

router = APIRouter(prefix="/quick-actions", tags=["quick_actions"])
unit_converter = UnitConverter()
synthetic_gen = SyntheticDataGenerator()


@router.post("/convert-unit")
def convert_unit(
    value: float,
    from_unit: str,
    to_unit: str,
    freq_ghz: float = None,
):
    """Convert between common antenna engineering units."""
    try:
        result = unit_converter.convert(value, from_unit, to_unit, freq_ghz)
        return result
    except ValueError as e:
        return {"error": str(e)}


@router.post("/scale-geometry")
def scale_geometry(
    geometry_params: dict[str, float],
    base_freq_ghz: float,
    target_freq_ghz: float,
):
    """Scale antenna geometry parameters between frequencies."""
    scaled = synthetic_gen.scale_geometry(geometry_params, base_freq_ghz, target_freq_ghz)
    scaling_factor = base_freq_ghz / target_freq_ghz

    return {
        "original": geometry_params,
        "scaled": scaled,
        "base_freq_ghz": base_freq_ghz,
        "target_freq_ghz": target_freq_ghz,
        "scaling_factor": scaling_factor,
    }


@router.post("/sensitivity-analysis")
def sensitivity_analysis(
    base_params: dict[str, float],
    param_to_vary: str,
    variation_percent: float = 5.0,
    num_steps: int = 11,
    model_id: int = None,
):
    """
    Perform sensitivity analysis on antenna parameters.

    Returns how the varied parameter affects the output
    when varied ±variation_percent from its base value.
    """
    if param_to_vary not in base_params:
        return {"error": f"Parameter '{param_to_vary}' not in base_params"}

    import numpy as np

    base_value = base_params[param_to_vary]
    min_val = base_value * (1 - variation_percent / 100)
    max_val = base_value * (1 + variation_percent / 100)
    variations = np.linspace(min_val, max_val, num_steps).tolist()

    # Without a model, return the parameter space
    param_sets = []
    for v in variations:
        params = base_params.copy()
        params[param_to_vary] = v
        param_sets.append({
            "params": params,
            "varied_value": v,
            "percent_change": ((v - base_value) / base_value) * 100,
        })

    return {
        "parameter": param_to_vary,
        "base_value": base_value,
        "variation_percent": variation_percent,
        "variations": param_sets,
        "note": "Provide model_id to get predicted outputs for each variation",
    }


@router.get("/wavelength-calculator")
def wavelength_calculator(freq_ghz: float):
    """Calculate wavelength and related values for a given frequency."""
    wavelength_mm = unit_converter.ghz_to_wavelength_mm(freq_ghz)
    return {
        "frequency_ghz": freq_ghz,
        "frequency_mhz": freq_ghz * 1000,
        "wavelength_mm": wavelength_mm,
        "wavelength_m": wavelength_mm / 1000,
        "half_wavelength_mm": wavelength_mm / 2,
        "quarter_wavelength_mm": wavelength_mm / 4,
        "common_patch_length_mm": wavelength_mm / 2 * 0.49,  # ~0.49λ for patch
    }
