"""
Core analytical model for a 4-element phased array at 28 GHz.

This module defines the ArrayModel class which encapsulates the physical
parameters and provides methods for computing radiation characteristics
of a uniform linear array (ULA).

Key design parameters:
    - Frequency       : 28 GHz  (5G NR FR2 / mmWave)
    - Elements        : 4       (N = 4)
    - Spacing         : lambda/2 = 5.356 mm
    - Wavelength      : 10.714 mm
    - Array length    : 3 * lambda/2 = 16.07 mm
"""

import numpy as np
from .array_factor import compute_array_factor, compute_normalized_af, closed_form_af

# Physical constants
SPEED_OF_LIGHT = 299_792_458.0  # m/s


class ArrayModel:
    """Analytical model for an N-element uniform linear array.

    Parameters
    ----------
    freq_hz : float
        Operating frequency in Hz (default: 28e9).
    num_elements : int
        Number of array elements (default: 4).
    spacing_factor : float
        Element spacing as a fraction of wavelength (default: 0.5 for lambda/2).
    scan_angle_deg : float
        Desired main beam scan angle in degrees from broadside (default: 0).

    Attributes
    ----------
    wavelength : float
        Free-space wavelength in meters.
    d : float
        Inter-element spacing in meters.
    k : float
        Free-space wavenumber in rad/m.
    beta : float
        Progressive phase shift in radians for beam steering.
    """

    def __init__(self, freq_hz=28e9, num_elements=4, spacing_factor=0.5,
                 scan_angle_deg=0.0):
        self.freq_hz = freq_hz
        self.num_elements = num_elements
        self.spacing_factor = spacing_factor
        self.scan_angle_deg = scan_angle_deg

        # Derived parameters
        self.wavelength = SPEED_OF_LIGHT / self.freq_hz
        self.d = self.spacing_factor * self.wavelength
        self.k = 2.0 * np.pi / self.wavelength
        self.beta = -self.k * self.d * np.sin(np.radians(self.scan_angle_deg))
        self.array_length = (self.num_elements - 1) * self.d

    # ------------------------------------------------------------------
    # Radiation pattern methods
    # ------------------------------------------------------------------

    def array_factor(self, theta_deg, weights=None):
        """Compute the complex array factor over the given angles.

        Parameters
        ----------
        theta_deg : np.ndarray
            Angles in degrees from broadside (-90 to +90).
        weights : np.ndarray or None
            Complex excitation weights per element.

        Returns
        -------
        af : np.ndarray (complex)
        """
        theta_rad = np.radians(theta_deg)
        return compute_array_factor(
            theta_rad, self.num_elements, self.d, self.wavelength,
            self.beta, weights,
        )

    def array_factor_db(self, theta_deg, weights=None):
        """Compute the normalized array factor in dB.

        Parameters
        ----------
        theta_deg : np.ndarray
            Angles in degrees from broadside.
        weights : np.ndarray or None
            Complex excitation weights per element.

        Returns
        -------
        af_db : np.ndarray
        """
        theta_rad = np.radians(theta_deg)
        return compute_normalized_af(
            theta_rad, self.num_elements, self.d, self.wavelength,
            self.beta, weights,
        )

    def closed_form_pattern(self, theta_deg):
        """Compute the closed-form array factor for uniform excitation.

        Parameters
        ----------
        theta_deg : np.ndarray
            Angles in degrees from broadside.

        Returns
        -------
        af : np.ndarray
            Magnitude of the closed-form array factor.
        """
        theta_rad = np.radians(theta_deg)
        return closed_form_af(
            theta_rad, self.num_elements, self.d, self.wavelength, self.beta,
        )

    # ------------------------------------------------------------------
    # Performance metrics
    # ------------------------------------------------------------------

    def half_power_beamwidth(self, resolution=0.01):
        """Estimate the half-power beamwidth (HPBW) in degrees.

        Scans the normalized array factor to find the -3 dB points
        on either side of the main beam.

        Parameters
        ----------
        resolution : float
            Angular resolution in degrees for the search grid.

        Returns
        -------
        hpbw : float
            Half-power beamwidth in degrees.
        """
        theta = np.arange(-90, 90 + resolution, resolution)
        af_db = self.array_factor_db(theta)

        # Find the main beam peak index
        peak_idx = np.argmax(af_db)

        # Search left of peak for -3 dB crossing
        left_idx = peak_idx
        for i in range(peak_idx, -1, -1):
            if af_db[i] <= -3.0:
                left_idx = i
                break

        # Search right of peak for -3 dB crossing
        right_idx = peak_idx
        for i in range(peak_idx, len(af_db)):
            if af_db[i] <= -3.0:
                right_idx = i
                break

        hpbw = theta[right_idx] - theta[left_idx]
        return hpbw

    def directivity(self, resolution=0.1):
        """Estimate the array directivity in dBi.

        Computes directivity via numerical integration of the normalized
        power pattern over the visible hemisphere, assuming an isotropic
        element pattern.

            D = 4*pi * |AF_max|^2 / integral(|AF|^2 * sin(theta) dtheta dphi)

        For a linear array in the azimuth plane, the phi integration yields 2*pi.

        Parameters
        ----------
        resolution : float
            Angular step in degrees for numerical integration.

        Returns
        -------
        directivity_dbi : float
            Estimated directivity in dBi.
        """
        theta = np.linspace(0, np.pi, int(180 / resolution) + 1)
        af = closed_form_af(theta - np.pi / 2, self.num_elements, self.d,
                            self.wavelength, self.beta)
        af_power = af ** 2

        # Numerical integration using the trapezoidal rule
        integrand = af_power * np.sin(theta)
        total_power = 2.0 * np.pi * np.trapezoid(integrand, theta)

        af_max_power = np.max(af_power)
        if total_power > 0:
            D = 4.0 * np.pi * af_max_power / total_power
        else:
            D = 1.0

        return 10.0 * np.log10(D)

    def first_null_beamwidth(self, resolution=0.01):
        """Estimate the first-null beamwidth (FNBW) in degrees.

        Parameters
        ----------
        resolution : float
            Angular resolution in degrees.

        Returns
        -------
        fnbw : float
            First-null beamwidth in degrees.
        """
        theta = np.arange(-90, 90 + resolution, resolution)
        af_db = self.array_factor_db(theta)
        peak_idx = np.argmax(af_db)

        # Search for first null left of peak
        left_null = theta[0]
        for i in range(peak_idx, 0, -1):
            if af_db[i] < -40:
                left_null = theta[i]
                break

        # Search for first null right of peak
        right_null = theta[-1]
        for i in range(peak_idx, len(af_db)):
            if af_db[i] < -40:
                right_null = theta[i]
                break

        return right_null - left_null

    def sidelobe_level(self, resolution=0.01):
        """Estimate the peak sidelobe level (SLL) in dB.

        Parameters
        ----------
        resolution : float
            Angular resolution in degrees.

        Returns
        -------
        sll_db : float
            Peak sidelobe level relative to the main beam in dB (negative).
        """
        theta = np.arange(-90, 90 + resolution, resolution)
        af_db = self.array_factor_db(theta)
        peak_idx = np.argmax(af_db)

        # Find first nulls on both sides to exclude main lobe
        left_null_idx = 0
        for i in range(peak_idx, 0, -1):
            if af_db[i] < -40:
                left_null_idx = i
                break

        right_null_idx = len(af_db) - 1
        for i in range(peak_idx, len(af_db)):
            if af_db[i] < -40:
                right_null_idx = i
                break

        # Find peak in sidelobe regions
        sll = -np.inf
        if left_null_idx > 0:
            sll = max(sll, np.max(af_db[:left_null_idx]))
        if right_null_idx < len(af_db) - 1:
            sll = max(sll, np.max(af_db[right_null_idx:]))

        return sll

    def grating_lobe_angles(self):
        """Compute grating lobe directions if they exist.

        A grating lobe appears when:
            d/lambda * sin(theta_g) = d/lambda * sin(theta_0) + m
        for integer m != 0, and |sin(theta_g)| <= 1.

        Returns
        -------
        angles_deg : list of float
            Angles of grating lobes in degrees. Empty if none exist.
        """
        d_over_lambda = self.d / self.wavelength
        sin_theta0 = np.sin(np.radians(self.scan_angle_deg))
        angles = []
        for m in [-2, -1, 1, 2]:
            sin_theta_g = sin_theta0 + m / d_over_lambda
            if -1.0 <= sin_theta_g <= 1.0:
                angles.append(np.degrees(np.arcsin(sin_theta_g)))
        return angles

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self):
        """Return a formatted summary string of the array model parameters
        and performance metrics.

        Returns
        -------
        text : str
        """
        lines = [
            "=" * 62,
            "  4-Element Uniform Linear Array — Analytical Model",
            "  Operating Frequency: 28 GHz (5G NR FR2 / mmWave)",
            "=" * 62,
            "",
            "  Physical Parameters",
            "  -------------------",
            f"    Frequency              : {self.freq_hz / 1e9:.3f} GHz",
            f"    Wavelength (lambda)    : {self.wavelength * 1e3:.4f} mm",
            f"    Number of elements (N) : {self.num_elements}",
            f"    Spacing factor (d/λ)   : {self.spacing_factor}",
            f"    Element spacing (d)    : {self.d * 1e3:.4f} mm",
            f"    Array length           : {self.array_length * 1e3:.4f} mm",
            f"    Wavenumber (k)         : {self.k:.2f} rad/m",
            f"    Scan angle             : {self.scan_angle_deg:.1f}°",
            f"    Progressive phase (β)  : {np.degrees(self.beta):.2f}°",
            "",
            "  Performance Metrics",
            "  -------------------",
            f"    Half-power beamwidth   : {self.half_power_beamwidth():.2f}°",
            f"    First-null beamwidth   : {self.first_null_beamwidth():.2f}°",
            f"    Peak sidelobe level    : {self.sidelobe_level():.2f} dB",
            f"    Estimated directivity  : {self.directivity():.2f} dBi",
        ]

        grating = self.grating_lobe_angles()
        if grating:
            lines.append(f"    Grating lobe angles    : "
                         + ", ".join(f"{a:.1f}°" for a in grating))
        else:
            lines.append("    Grating lobes          : None (d ≤ λ/2)")

        # Theoretical cross-checks
        lines += [
            "",
            "  Theoretical Reference (uniform weights, broadside)",
            "  --------------------------------------------------",
            f"    HPBW ≈ 0.886·λ/(N·d)     = "
            f"{np.degrees(0.886 * self.wavelength / (self.num_elements * self.d)):.2f}°",
            f"    Directivity ≈ N           = "
            f"{10 * np.log10(self.num_elements):.2f} dBi  (ideal isotropic elements)",
            f"    Max SLL (uniform)         ≈ −13.26 dB",
            "",
            "=" * 62,
        ]

        return "\n".join(lines)
