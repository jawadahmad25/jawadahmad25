"""Tests for synthetic data generator."""
import pytest
import numpy as np
import pandas as pd

from app.services.synthetic_data import SyntheticDataGenerator


@pytest.fixture
def generator():
    return SyntheticDataGenerator()


@pytest.fixture
def base_data():
    """Create base frequency data at 2.4 GHz."""
    freq = np.linspace(1.0, 4.0, 301)
    s11 = -15 * np.exp(-((freq - 2.4) ** 2) / 0.05) - 3
    gain = 5 + 2 * np.exp(-((freq - 2.4) ** 2) / 0.1)
    return pd.DataFrame({
        "Frequency_GHz": freq,
        "S11_dB": s11,
        "Gain_dBi": gain,
    })


class TestSyntheticDataGenerator:
    def test_frequency_scaling(self, generator, base_data):
        result = generator.generate(base_data, 2.4, 28.0)
        synth = result["data"]

        # Frequency should be scaled
        scaling = 28.0 / 2.4
        assert synth["Frequency_GHz"].min() == pytest.approx(base_data["Frequency_GHz"].min() * scaling)
        assert synth["Frequency_GHz"].max() == pytest.approx(base_data["Frequency_GHz"].max() * scaling)

    def test_s11_preserved(self, generator, base_data):
        result = generator.generate(base_data, 2.4, 28.0)
        synth = result["data"]

        # S11 shape should be preserved
        assert np.allclose(synth["S11_dB"].values, base_data["S11_dB"].values)

    def test_gain_scaling(self, generator, base_data):
        result = generator.generate(base_data, 2.4, 28.0)
        synth = result["data"]

        # Gain should increase by 20*log10(28/2.4) dB
        gain_adj = 20 * np.log10(28.0 / 2.4)
        expected = base_data["Gain_dBi"].values + gain_adj
        assert np.allclose(synth["Gain_dBi"].values, expected)

    def test_scaling_factor(self, generator, base_data):
        result = generator.generate(base_data, 2.4, 28.0)
        assert result["scaling_factor"] == pytest.approx(28.0 / 2.4)

    def test_num_points_preserved(self, generator, base_data):
        result = generator.generate(base_data, 2.4, 28.0)
        assert result["num_points"] == len(base_data)

    def test_geometry_scaling(self, generator):
        geometry = {"patch_length": 40.0, "patch_width": 30.0, "substrate_height": 1.6}
        scaled = generator.scale_geometry(geometry, 2.4, 28.0)

        factor = 2.4 / 28.0
        assert scaled["patch_length"] == pytest.approx(40.0 * factor)
        assert scaled["patch_width"] == pytest.approx(30.0 * factor)
