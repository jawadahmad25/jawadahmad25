"""Tests for data alignment engine."""
import pytest
import numpy as np
import pandas as pd

from app.services.data_alignment import DataAlignmentEngine


@pytest.fixture
def engine():
    return DataAlignmentEngine()


@pytest.fixture
def sim_data():
    """Simulation data: coarser grid, wider range."""
    freq = np.arange(0, 10.01, 0.01)
    s11 = -10 * np.sin(2 * np.pi * freq / 5) - 5
    return pd.DataFrame({"Frequency_GHz": freq, "S11_dB": s11})


@pytest.fixture
def meas_data():
    """Measurement data: finer grid, narrower range."""
    freq = np.arange(0.5, 9.5, 0.001)
    s11 = -10 * np.sin(2 * np.pi * freq / 5) - 5 + np.random.normal(0, 0.1, len(freq))
    return pd.DataFrame({"Frequency_GHz": freq, "S11_dB": s11})


class TestDataAlignment:
    def test_basic_alignment(self, engine, sim_data, meas_data):
        result = engine.align(sim_data, meas_data)
        aligned = result["aligned_df"]

        # Should have common frequency range
        assert aligned["Frequency_GHz"].min() >= max(sim_data["Frequency_GHz"].min(), meas_data["Frequency_GHz"].min())
        assert aligned["Frequency_GHz"].max() <= min(sim_data["Frequency_GHz"].max(), meas_data["Frequency_GHz"].max())

    def test_frequency_step_preserved(self, engine, sim_data, meas_data):
        result = engine.align(sim_data, meas_data)
        stats = result["stats"]

        # Should use reference grid step
        assert stats["aligned"]["freq_step"] == pytest.approx(0.01, abs=0.001)

    def test_different_ranges(self, engine):
        """Test alignment with different frequency ranges."""
        ref = pd.DataFrame({
            "Frequency_GHz": np.arange(26, 30.01, 0.01),
            "S11_dB": np.random.randn(401) * 5 - 15,
        })
        target = pd.DataFrame({
            "Frequency_GHz": np.arange(25, 31.01, 0.005),
            "S11_dB": np.random.randn(1201) * 5 - 15,
        })

        result = engine.align(ref, target)
        aligned = result["aligned_df"]

        # Overlap range should be 26-30 GHz
        assert aligned["Frequency_GHz"].min() == pytest.approx(26.0, abs=0.01)
        assert aligned["Frequency_GHz"].max() == pytest.approx(30.0, abs=0.01)

    def test_no_overlap_raises_error(self, engine):
        """Test that non-overlapping ranges raise ValueError."""
        ref = pd.DataFrame({
            "Frequency_GHz": np.arange(1, 5, 0.1),
            "S11_dB": np.random.randn(40),
        })
        target = pd.DataFrame({
            "Frequency_GHz": np.arange(10, 15, 0.1),
            "S11_dB": np.random.randn(50),
        })

        with pytest.raises(ValueError, match="No overlapping frequency range"):
            engine.align(ref, target)

    def test_output_columns(self, engine, sim_data, meas_data):
        result = engine.align(sim_data, meas_data)
        aligned = result["aligned_df"]

        assert "Frequency_GHz" in aligned.columns
        assert "ref_S11_dB" in aligned.columns
        assert "target_S11_dB" in aligned.columns

    def test_preview_generated(self, engine, sim_data, meas_data):
        result = engine.align(sim_data, meas_data)
        assert "preview" in result
        assert "columns" in result["preview"]
        assert "data" in result["preview"]

    def test_interpolation_methods(self, engine, sim_data, meas_data):
        for method in ["linear", "cubic", "quadratic"]:
            result = engine.align(sim_data, meas_data, method=method)
            assert result["aligned_df"] is not None

    def test_stats_structure(self, engine, sim_data, meas_data):
        result = engine.align(sim_data, meas_data)
        stats = result["stats"]

        assert "reference" in stats
        assert "target" in stats
        assert "aligned" in stats
        assert "num_points" in stats["reference"]
        assert "freq_min" in stats["reference"]
        assert "freq_max" in stats["reference"]
