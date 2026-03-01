"""Tests for publication tools."""
import pytest

from app.services.publication_tools import (
    LaTeXTableFormatter, HighlightsGenerator, CitationFormatter, UnitConverter,
)


class TestLaTeXTableFormatter:
    @pytest.fixture
    def formatter(self):
        return LaTeXTableFormatter()

    def test_basic_table(self, formatter):
        data = [
            {"Model": "RF", "MSE": "0.0012", "R2": "0.97"},
            {"Model": "GB", "MSE": "0.0015", "R2": "0.96"},
        ]
        result = formatter.format_table(data, caption="ML Results", label="tab:ml")
        assert "\\begin{table}" in result["latex_code"]
        assert "\\end{table}" in result["latex_code"]
        assert "ML Results" in result["latex_code"]
        assert "tab:ml" in result["latex_code"]
        assert result["num_rows"] == 2
        assert result["num_cols"] == 3

    def test_bold_headers(self, formatter):
        data = [{"A": "1", "B": "2"}]
        result = formatter.format_table(data, bold_header=True)
        assert "\\textbf{A}" in result["latex_code"]

    def test_special_characters(self, formatter):
        data = [{"Impedance": "50 Ω", "Angle": "45°"}]
        result = formatter.format_table(data)
        assert "$\\Omega$" in result["latex_code"]
        assert "$^\\circ$" in result["latex_code"]

    def test_font_size(self, formatter):
        data = [{"A": "1"}]
        result = formatter.format_table(data, font_size="footnotesize")
        assert "\\footnotesize" in result["latex_code"]

    def test_landscape(self, formatter):
        data = [{"A": "1"}]
        result = formatter.format_table(data, orientation="landscape")
        assert "\\begin{landscape}" in result["latex_code"]

    def test_from_csv_text(self, formatter):
        csv = "Model,MSE,R2\nRF,0.0012,0.97"
        result = formatter.from_csv_text(csv)
        assert result["num_rows"] == 1
        assert result["num_cols"] == 3

    def test_empty_data(self, formatter):
        result = formatter.format_table([])
        assert result["latex_code"] == ""
        assert result["num_rows"] == 0


class TestHighlightsGenerator:
    @pytest.fixture
    def generator(self):
        return HighlightsGenerator()

    def test_generate_highlights(self, generator):
        abstract = (
            "A novel 28 GHz MIMO antenna array is proposed for 5G applications. "
            "The design achieves a peak gain of 15.2 dBi with -10 dB bandwidth of 2.5 GHz. "
            "Machine learning models predict S11 with R² of 0.97. "
            "The antenna demonstrates improved performance compared to existing designs. "
            "Measured results validate the simulated performance with good agreement."
        )
        result = generator.generate(abstract, num_highlights=5)
        assert len(result["highlights"]) == 5
        assert all(len(h) <= 85 for h in result["highlights"])
        assert "\\begin{highlights}" in result["latex_formatted"]

    def test_max_chars(self, generator):
        abstract = "A very long sentence about antenna design that provides detailed information about the proposed methodology and its applications in 5G communications."
        result = generator.generate(abstract, max_chars=85)
        for h in result["highlights"]:
            assert len(h) <= 85


class TestCitationFormatter:
    @pytest.fixture
    def formatter(self):
        return CitationFormatter()

    def test_parse_bibtex(self, formatter):
        bibtex = """@article{ahmad2026,
  author = {Ahmad, Jawad and Khan, Ali},
  title = {28 GHz MIMO Antenna for 5G},
  journal = {IEEE TAP},
  year = {2026},
  volume = {74},
  pages = {1234-1245},
  doi = {10.1109/TAP.2026.1234}
}"""
        result = formatter.parse_bibtex(bibtex)
        assert result["type"] == "article"
        assert result["key"] == "ahmad2026"
        assert "Ahmad" in result["author"]
        assert result["year"] == "2026"

    def test_format_ieee(self, formatter):
        entry = {
            "author": "Ahmad, Jawad and Khan, Ali",
            "title": "28 GHz MIMO Antenna for 5G",
            "journal": "IEEE TAP",
            "year": "2026",
            "volume": "74",
            "pages": "1234-1245",
        }
        ieee = formatter.format_ieee(entry)
        assert "IEEE TAP" in ieee
        assert "2026" in ieee

    def test_format_elsevier(self, formatter):
        entry = {
            "author": "Ahmad, Jawad and Khan, Ali",
            "title": "28 GHz MIMO Antenna for 5G",
            "journal": "AEU Int. J. Electron. Commun.",
            "year": "2026",
        }
        elsevier = formatter.format_elsevier(entry)
        assert "AEU" in elsevier
        assert "2026" in elsevier


class TestUnitConverter:
    @pytest.fixture
    def converter(self):
        return UnitConverter()

    def test_dbm_to_watts(self, converter):
        assert converter.dbm_to_watts(30) == pytest.approx(1.0)
        assert converter.dbm_to_watts(0) == pytest.approx(0.001)

    def test_watts_to_dbm(self, converter):
        assert converter.watts_to_dbm(1.0) == pytest.approx(30.0)
        assert converter.watts_to_dbm(0.001) == pytest.approx(0.0)

    def test_ghz_to_wavelength(self, converter):
        wl = converter.ghz_to_wavelength_mm(28)
        assert wl == pytest.approx(10.71, abs=0.1)

    def test_wavelength_to_ghz(self, converter):
        freq = converter.wavelength_mm_to_ghz(10.71)
        assert freq == pytest.approx(28, abs=0.5)

    def test_mm_to_lambda(self, converter):
        result = converter.mm_to_lambda(5.35, 28)
        assert result == pytest.approx(0.5, abs=0.05)

    def test_db_to_linear(self, converter):
        assert converter.db_to_linear(10) == pytest.approx(10.0)
        assert converter.db_to_linear(3) == pytest.approx(2.0, abs=0.01)

    def test_convert_general(self, converter):
        result = converter.convert(30, "dbm", "watts")
        assert result["output_value"] == pytest.approx(1.0)
        assert result["output_unit"] == "watts"
