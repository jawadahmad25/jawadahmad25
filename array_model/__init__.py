"""
Analytical Model for a 4-Element Phased Array Antenna at 28 GHz.

This package provides the mathematical framework for modeling a uniform
linear array (ULA) operating at 28 GHz (5G mmWave band) with half-wavelength
inter-element spacing.
"""

from .core import ArrayModel
from .array_factor import compute_array_factor, compute_normalized_af

__all__ = ["ArrayModel", "compute_array_factor", "compute_normalized_af"]
