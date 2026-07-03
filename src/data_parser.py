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

    def detect_column_structure(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detect the actual column structure, handling DNS outages that change column count."""
        structure = {"target_groups": {}}

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

        return structure

    def get_active_targets(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get list of active targets with their data availability."""
        structure = self.detect_column_structure(df)
        active_targets = []

        for target_num in structure["target_groups"]:
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
                        "has_delay_data": has_delay_data,
                        "has_loss_data": has_loss_data,
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
