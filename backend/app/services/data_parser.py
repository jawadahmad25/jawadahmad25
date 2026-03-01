"""
Data parser for antenna simulation and measurement files.

Supports:
- CST .txt exports (frequency, S11, S21, gain patterns)
- HFSS .csv exports
- VNA measurement data (.s2p Touchstone, .csv)
- Generic CSV files
"""
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


class DataParser:
    """Detects and parses various antenna data file formats."""

    SUPPORTED_EXTENSIONS = {".txt", ".csv", ".s2p", ".s1p", ".s3p", ".s4p"}

    def detect_format(self, file_path: str) -> str:
        """Auto-detect the file format based on extension and content."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext in (".s2p", ".s1p", ".s3p", ".s4p"):
            return "vna_s2p"

        content = path.read_text(errors="replace")
        first_lines = content.split("\n")[:20]
        header_text = "\n".join(first_lines).lower()

        if ext == ".txt":
            if any(kw in header_text for kw in ["cst", "frequency / ghz", "frequency / mhz"]):
                return "cst_txt"
            if self._looks_like_cst(first_lines):
                return "cst_txt"

        if ext == ".csv":
            if any(kw in header_text for kw in ["hfss", "ansoft", "ansys"]):
                return "hfss_csv"
            if "freq" in header_text and ("s(" in header_text or "db(" in header_text):
                return "hfss_csv"
            if any(kw in header_text for kw in ["vna", "measurement", "network analyzer"]):
                return "vna_csv"

        return "generic_csv"

    def parse(self, file_path: str, file_format: Optional[str] = None) -> dict:
        """Parse a data file and return structured data with metadata."""
        if file_format is None:
            file_format = self.detect_format(file_path)

        parsers = {
            "cst_txt": self._parse_cst_txt,
            "hfss_csv": self._parse_hfss_csv,
            "vna_s2p": self._parse_s2p,
            "vna_csv": self._parse_vna_csv,
            "generic_csv": self._parse_generic_csv,
        }

        parser = parsers.get(file_format, self._parse_generic_csv)
        result = parser(file_path)
        result["file_format"] = file_format
        result["file_path"] = file_path

        # Extract frequency info
        if "data" in result and result["data"] is not None:
            df = result["data"]
            freq_col = self._find_frequency_column(df)
            if freq_col:
                result["freq_column"] = freq_col
                freq_vals = df[freq_col].values
                result["freq_min"] = float(np.min(freq_vals))
                result["freq_max"] = float(np.max(freq_vals))
                result["num_points"] = len(freq_vals)
                if len(freq_vals) > 1:
                    steps = np.diff(freq_vals)
                    result["freq_step"] = float(np.median(steps))

        return result

    def _looks_like_cst(self, lines: list[str]) -> bool:
        """Check if content looks like CST export (tab/space separated numeric data)."""
        data_lines = [l for l in lines if l.strip() and not l.strip().startswith(("#", "!", "%"))]
        if len(data_lines) < 2:
            return False
        for line in data_lines[:5]:
            parts = re.split(r"[\t\s]+", line.strip())
            try:
                [float(p) for p in parts if p]
                if len(parts) >= 2:
                    return True
            except ValueError:
                continue
        return False

    def _parse_cst_txt(self, file_path: str) -> dict:
        """Parse CST Studio Suite .txt export files."""
        lines = Path(file_path).read_text(errors="replace").split("\n")

        # Find header lines (comments) and data start
        header_lines = []
        data_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("#", "!", "%")):
                header_lines.append(stripped)
                data_start = i + 1
                continue
            # Check if this is a data line
            parts = re.split(r"[\t\s]+", stripped)
            try:
                [float(p) for p in parts if p]
                data_start = i
                break
            except ValueError:
                header_lines.append(stripped)
                data_start = i + 1

        # Try to extract column names from header
        columns = None
        for h in header_lines:
            h_clean = re.sub(r"^[#!%]+\s*", "", h)
            if "/" in h_clean or "frequency" in h_clean.lower():
                columns = [c.strip() for c in re.split(r"[\t]+", h_clean) if c.strip()]
                break

        # Parse data
        data_rows = []
        for line in lines[data_start:]:
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "!", "%")):
                continue
            parts = re.split(r"[\t\s]+", stripped)
            try:
                row = [float(p) for p in parts if p]
                if row:
                    data_rows.append(row)
            except ValueError:
                continue

        if not data_rows:
            return {"data": None, "columns": [], "error": "No data found"}

        df = pd.DataFrame(data_rows)

        # Assign column names
        if columns and len(columns) == len(df.columns):
            df.columns = columns
        else:
            default_names = ["Frequency"]
            for i in range(1, len(df.columns)):
                default_names.append(f"Value_{i}")
            df.columns = default_names[:len(df.columns)]

        # Normalize frequency column name
        df = self._normalize_freq_column(df)

        return {
            "data": df,
            "columns": list(df.columns),
            "header_info": header_lines,
        }

    def _parse_hfss_csv(self, file_path: str) -> dict:
        """Parse HFSS .csv export files."""
        # HFSS CSVs may have metadata rows before the actual data
        lines = Path(file_path).read_text(errors="replace").split("\n")

        # Find the header row (contains column names)
        header_row = 0
        for i, line in enumerate(lines):
            if "freq" in line.lower() or "s(" in line.lower() or "db(" in line.lower():
                header_row = i
                break

        df = pd.read_csv(file_path, skiprows=header_row)

        # Clean column names
        df.columns = [col.strip().strip('"') for col in df.columns]
        df = self._normalize_freq_column(df)

        return {
            "data": df,
            "columns": list(df.columns),
            "header_info": lines[:header_row],
        }

    def _parse_s2p(self, file_path: str) -> dict:
        """Parse Touchstone .s2p/.s1p files."""
        lines = Path(file_path).read_text(errors="replace").split("\n")

        # Parse option line
        freq_unit = "ghz"
        param_type = "s"
        data_format = "db"

        comments = []
        data_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("!"):
                comments.append(stripped[1:].strip())
                continue
            if stripped.startswith("#"):
                parts = stripped[1:].split()
                if parts:
                    freq_unit = parts[0].lower() if len(parts) > 0 else "ghz"
                    param_type = parts[1].lower() if len(parts) > 1 else "s"
                    data_format = parts[2].lower() if len(parts) > 2 else "db"
                data_start = i + 1
                continue
            if re.match(r"^[\d\.\-\+eE]", stripped):
                data_start = i
                break

        # Frequency multiplier
        freq_multipliers = {"hz": 1e-9, "khz": 1e-6, "mhz": 1e-3, "ghz": 1.0}
        freq_mult = freq_multipliers.get(freq_unit, 1.0)

        # Parse data
        data_rows = []
        for line in lines[data_start:]:
            stripped = line.strip()
            if not stripped or stripped.startswith(("!", "#")):
                continue
            parts = re.split(r"[\t\s]+", stripped)
            try:
                row = [float(p) for p in parts if p]
                if row:
                    data_rows.append(row)
            except ValueError:
                continue

        if not data_rows:
            return {"data": None, "columns": [], "error": "No data found"}

        df = pd.DataFrame(data_rows)

        # Name columns based on number of ports
        num_data_cols = len(df.columns) - 1
        col_names = ["Frequency_GHz"]

        if num_data_cols == 2:  # S1P: magnitude, angle
            col_names.extend(["S11_mag", "S11_ang"])
        elif num_data_cols == 8:  # S2P: S11, S21, S12, S22
            for sp in ["S11", "S21", "S12", "S22"]:
                if data_format == "db":
                    col_names.extend([f"{sp}_dB", f"{sp}_ang"])
                elif data_format == "ma":
                    col_names.extend([f"{sp}_mag", f"{sp}_ang"])
                else:
                    col_names.extend([f"{sp}_re", f"{sp}_im"])
        else:
            for i in range(num_data_cols):
                col_names.append(f"Col_{i+1}")

        df.columns = col_names[:len(df.columns)]

        # Convert frequency to GHz
        df["Frequency_GHz"] = df["Frequency_GHz"] * freq_mult

        return {
            "data": df,
            "columns": list(df.columns),
            "header_info": comments,
            "freq_unit": freq_unit,
            "param_type": param_type,
            "data_format": data_format,
        }

    def _parse_vna_csv(self, file_path: str) -> dict:
        """Parse VNA measurement CSV files."""
        df = pd.read_csv(file_path)
        df.columns = [col.strip() for col in df.columns]
        df = self._normalize_freq_column(df)

        return {
            "data": df,
            "columns": list(df.columns),
            "header_info": [],
        }

    def _parse_generic_csv(self, file_path: str) -> dict:
        """Parse generic CSV files with auto-detection."""
        # Try different separators
        for sep in [",", "\t", ";", " "]:
            try:
                df = pd.read_csv(file_path, sep=sep)
                if len(df.columns) >= 2:
                    break
            except Exception:
                continue
        else:
            return {"data": None, "columns": [], "error": "Could not parse file"}

        df.columns = [col.strip() for col in df.columns]
        df = self._normalize_freq_column(df)

        return {
            "data": df,
            "columns": list(df.columns),
            "header_info": [],
        }

    def _normalize_freq_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize frequency column name to 'Frequency_GHz'."""
        freq_patterns = [
            (r"(?i)freq.*ghz", "Frequency_GHz", 1.0),
            (r"(?i)freq.*mhz", "Frequency_GHz", 1e-3),
            (r"(?i)freq.*hz", "Frequency_GHz", 1e-9),
            (r"(?i)^freq", "Frequency_GHz", 1.0),
        ]
        for pattern, new_name, multiplier in freq_patterns:
            for col in df.columns:
                if re.match(pattern, col):
                    if multiplier != 1.0:
                        df[col] = df[col] * multiplier
                    df = df.rename(columns={col: new_name})
                    return df
        return df

    def _find_frequency_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the frequency column in a DataFrame."""
        for col in df.columns:
            if "freq" in col.lower():
                return col
        # If first column is monotonically increasing, assume frequency
        if df.iloc[:, 0].is_monotonic_increasing:
            return df.columns[0]
        return None
