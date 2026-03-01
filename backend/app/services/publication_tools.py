"""
Publication assistant tools for antenna research papers.

Features:
- LaTeX table formatter
- Research highlights generator
- BibTeX citation parser and formatter
- Unit converter
"""
import re
import csv
import io
from typing import Optional


class LaTeXTableFormatter:
    """Generate properly formatted LaTeX tables from data."""

    SPECIAL_CHARS = {
        "Ω": r"$\Omega$",
        "°": r"$^\circ$",
        "±": r"$\pm$",
        "≤": r"$\leq$",
        "≥": r"$\geq$",
        "λ": r"$\lambda$",
        "λ₀": r"$\lambda_0$",
        "μ": r"$\mu$",
        "ε": r"$\varepsilon$",
        "εr": r"$\varepsilon_r$",
        "∞": r"$\infty$",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "−": r"$-$",
        "×": r"$\times$",
    }

    def format_table(
        self,
        data: list[dict],
        caption: str = "Table Caption",
        label: str = "tab:results",
        font_size: str = "normalsize",
        orientation: str = "portrait",
        column_format: Optional[str] = None,
        bold_header: bool = True,
    ) -> dict:
        """Generate a LaTeX table from data."""
        if not data:
            return {"latex_code": "", "num_rows": 0, "num_cols": 0, "preview_text": ""}

        headers = list(data[0].keys())
        num_cols = len(headers)
        num_rows = len(data)

        # Generate column format
        if column_format is None:
            column_format = "|" + "|".join(["c"] * num_cols) + "|"

        # Build table
        lines = []

        if orientation == "landscape":
            lines.append(r"\begin{landscape}")

        lines.append(r"\begin{table}[htbp]")
        lines.append(r"\centering")

        if font_size != "normalsize":
            lines.append(rf"\{font_size}")

        lines.append(rf"\caption{{{self._escape_latex(caption)}}}")
        lines.append(rf"\label{{{label}}}")
        lines.append(rf"\begin{{tabular}}{{{column_format}}}")
        lines.append(r"\hline")

        # Header row
        if bold_header:
            header_cells = [rf"\textbf{{{self._escape_latex(str(h))}}}" for h in headers]
        else:
            header_cells = [self._escape_latex(str(h)) for h in headers]
        lines.append(" & ".join(header_cells) + r" \\")
        lines.append(r"\hline")

        # Data rows
        for row in data:
            cells = [self._escape_latex(str(row.get(h, ""))) for h in headers]
            lines.append(" & ".join(cells) + r" \\")

        lines.append(r"\hline")
        lines.append(r"\end{tabular}")
        lines.append(r"\end{table}")

        if orientation == "landscape":
            lines.append(r"\end{landscape}")

        latex_code = "\n".join(lines)

        # Generate preview
        preview_lines = [" | ".join(headers)]
        preview_lines.append("-" * len(preview_lines[0]))
        for row in data[:5]:
            preview_lines.append(" | ".join(str(row.get(h, "")) for h in headers))
        if num_rows > 5:
            preview_lines.append(f"... ({num_rows - 5} more rows)")

        return {
            "latex_code": latex_code,
            "num_rows": num_rows,
            "num_cols": num_cols,
            "preview_text": "\n".join(preview_lines),
        }

    def from_csv_text(self, csv_text: str, **kwargs) -> dict:
        """Generate LaTeX table from CSV text."""
        reader = csv.DictReader(io.StringIO(csv_text))
        data = list(reader)
        return self.format_table(data, **kwargs)

    def _escape_latex(self, text: str) -> str:
        """Escape special characters for LaTeX."""
        for char, replacement in self.SPECIAL_CHARS.items():
            text = text.replace(char, replacement)
        return text


