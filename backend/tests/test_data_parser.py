"""Tests for data parser module."""
import tempfile
import os
import pytest
import numpy as np

from app.services.data_parser import DataParser


@pytest.fixture
def parser():
    return DataParser()


@pytest.fixture
def cst_txt_file():
    """Create a sample CST .txt file."""
    content = """# CST Microwave Studio Export
# Frequency / GHz\tS1,1 / dB
1.0\t-5.2
2.0\t-8.7
3.0\t-15.3
4.0\t-22.1
5.0\t-18.4
6.0\t-12.0
7.0\t-8.5
8.0\t-6.2
9.0\t-4.8
10.0\t-3.9
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name


@pytest.fixture
def hfss_csv_file():
    """Create a sample HFSS .csv file."""
    content = """Freq [GHz],dB(S(1,1)),dB(S(2,1))
26.0,-5.1,-25.3
27.0,-10.2,-22.1
28.0,-28.5,-15.4
29.0,-15.3,-18.7
30.0,-8.7,-20.5
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(content)
        return f.name


@pytest.fixture
def s2p_file():
    """Create a sample .s2p Touchstone file."""
    content = """! VNA Measurement
! Freq S11_dB S11_angle S21_dB S21_angle S12_dB S12_angle S22_dB S22_angle
# GHz S DB R 50
26.0 -5.2 -120.3 -25.1 45.2 -25.3 44.8 -5.5 -118.7
27.0 -12.4 -145.6 -20.3 60.1 -20.5 59.7 -11.8 -143.2
28.0 -30.2 -178.9 -14.7 85.3 -14.9 84.9 -29.5 -177.5
29.0 -18.6 150.2 -17.8 72.4 -18.0 71.9 -17.9 151.8
30.0 -8.9 120.5 -22.4 55.7 -22.6 55.2 -9.2 121.9
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.s2p', delete=False) as f:
        f.write(content)
        return f.name


@pytest.fixture
def generic_csv_file():
    """Create a generic CSV file."""
    content = """frequency,s11_db,gain_dbi
2.0,-8.5,5.2
2.2,-12.3,6.1
2.4,-25.7,7.8
2.6,-18.1,6.9
2.8,-10.4,5.5
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(content)
        return f.name


class TestDataParser:
    def test_detect_format_cst(self, parser, cst_txt_file):
        fmt = parser.detect_format(cst_txt_file)
        assert fmt == "cst_txt"
        os.unlink(cst_txt_file)

    def test_detect_format_hfss(self, parser, hfss_csv_file):
        fmt = parser.detect_format(hfss_csv_file)
        assert fmt == "hfss_csv"
        os.unlink(hfss_csv_file)

    def test_detect_format_s2p(self, parser, s2p_file):
        fmt = parser.detect_format(s2p_file)
        assert fmt == "vna_s2p"
        os.unlink(s2p_file)

    def test_parse_cst_txt(self, parser, cst_txt_file):
        result = parser.parse(cst_txt_file)
        assert result["file_format"] == "cst_txt"
        assert result["data"] is not None
        assert len(result["data"]) == 10
        assert result["num_points"] == 10
        assert result["freq_min"] == pytest.approx(1.0)
        assert result["freq_max"] == pytest.approx(10.0)
        os.unlink(cst_txt_file)

    def test_parse_hfss_csv(self, parser, hfss_csv_file):
        result = parser.parse(hfss_csv_file)
        assert result["file_format"] == "hfss_csv"
        assert result["data"] is not None
        assert len(result["data"]) == 5
        os.unlink(hfss_csv_file)

    def test_parse_s2p(self, parser, s2p_file):
        result = parser.parse(s2p_file)
        assert result["file_format"] == "vna_s2p"
        assert result["data"] is not None
        assert len(result["data"]) == 5
        assert "Frequency_GHz" in result["data"].columns
        assert result["data"]["Frequency_GHz"].iloc[0] == pytest.approx(26.0)
        os.unlink(s2p_file)

    def test_parse_generic_csv(self, parser, generic_csv_file):
        result = parser.parse(generic_csv_file)
        assert result["data"] is not None
        assert len(result["data"]) == 5
        os.unlink(generic_csv_file)

    def test_frequency_metadata(self, parser, generic_csv_file):
        result = parser.parse(generic_csv_file)
        assert result["freq_min"] == pytest.approx(2.0)
        assert result["freq_max"] == pytest.approx(2.8)
        assert result["num_points"] == 5
        os.unlink(generic_csv_file)
