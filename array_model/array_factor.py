"""
Array factor computation for a uniform linear array (ULA).

The array factor (AF) describes the far-field radiation pattern contribution
due to the spatial arrangement and excitation of the array elements, independent
of the individual element pattern.

For an N-element ULA along the z-axis with uniform spacing d:

    AF(theta) = sum_{n=0}^{N-1} w_n * exp(j * n * (k*d*cos(theta) + beta))

where:
    theta : angle from the array axis (0 to pi)
    k     : wavenumber = 2*pi / lambda
    d     : inter-element spacing
    beta  : progressive phase shift between elements
    w_n   : complex weight for the n-th element
"""

import numpy as np


def compute_array_factor(theta, num_elements, d, wavelength, beta=0.0, weights=None):
    """Compute the complex array factor for a uniform linear array.

    Parameters
    ----------
    theta : np.ndarray
        Observation angles in radians (measured from array broadside).
    num_elements : int
        Number of array elements (N).
    d : float
        Inter-element spacing in meters.
    wavelength : float
        Operating wavelength in meters.
    beta : float, optional
        Progressive phase shift in radians (default 0 for broadside).
    weights : np.ndarray or None, optional
        Complex excitation weights for each element. If None, uniform
        amplitude/phase excitation is assumed.

    Returns
    -------
    af : np.ndarray
        Complex array factor at each observation angle.
    """
    k = 2.0 * np.pi / wavelength
    psi = k * d * np.sin(theta) + beta

    if weights is None:
        weights = np.ones(num_elements)

    af = np.zeros_like(theta, dtype=complex)
    for n in range(num_elements):
        af += weights[n] * np.exp(1j * n * psi)

    return af


def compute_normalized_af(theta, num_elements, d, wavelength, beta=0.0, weights=None):
    """Compute the normalized array factor magnitude in dB.

    The array factor is normalized so the peak value is 0 dB.

    Parameters
    ----------
    theta : np.ndarray
        Observation angles in radians.
    num_elements : int
        Number of array elements.
    d : float
        Inter-element spacing in meters.
    wavelength : float
        Operating wavelength in meters.
    beta : float, optional
        Progressive phase shift in radians (default 0).
    weights : np.ndarray or None, optional
        Complex excitation weights.

    Returns
    -------
    af_db : np.ndarray
        Normalized array factor magnitude in dB.
    """
    af = compute_array_factor(theta, num_elements, d, wavelength, beta, weights)
    af_mag = np.abs(af)
    af_mag_max = np.max(af_mag)
    if af_mag_max > 0:
        af_norm = af_mag / af_mag_max
    else:
        af_norm = af_mag
    # Clip to avoid log10(0)
    af_norm = np.clip(af_norm, 1e-10, None)
    af_db = 20.0 * np.log10(af_norm)
    return af_db


def closed_form_af(theta, num_elements, d, wavelength, beta=0.0):
    """Compute the array factor using the closed-form expression.

    For a uniform linear array with equal weights, the array factor has
    the well-known closed-form:

        AF(theta) = sin(N * psi / 2) / sin(psi / 2)

    where psi = k*d*sin(theta) + beta.

    Parameters
    ----------
    theta : np.ndarray
        Observation angles in radians.
    num_elements : int
        Number of array elements (N).
    d : float
        Inter-element spacing in meters.
    wavelength : float
        Operating wavelength in meters.
    beta : float, optional
        Progressive phase shift in radians (default 0).

    Returns
    -------
    af : np.ndarray
        Real-valued array factor magnitude.
    """
    k = 2.0 * np.pi / wavelength
    psi = k * d * np.sin(theta) + beta

    numerator = np.sin(num_elements * psi / 2.0)
    denominator = np.sin(psi / 2.0)

    # Handle psi = 0 (main beam direction) to avoid 0/0
    safe_denom = np.where(np.abs(denominator) < 1e-12, 1.0, denominator)
    af = np.where(
        np.abs(denominator) < 1e-12,
        float(num_elements),
        numerator / safe_denom,
    )
    return np.abs(af)