class HighlightsGenerator:
    """Generate Elsevier-style research highlights."""

    def generate(
        self,
        abstract: str,
        num_highlights: int = 5,
        max_chars: int = 85,
    ) -> dict:
        """
        Generate research highlights from an abstract.

        Extracts key findings and formats them as Elsevier highlights
        (<85 characters each).
        """
        sentences = self._split_sentences(abstract)

        highlights = []
        # Extract key sentences with metrics/novelty
        priority_keywords = [
            "novel", "proposed", "achieved", "improved", "demonstrated",
            "first", "new", "design", "bandwidth", "gain", "efficiency",
            "dB", "GHz", "MHz", "%", "MIMO", "antenna", "array",
        ]

        scored = []
        for sent in sentences:
            score = sum(1 for kw in priority_keywords if kw.lower() in sent.lower())
            scored.append((score, sent))

        scored.sort(key=lambda x: x[0], reverse=True)

        for _, sent in scored[:num_highlights]:
            highlight = self._trim_to_highlight(sent, max_chars)
            if highlight and highlight not in highlights:
                highlights.append(highlight)

        # Pad with generic highlights if needed
        while len(highlights) < num_highlights and scored:
            for _, sent in scored:
                h = self._trim_to_highlight(sent, max_chars)
                if h and h not in highlights:
                    highlights.append(h)
                    break
            else:
                break

        highlights = highlights[:num_highlights]

        # Format as LaTeX
        latex_lines = [r"\begin{highlights}"]
        for h in highlights:
            latex_lines.append(rf"\item {self._latex_escape_highlight(h)}")
        latex_lines.append(r"\end{highlights}")

        return {
            "highlights": highlights,
            "latex_formatted": "\n".join(latex_lines),
        }

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def _trim_to_highlight(self, sentence: str, max_chars: int) -> str:
        """Trim a sentence to fit highlight length."""
        # Remove common starting patterns
        sentence = re.sub(r"^(In this (paper|work|study),?\s*)", "", sentence)
        sentence = re.sub(r"^(This (paper|work|study)\s+)", "", sentence)
        sentence = re.sub(r"^(We\s+)", "", sentence)

        # Capitalize first letter
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]

        # Remove trailing period
        sentence = sentence.rstrip(".")

        if len(sentence) <= max_chars:
            return sentence

        # Truncate at word boundary
        truncated = sentence[:max_chars]
        last_space = truncated.rfind(" ")
        if last_space > max_chars * 0.6:
            truncated = truncated[:last_space]

        return truncated

    def _latex_escape_highlight(self, text: str) -> str:
        """Escape highlight text for LaTeX."""
        replacements = {
            "±": r"$\pm$",
            "≤": r"$\leq$",
            "≥": r"$\geq$",
            "λ₀": r"$\lambda_0$",
            "°": r"$^\circ$",
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        return text


class CitationFormatter:
    """Parse BibTeX and format citations for different journals."""

    def parse_bibtex(self, bibtex: str) -> dict:
        """Parse a BibTeX entry into structured fields."""
        result = {}

        # Entry type and key
        match = re.match(r"@(\w+)\{([^,]+),", bibtex.strip())
        if match:
            result["type"] = match.group(1).lower()
            result["key"] = match.group(2).strip()

        # Extract fields
        fields = re.findall(r"(\w+)\s*=\s*\{([^}]*)\}", bibtex)
        for field, value in fields:
            result[field.lower()] = value.strip()

        return result

    def format_ieee(self, entry: dict) -> str:
        """Format citation in IEEE style."""
        parts = []

        # Authors
        if "author" in entry:
            authors = self._format_authors_ieee(entry["author"])
            parts.append(authors)

        # Title
        if "title" in entry:
            parts.append(f'"{entry["title"]},"')

        # Journal/Conference
        if "journal" in entry:
            parts.append(f'*{entry["journal"]}*,')
        elif "booktitle" in entry:
            parts.append(f'in *{entry["booktitle"]}*,')

        # Volume/Number
        vol_parts = []
        if "volume" in entry:
            vol_parts.append(f'vol. {entry["volume"]}')
        if "number" in entry:
            vol_parts.append(f'no. {entry["number"]}')
        if "pages" in entry:
            vol_parts.append(f'pp. {entry["pages"]}')
        if vol_parts:
            parts.append(", ".join(vol_parts) + ",")

        # Date
        if "year" in entry:
            month = entry.get("month", "")
            parts.append(f"{month} {entry['year']}." if month else f"{entry['year']}.")

        # DOI
        if "doi" in entry:
            parts.append(f'doi: {entry["doi"]}.')

        return " ".join(parts)

    def format_elsevier(self, entry: dict) -> str:
        """Format citation in Elsevier style."""
        parts = []

        if "author" in entry:
            authors = self._format_authors_elsevier(entry["author"])
            parts.append(authors)

        if "title" in entry:
            parts.append(f'{entry["title"]}.')

        if "journal" in entry:
            parts.append(f'{entry["journal"]}')

        vol_parts = []
        if "volume" in entry:
            vol_parts.append(entry["volume"])
        if "year" in entry:
            vol_parts.append(f'({entry["year"]})')
        if "pages" in entry:
            vol_parts.append(entry["pages"])
        if vol_parts:
            parts.append(" ".join(vol_parts) + ".")

        return " ".join(parts)

    def _format_authors_ieee(self, authors_str: str) -> str:
        """Format author names in IEEE style."""
        authors = [a.strip() for a in authors_str.split(" and ")]
        formatted = []
        for author in authors:
            if "," in author:
                parts = author.split(",")
                last = parts[0].strip()
                first = parts[1].strip() if len(parts) > 1 else ""
                initials = ". ".join(w[0] for w in first.split() if w) + "."
                formatted.append(f"{initials} {last}")
            else:
                formatted.append(author)

        if len(formatted) > 3:
            return ", ".join(formatted[:3]) + ", *et al.*"
        return ", ".join(formatted[:-1]) + ", and " + formatted[-1] if len(formatted) > 1 else formatted[0]

    def _format_authors_elsevier(self, authors_str: str) -> str:
        """Format author names in Elsevier style."""
        authors = [a.strip() for a in authors_str.split(" and ")]
        formatted = []
        for author in authors:
            if "," in author:
                parts = author.split(",")
                last = parts[0].strip()
                first = parts[1].strip() if len(parts) > 1 else ""
                initials = "".join(w[0] + "." for w in first.split() if w)
                formatted.append(f"{last} {initials}")
            else:
                formatted.append(author)

        if len(formatted) > 3:
            return ", ".join(formatted[:3]) + ", et al."
        return ", ".join(formatted)


class UnitConverter:
    """Common unit conversions for antenna engineering."""

    SPEED_OF_LIGHT = 299792458  # m/s

    def dbm_to_watts(self, dbm: float) -> float:
        """Convert dBm to Watts."""
        return 10 ** ((dbm - 30) / 10)

    def watts_to_dbm(self, watts: float) -> float:
        """Convert Watts to dBm."""
        import math
        return 10 * math.log10(watts) + 30

    def ghz_to_wavelength_mm(self, ghz: float) -> float:
        """Convert frequency in GHz to wavelength in mm."""
        return (self.SPEED_OF_LIGHT / (ghz * 1e9)) * 1000

    def wavelength_mm_to_ghz(self, wavelength_mm: float) -> float:
        """Convert wavelength in mm to frequency in GHz."""
        return self.SPEED_OF_LIGHT / (wavelength_mm / 1000) / 1e9

    def mm_to_lambda(self, mm: float, freq_ghz: float) -> float:
        """Convert mm to wavelength ratio (λ₀)."""
        wavelength = self.ghz_to_wavelength_mm(freq_ghz)
        return mm / wavelength

    def lambda_to_mm(self, lambda_ratio: float, freq_ghz: float) -> float:
        """Convert wavelength ratio (λ₀) to mm."""
        wavelength = self.ghz_to_wavelength_mm(freq_ghz)
        return lambda_ratio * wavelength

    def db_to_linear(self, db: float) -> float:
        """Convert dB to linear scale."""
        return 10 ** (db / 10)

    def linear_to_db(self, linear: float) -> float:
        """Convert linear scale to dB."""
        import math
        return 10 * math.log10(linear)

    def convert(self, value: float, from_unit: str, to_unit: str, freq_ghz: Optional[float] = None) -> dict:
        """General purpose converter."""
        conversions = {
            ("dbm", "watts"): lambda v: self.dbm_to_watts(v),
            ("watts", "dbm"): lambda v: self.watts_to_dbm(v),
            ("ghz", "wavelength_mm"): lambda v: self.ghz_to_wavelength_mm(v),
            ("wavelength_mm", "ghz"): lambda v: self.wavelength_mm_to_ghz(v),
            ("db", "linear"): lambda v: self.db_to_linear(v),
            ("linear", "db"): lambda v: self.linear_to_db(v),
            ("ghz", "mhz"): lambda v: v * 1000,
            ("mhz", "ghz"): lambda v: v / 1000,
            ("mm", "m"): lambda v: v / 1000,
            ("m", "mm"): lambda v: v * 1000,
        }

        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            result = conversions[key](value)
            return {
                "input_value": value,
                "input_unit": from_unit,
                "output_value": result,
                "output_unit": to_unit,
            }

        # Lambda conversions need frequency
        if from_unit.lower() == "mm" and to_unit.lower() == "lambda" and freq_ghz:
            result = self.mm_to_lambda(value, freq_ghz)
            return {"input_value": value, "input_unit": from_unit,
                    "output_value": result, "output_unit": f"λ₀ at {freq_ghz} GHz"}

        if from_unit.lower() == "lambda" and to_unit.lower() == "mm" and freq_ghz:
            result = self.lambda_to_mm(value, freq_ghz)
            return {"input_value": value, "input_unit": f"λ₀ at {freq_ghz} GHz",
                    "output_value": result, "output_unit": "mm"}

        raise ValueError(f"Unsupported conversion: {from_unit} -> {to_unit}")
