"""
SECTION 4: BALANCE SHEET Builder
Dynamically builds annual balance sheet using API data
"""
import requests
import json
import re

class Section4Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.api_url = "https://frapi.marketsmojo.com/apiv1/financials/get-balancesheet"
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
        """Fetch annual balance sheet data from API"""
        print(f"Fetching annual balance sheet data for Stock ID: {self.stock_id}")

        try:
            payload = {
                "sid": self.stock_id,
                "exchange": self.exchange,
                "period": "y"
            }

            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == '200' and 'data' in result:
                self.data = result['data']
                print(f"[OK] Annual balance sheet API successful")
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

                # Check in nested items
                items = section.get('items', [])
                for item in items:
                    if item.get(key_type) == field_name:
                        value = item.get(period_key)
                        if value is not None:
                            return str(value)

            return None
        except Exception as e:
            return None

    def build_section(self):
        """Build SECTION 4 from API data - branches to bank or non-bank logic"""
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

        # Branch based on stock type
        if is_bank:
            return self._build_bank_section(periods, labels, data_items, key_type)
        else:
            return self._build_non_bank_section(periods, labels, data_items, key_type)

    def _build_non_bank_section(self, periods, labels, data_items, key_type):
        """Build Section 4 for non-bank stocks with standard balance sheet fields"""
        # Field definitions: (display_name, api_field_name)
        field_defs = [
            ("Share Capital", "Share Capital"),
            ("Reserves & Surplus", "Total Reserve"),
            ("Shareholder Funds", "Shareholder's Funds"),
            ("Long-Term Debt", "Long-Term Borrowings"),
            ("Trade Payables", "Trade Payables"),
            ("Other Current", "Other Current Liabilities"),
            ("Current Liabilities", "Total Current Liabilities"),
            ("Fixed Assets", "Net Block"),
            ("Investments", "Non Current Investments"),
            ("Current Assets", "Total Current Assets"),
        ]

        # Extract all values
        field_values = {}
        for display_name, api_field in field_defs:
            field_values[display_name] = []
            for period_key in periods:
                value = self._extract_field_value(data_items, api_field, period_key, key_type)
                # Handle "0.00" as "0" for display
                if value and value != "N/A":
                    try:
                        float_val = float(value.replace(',', ''))
                        if float_val == 0:
                            value = "0"
                    except:
                        pass
                field_values[display_name].append(value if value else "N/A")

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 4: BALANCE SHEET")
        lines.append("=" * 80)
        lines.append("")
        lines.append("All amounts in Rs. Crores")
        lines.append("=" * 80)
        lines.append("")

        # Header - wider columns for better readability
        header = "Year:                     "
        for label in labels:
            header += f"{label:<12}"
        lines.append(header)
        lines.append("-" * 80)
        lines.append("")

        # Share Capital
        row = "Share Capital:            "
        for val in field_values["Share Capital"]:
            row += f"{val:<12}"
        lines.append(row)

        # Reserves & Surplus
        row = "Reserves & Surplus:       "
        for val in field_values["Reserves & Surplus"]:
            row += f"{val:<12}"
        lines.append(row)

        # Shareholder Funds
        row = "Shareholder Funds:        "
        for val in field_values["Shareholder Funds"]:
            row += f"{val:<12}"
        lines.append(row)

        # Long-Term Debt
        row = "Long-Term Debt:           "
        for val in field_values["Long-Term Debt"]:
            row += f"{val:<12}"
        lines.append(row)

        # Trade Payables
        row = "- Trade Payables:         "
        for val in field_values["Trade Payables"]:
            row += f"{val:<12}"
        lines.append(row)

        # Other Current
        row = "- Other Current:          "
        for val in field_values["Other Current"]:
            row += f"{val:<12}"
        lines.append(row)

        # Current Liabilities
        row = "Current Liabilities:      "
        for val in field_values["Current Liabilities"]:
            row += f"{val:<12}"
        lines.append(row)

        # ASSETS header
        lines.append("ASSETS")

        # Fixed Assets
        row = "Fixed Assets:             "
        for val in field_values["Fixed Assets"]:
            row += f"{val:<12}"
        lines.append(row)

        # Investments
        row = "Investments:              "
        for val in field_values["Investments"]:
            row += f"{val:<12}"
        lines.append(row)

        # Current Assets
        row = "Current Assets:           "
        for val in field_values["Current Assets"]:
            row += f"{val:<12}"
        lines.append(row)

        lines.append("")

        return "\n".join(lines)

    def _build_bank_section(self, periods, labels, data_items, key_type):
        """Build Section 4 for bank stocks with bank-specific fields"""
        # Bank-specific field definitions (includes standard + bank-specific fields)
        bank_field_defs = [
            ("Share Capital", "Share Capital"),
            ("Reserves & Surplus", "Total Reserve"),
            ("Shareholder Funds", "Shareholder's Funds"),
            ("Deposits", "Deposits"),
            ("Borrowings", "Borrowings"),
            ("Long-Term Debt", "Long-Term Borrowings"),
            ("Trade Payables", "Trade Payables"),
            ("Other Current", "Other Current Liabilities"),
            ("Current Liabilities", "Total Current Liabilities"),
            ("Fixed Assets", "Net Block"),
            ("Investments", "Investments"),
            ("Advances", "Advances"),
            ("Current Assets", "Total Current Assets"),
        ]

        # Extract all values
        field_values = {}
        for display_name, api_field in bank_field_defs:
            field_values[display_name] = []
            for period_key in periods:
                value = self._extract_field_value(data_items, api_field, period_key, key_type)
                # Handle "0.00" as "0" for display
                if value and value != "N/A":
                    try:
                        float_val = float(value.replace(',', ''))
                        if float_val == 0:
                            value = "0"
                    except:
                        pass
                field_values[display_name].append(value if value else "N/A")

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 4: BALANCE SHEET (BANK)")
        lines.append("=" * 80)
        lines.append("")
        lines.append("All amounts in Rs. Crores")
        lines.append("=" * 80)
        lines.append("")

        # Header - wider columns for better readability
        header = "Year:                     "
        for label in labels:
            header += f"{label:<12}"
        lines.append(header)
        lines.append("-" * 80)
        lines.append("")

        # Share Capital
        row = "Share Capital:            "
        for val in field_values["Share Capital"]:
            row += f"{val:<12}"
        lines.append(row)

        # Reserves & Surplus
        row = "Reserves & Surplus:       "
        for val in field_values["Reserves & Surplus"]:
            row += f"{val:<12}"
        lines.append(row)

        # Shareholder Funds
        row = "Shareholder Funds:        "
        for val in field_values["Shareholder Funds"]:
            row += f"{val:<12}"
        lines.append(row)

        # Deposits (bank-specific)
        row = "Deposits:                 "
        for val in field_values["Deposits"]:
            row += f"{val:<12}"
        lines.append(row)

        # Borrowings (bank-specific)
        row = "Borrowings:               "
        for val in field_values["Borrowings"]:
            row += f"{val:<12}"
        lines.append(row)

        # Long-Term Debt
        row = "Long-Term Debt:           "
        for val in field_values["Long-Term Debt"]:
            row += f"{val:<12}"
        lines.append(row)

        # Trade Payables
        row = "- Trade Payables:         "
        for val in field_values["Trade Payables"]:
            row += f"{val:<12}"
        lines.append(row)

        # Other Current
        row = "- Other Current:          "
        for val in field_values["Other Current"]:
            row += f"{val:<12}"
        lines.append(row)

        # Current Liabilities
        row = "Current Liabilities:      "
        for val in field_values["Current Liabilities"]:
            row += f"{val:<12}"
        lines.append(row)

        # ASSETS header
        lines.append("ASSETS")

        # Fixed Assets
        row = "Fixed Assets:             "
        for val in field_values["Fixed Assets"]:
            row += f"{val:<12}"
        lines.append(row)

        # Investments
        row = "Investments:              "
        for val in field_values["Investments"]:
            row += f"{val:<12}"
        lines.append(row)

        # Advances (bank-specific)
        row = "Advances:                 "
        for val in field_values["Advances"]:
            row += f"{val:<12}"
        lines.append(row)

        # Current Assets
        row = "Current Assets:           "
        for val in field_values["Current Assets"]:
            row += f"{val:<12}"
        lines.append(row)

        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 4 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 4 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 4 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section4Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section4_output.txt")

    output_file = f"section4_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 4 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section4_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
