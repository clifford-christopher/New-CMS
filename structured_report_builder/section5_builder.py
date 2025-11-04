"""
SECTION 5: CASH FLOW STATEMENT Builder
Dynamically builds annual cash flow statement using API data
"""
import requests
import json
import re

class Section5Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.api_url = "https://frapi.marketsmojo.com/apiv1/financials/get-cashflow"
        self.data = {}

    def _is_bank_stock(self):
        """Check if the stock is a bank based on industry name"""
        try:
            main_header = self.data.get('main_header', {})
            ind_name = main_header.get('ind_name', '').lower()
            # Check for bank but exclude NBFCs
            is_bank = 'bank' in ind_name and 'nbfc' not in ind_name and 'non banking' not in ind_name
            return is_bank
        except:
            return False

    def fetch_data(self):
        """Fetch annual cash flow data from API"""
        print(f"Fetching annual cash flow data for Stock ID: {self.stock_id}")

        try:
            payload = {
                "sid": self.stock_id,
                "exchange": self.exchange,
                "period": "y",
                "card": "1"
            }

            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == 200 and 'data' in result:
                self.data = result['data']
                print(f"[OK] Annual cash flow API successful")
                return self.data
            else:
                print(f"[WARNING] API returned non-200 code")
                return {}
        except Exception as e:
            print(f"[ERROR] API failed: {e}")
            return {}

    def _get_all_periods(self, period_dates):
        """Get all available period keys from period_dates array"""
        try:
            if not period_dates or len(period_dates) < 2:
                return []

            periods = []
            labels = []
            for i, period in enumerate(period_dates):
                if i > 0:  # Skip first item (label)
                    key = period.get('key')
                    label = period.get('label', '')
                    if key:
                        periods.append(key)
                        labels.append(label)
            return periods, labels
        except:
            return [], []

    def _extract_field_value(self, data_items, field_name, period_key, key_type='consolidate'):
        """Extract field value from data items for a specific period"""
        try:
            for section in data_items:
                # Check direct match
                if section.get(key_type) == field_name:
                    value = section.get(period_key)
                    if value is not None:
                        return str(value)

            return None
        except Exception as e:
            return None

    def build_section(self):
        """Build SECTION 5 from API data"""
        if not self.data:
            self.fetch_data()

        # Determine data source
        is_bank = self._is_bank_stock()
        snapshot = self.data.get('snapshot', {})

        if is_bank:
            print(f"[INFO] Bank stock detected - using standalone data")
            data_source = snapshot.get('standalone', {}).get('data', {})
            key_type = 'standalone'
            if not data_source:
                data_source = snapshot.get('consolidate', {}).get('data', {})
                key_type = 'consolidate'
        else:
            data_source = snapshot.get('consolidate', {}).get('data', {})
            key_type = 'consolidate'
            if not data_source:
                data_source = snapshot.get('standalone', {}).get('data', {})
                key_type = 'standalone'

        if not data_source:
            return "Error: No financial data available"

        # Get periods
        period_dates = data_source.get('period_dates', [])
        periods, labels = self._get_all_periods(period_dates)

        if not periods:
            return "Error: No periods available"

        print(f"[INFO] Found {len(periods)} years: {labels}")

        data_items = data_source.get(key_type, [])

        # Field definitions (same for bank and non-bank)
        # Try multiple field names for compatibility
        field_defs = [
            ("Profit Before Tax", ["Profit Before Tax", "Net Profit Before Taxes"]),
            ("Adjustments", ["Adjustment", "Adjustments for Expenses & Provisions"]),
            ("Changes in WC", ["Changes In working Capital", "Adjustments for Liabilities & Assets"]),
            ("Cash Flow from Operations", ["Cash Flow from Operating Activities"]),
            ("Cash Flow from Investing", ["Cash Flow from Investing Activities"]),
            ("Cash Flow from Financing", ["Cash Flow from Financing Activities"]),
            ("Net Cash Inflow", ["Net Cash Inflow / Outflow", "Net increase/(decrease) in cash and cash equivalents"]),
            ("Opening Cash", ["Opening Cash & Cash Equivalents"]),
            ("Closing Cash", ["Closing Cash & Cash Equivalent"]),
        ]

        # Extract all values
        field_values = {}
        for display_name, api_field_list in field_defs:
            field_values[display_name] = []
            for period_key in periods:
                value = None
                # Try all possible field names
                for api_field in api_field_list:
                    value = self._extract_field_value(data_items, api_field, period_key, key_type)
                    if value:
                        break
                field_values[display_name].append(value if value else "N/A")

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 5: CASH FLOW STATEMENT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("All amounts in Rs. Crores")
        lines.append("=" * 80)
        lines.append("")

        # Header
        header = "Year:               "
        for label in labels:
            header += f"{label:<12}"
        lines.append(header)
        lines.append("-" * 80)

        # Profit Before Tax
        row = "Profit Before Tax:  "
        for val in field_values["Profit Before Tax"]:
            row += f"{val:<12}"
        lines.append(row)

        # Adjustments
        row = "Adjustments:        "
        for val in field_values["Adjustments"]:
            row += f"{val:<12}"
        lines.append(row)

        # Changes in WC
        row = "Changes in WC:      "
        for val in field_values["Changes in WC"]:
            row += f"{val:<12}"
        lines.append(row)

        # Cash Flow from Operations (multi-line label)
        lines.append("Cash Flow from")
        row = "Operations:         "
        for val in field_values["Cash Flow from Operations"]:
            row += f"{val:<12}"
        lines.append(row)

        # Cash Flow from Investing (multi-line label)
        lines.append("Cash Flow from")
        row = "Investing:          "
        for val in field_values["Cash Flow from Investing"]:
            row += f"{val:<12}"
        lines.append(row)

        # Cash Flow from Financing (multi-line label)
        lines.append("Cash Flow from")
        row = "Financing:          "
        for val in field_values["Cash Flow from Financing"]:
            row += f"{val:<12}"
        lines.append(row)

        # Net Cash Inflow
        row = "Net Cash Inflow:    "
        for val in field_values["Net Cash Inflow"]:
            row += f"{val:<12}"
        lines.append(row)

        # Opening Cash
        row = "Opening Cash:       "
        for val in field_values["Opening Cash"]:
            row += f"{val:<12}"
        lines.append(row)

        # Closing Cash
        row = "Closing Cash:       "
        for val in field_values["Closing Cash"]:
            row += f"{val:<12}"
        lines.append(row)

        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 5 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 5 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 5 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section5Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section5_output.txt")

    output_file = f"section5_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 5 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section5_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
