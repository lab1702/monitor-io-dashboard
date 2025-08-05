import io
import re
from typing import Any, Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup


class NetworkMonitorParser:
    def __init__(self, base_url: str = "http://192.168.0.246"):
        self.base_url = base_url.rstrip("/")

    def get_file_list(self) -> List[Dict[str, str]]:
        """Get list of available files from the monitoring device."""
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            files = []

            for row in soup.find_all("tr")[1:]:  # Skip header row
                cells = row.find_all("td")
                if len(cells) >= 4:
                    link = cells[0].find("a")
                    if link:
                        files.append(
                            {
                                "name": link.text,
                                "url": f"{self.base_url}/{link.text}",
                                "modified": cells[1].text,
                                "size": cells[2].text,
                                "type": cells[3].text,
                            }
                        )
            return files
        except Exception as e:
            print(f"Error fetching file list: {e}")
            return []

    def parse_latest_results(self) -> Dict[str, Dict[str, str]]:
        """Parse the latest results log file."""
        try:
            response = requests.get(f"{self.base_url}/Latest_NetMonitor_Results.log")
            response.raise_for_status()

            results = {}
            lines = response.text.strip().split("\n")

            for line in lines:
                line = line.strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    target = parts[0].strip()
                    data = parts[1].strip()

                    # Parse the data format: "xmt/rcv/%loss = 10/0/100%"
                    # or "xmt/rcv/%loss = 10/10/0%, min/avg/max = 14.5/15.3/17.8"
                    if "xmt/rcv/%loss" in data:
                        match = re.search(r"xmt/rcv/%loss = (\d+)/(\d+)/(\d+)%", data)
                        if match:
                            xmt, rcv, loss = match.groups()
                            result = {
                                "transmitted": int(xmt),
                                "received": int(rcv),
                                "loss_percent": int(loss),
                            }

                            # Check for timing data
                            timing_match = re.search(
                                r"min/avg/max = ([\d.]+)/([\d.]+)/([\d.]+)", data
                            )
                            if timing_match:
                                result.update(
                                    {
                                        "min_delay": float(timing_match.group(1)),
                                        "avg_delay": float(timing_match.group(2)),
                                        "max_delay": float(timing_match.group(3)),
                                    }
                                )

                            results[target] = result

            return results
        except Exception as e:
            print(f"Error parsing latest results: {e}")
            return {}

    def parse_event_summary(self) -> pd.DataFrame:
        """Parse the event summary CSV file."""
        try:
            response = requests.get(f"{self.base_url}/NetMonitor_Event_Summary.csv")
            response.raise_for_status()

            df = pd.read_csv(io.StringIO(response.text))
            df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
            return df
        except Exception as e:
            print(f"Error parsing event summary: {e}")
            return pd.DataFrame()

    def parse_daily_csv(self, filename: str) -> pd.DataFrame:
        """Parse a specific daily CSV file."""
        try:
            response = requests.get(f"{self.base_url}/{filename}")
            response.raise_for_status()

            df = pd.read_csv(io.StringIO(response.text))
            df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
            return df
        except Exception as e:
            print(f"Error parsing daily CSV {filename}: {e}")
            return pd.DataFrame()

    def get_target_columns(self, df: pd.DataFrame) -> List[str]:
        """Extract target names from DataFrame columns, handling variable column counts."""
        targets = []
        for col in df.columns:
            if col.startswith("Target") and not any(
                c in col for c in ["Transmit", "Receive", "Loss", "Delay"]
            ):
                targets.append(col)
        return targets

    def detect_column_structure(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detect the actual column structure, handling DNS outages that change column count."""
        structure = {"base_columns": [], "target_groups": {}, "total_targets": 0}

        # Base columns (always present)
        base_cols = ["Date", "Time", "Timezone", "IPAddress", "DateTime"]
        structure["base_columns"] = [col for col in base_cols if col in df.columns]

        # Find target groups by looking for Target[N] columns
        target_numbers = set()
        for col in df.columns:
            if col.startswith("Target") and col[6:].isdigit():
                target_num = int(col[6:])
                target_numbers.add(target_num)

        # Group columns by target number
        for target_num in sorted(target_numbers):
            target_cols = []
            for col in df.columns:
                if col.endswith(str(target_num)):
                    target_cols.append(col)

            if target_cols:
                structure["target_groups"][target_num] = target_cols

        structure["total_targets"] = len(target_numbers)
        return structure

    def extract_target_data(self, df: pd.DataFrame, target_num: int) -> pd.DataFrame:
        """Extract data for a specific target number from DataFrame, handling missing targets gracefully."""
        target_cols = [col for col in df.columns if col.endswith(str(target_num))]

        if not target_cols:
            # Return empty DataFrame if target doesn't exist
            return pd.DataFrame()

        base_cols = ["Date", "Time", "DateTime", "IPAddress", "Timezone"]
        available_base_cols = [col for col in base_cols if col in df.columns]

        result_df = df[available_base_cols + target_cols].copy()

        # Rename columns to remove target number suffix
        rename_dict = {}
        for col in target_cols:
            new_name = col.replace(str(target_num), "").rstrip("_")
            rename_dict[col] = new_name

        result_df = result_df.rename(columns=rename_dict)

        # Add target name if available
        target_col = f"Target{target_num}"
        if target_col in df.columns:
            # Get the first non-null target name
            target_names = df[target_col].dropna()
            if not target_names.empty:
                result_df["TargetName"] = target_names.iloc[0]
            else:
                result_df["TargetName"] = f"Target{target_num}"
        else:
            result_df["TargetName"] = f"Target{target_num}"

        return result_df

    def get_active_targets(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get list of active targets with their data availability."""
        structure = self.detect_column_structure(df)
        active_targets = []

        for target_num, cols in structure["target_groups"].items():
            target_col = f"Target{target_num}"
            if target_col in df.columns:
                # Get target name
                target_names = df[target_col].dropna()
                target_name = (
                    target_names.iloc[0]
                    if not target_names.empty
                    else f"Target{target_num}"
                )

                # Check data availability
                delay_col = f"DelayAvg{target_num}"
                loss_col = f"LossPct{target_num}"

                has_delay_data = delay_col in df.columns and df[delay_col].notna().any()
                has_loss_data = loss_col in df.columns and df[loss_col].notna().any()

                active_targets.append(
                    {
                        "number": target_num,
                        "name": target_name,
                        "columns": cols,
                        "has_delay_data": has_delay_data,
                        "has_loss_data": has_loss_data,
                        "data_points": len(df[df[target_col].notna()])
                        if target_col in df.columns
                        else 0,
                    }
                )

        return sorted(active_targets, key=lambda x: x["number"])

    def get_all_daily_files(self) -> List[str]:
        """Get list of all daily CSV files."""
        files = self.get_file_list()
        daily_files = []

        for file_info in files:
            filename = file_info["name"]
            if (
                filename.startswith("NetMonitor_")
                and filename.endswith(".csv")
                and "Event_Summary" not in filename
            ):
                daily_files.append(filename)

        return sorted(daily_files)

    def get_dashboard_data(self) -> Dict:
        """Get all data needed for the dashboard."""
        return {
            "latest_results": self.parse_latest_results(),
            "event_summary": self.parse_event_summary(),
            "daily_files": self.get_all_daily_files(),
            "file_list": self.get_file_list(),
        }
