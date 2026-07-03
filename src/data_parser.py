import io
import re
from typing import Any, Dict, List

import pandas as pd
import requests


class NetworkMonitorParser:
    def __init__(self, base_url: str = "http://192.168.0.246"):
        self.base_url = base_url.rstrip("/")

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
                                result["avg_delay"] = float(timing_match.group(2))

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

    def get_active_targets(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get list of active targets with their data availability."""
        # Find Target[N] columns; handles DNS outages that change column count.
        target_numbers = sorted(
            int(col[6:])
            for col in df.columns
            if col.startswith("Target") and col[6:].isdigit()
        )
        active_targets = []

        for target_num in target_numbers:
            names = df[f"Target{target_num}"].dropna()
            delay_col = f"DelayAvg{target_num}"
            loss_col = f"LossPct{target_num}"
            active_targets.append(
                {
                    "number": target_num,
                    "name": names.iloc[0] if not names.empty else f"Target{target_num}",
                    "has_delay_data": delay_col in df.columns and df[delay_col].notna().any(),
                    "has_loss_data": loss_col in df.columns and df[loss_col].notna().any(),
                }
            )

        return active_targets

    def get_all_daily_files(self) -> List[str]:
        """List daily CSV filenames from the device's directory page (anchor texts)."""
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            names = re.findall(r"<a [^>]*>([^<]+)</a>", response.text)
        except Exception as e:
            print(f"Error fetching file list: {e}")
            return []
        return sorted(
            f
            for f in names
            if f.startswith("NetMonitor_")
            and f.endswith(".csv")
            and "Event_Summary" not in f
        )
