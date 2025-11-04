"""
SECTION 3: ANNUAL INCOME STATEMENT Builder
Dynamically builds annual income statement using API data
"""
import requests
import json
import re

class Section3Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.api_url = "https://frapi.marketsmojo.com/apiv1/financials/get-profitloss"
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
        """Fetch annual profit & loss data from API"""
        print(f"Fetching annual profit & loss data for Stock ID: {self.stock_id}")

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
                print(f"[OK] Annual profit & loss API successful")
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

    def _calculate_yoy_growth(self, current, previous):
        """Calculate YoY growth percentage between two values"""
        try:
            curr_val = float(str(current).replace(',', '').replace('%', ''))
            prev_val = float(str(previous).replace(',', '').replace('%', ''))

            if prev_val == 0:
                return "N/A"

            growth = ((curr_val - prev_val) / prev_val) * 100

            # Add + sign for positive growth, - is already included for negative
            if growth > 0:
                return f"+{growth:.1f}%"
            elif growth < 0:
                return f"{growth:.1f}%"  # Already has minus sign
            else:
                return "0.0%"
        except:
            return "N/A"

    def _calculate_margin(self, value, base_value):
        """Calculate margin percentage"""
        try:
            val = float(str(value).replace(',', ''))
            base = float(str(base_value).replace(',', ''))

            if base == 0:
                return "N/A"

            margin = (val / base) * 100
            return f"{margin:.1f}%"
        except:
            return "N/A"

    def _calculate_tax_rate(self, tax, pbt):
        """Calculate tax rate percentage"""
        try:
            tax_val = float(str(tax).replace(',', ''))
            pbt_val = float(str(pbt).replace(',', ''))

            if pbt_val == 0:
                return "N/A"

            rate = (tax_val / pbt_val) * 100
            return f"{rate:.1f}%"
        except:
            return "N/A"

    def build_section(self):
        """Build SECTION 3 from API data - branches to bank or non-bank logic"""
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
        """Build Section 3 for non-bank stocks with standard financial fields"""
        # Field definitions: (display_name, api_field_name)
        field_defs = [
            ("Net Sales", "Net Sales"),
            ("Total Expenditure", "Total Expenditure"),
            ("Employee Cost", "Employee Cost"),
            ("Operating Profit (PBDIT) excl Other Income", "Operating Profit (PBDIT) excl Other Income"),
            ("Other Income", "Other Income"),
            ("Operating Profit (PBDIT)", "Operating Profit (PBDIT)"),
            ("Interest", "Interest"),
            ("Depreciation", "Depreciation"),
            ("Profit Before Tax", "Profit Before Tax"),
            ("Provision for Tax", "Provision for Tax"),
            ("Profit After Tax", "Profit After Tax"),
            ("Operating Profit Margin (Excl OI)", "Operating Profit Margin (Excl OI)"),
            ("Gross Profit Margin", "Gross Profit Margin"),
            ("PAT Margin", "PAT Margin"),
        ]

        # Extract all values
        field_values = {}
        for display_name, api_field in field_defs:
            field_values[display_name] = []
            for period_key in periods:
                value = self._extract_field_value(data_items, api_field, period_key, key_type)
                field_values[display_name].append(value if value else "N/A")

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 3: ANNUAL INCOME STATEMENT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("All amounts in Rs. Crores")
        lines.append("=" * 80)
        lines.append("")

        # Header
        header = "Year:               "
        for label in labels:
            header += f"{label:12}"
        lines.append(header)
        lines.append("-" * len(header))

        # Net Sales
        row = "Net Sales:          "
        for val in field_values["Net Sales"]:
            row += f"{val:12}"
        lines.append(row)

        # YoY Growth for Net Sales
        row = "YoY Growth (%):     "
        for i in range(len(periods)):
            if i == len(periods) - 1:  # Last period (oldest)
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_yoy_growth(field_values["Net Sales"][i], field_values["Net Sales"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        lines.append("")

        # Total Expenditure
        row = "Total Expenditure:  "
        for val in field_values["Total Expenditure"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Employee Cost
        row = "Employee Cost:      "
        for val in field_values["Employee Cost"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Operating Profit (PBDIT) excl OI
        lines.append("Operating Profit")
        row = "(PBDIT) excl OI:    "
        for val in field_values["Operating Profit (PBDIT) excl Other Income"]:
            row += f"{val:12}"
        lines.append(row)

        # Margin %
        row = "Margin (%):         "
        for i in range(len(periods)):
            margin = self._calculate_margin(
                field_values["Operating Profit (PBDIT) excl Other Income"][i],
                field_values["Net Sales"][i]
            )
            row += f"{margin:12}"
        lines.append(row)

        lines.append("")

        # Other Income
        row = "Other Income:       "
        for val in field_values["Other Income"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Operating Profit (PBDIT)
        lines.append("Operating Profit")
        row = "(PBDIT):            "
        for val in field_values["Operating Profit (PBDIT)"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Interest
        row = "Interest:           "
        for val in field_values["Interest"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Depreciation
        row = "Depreciation:       "
        for val in field_values["Depreciation"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Profit Before Tax
        row = "Profit Before Tax:  "
        for val in field_values["Profit Before Tax"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Tax
        row = "Tax:                "
        for val in field_values["Provision for Tax"]:
            row += f"{val:12}"
        lines.append(row)

        # Tax Rate %
        row = "Tax Rate (%):       "
        for i in range(len(periods)):
            tax_rate = self._calculate_tax_rate(
                field_values["Provision for Tax"][i],
                field_values["Profit Before Tax"][i]
            )
            row += f"{tax_rate:12}"
        lines.append(row)

        lines.append("")

        # Profit After Tax
        row = "Profit After Tax:   "
        for val in field_values["Profit After Tax"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Operating Margin (Excl OI) %
        lines.append("Operating Margin")
        row = "(Excl OI) %:        "
        for i in range(len(periods)):
            margin = self._calculate_margin(
                field_values["Operating Profit (PBDIT) excl Other Income"][i],
                field_values["Net Sales"][i]
            )
            row += f"{margin:12}"
        lines.append(row)

        lines.append("")

        # Gross Margin %
        row = "Gross Margin %:     "
        for i in range(len(periods)):
            # Try to get from API first
            gross_margin = field_values["Gross Profit Margin"][i]
            if gross_margin == "N/A":
                # Calculate from Operating Profit (PBDIT) / Net Sales
                gross_margin = self._calculate_margin(
                    field_values["Operating Profit (PBDIT)"][i],
                    field_values["Net Sales"][i]
                )
            row += f"{gross_margin:12}"
        lines.append(row)

        lines.append("")

        # PAT Margin %
        row = "PAT Margin %:       "
        for i in range(len(periods)):
            # Try to get from API first
            pat_margin = field_values["PAT Margin"][i]
            if pat_margin == "N/A":
                # Calculate from PAT / Net Sales
                pat_margin = self._calculate_margin(
                    field_values["Profit After Tax"][i],
                    field_values["Net Sales"][i]
                )
            row += f"{pat_margin:12}"
        lines.append(row)

        lines.append("")

        return "\n".join(lines)

    def _build_bank_section(self, periods, labels, data_items, key_type):
        """Build Section 3 for bank stocks with bank-specific fields"""
        # Bank-specific field definitions
        bank_field_defs = [
            ("Interest Earned", "Interest Earned"),
            ("Other Income", "Other Income"),
            ("Total Income", "Total Income"),
            ("Interest Expended", "Interest Expended"),
            ("Provisions and Contingencies", "Provisions and Contingencies"),
            ("Profit Before Tax", "Profit Before Tax"),
            ("Taxes", "Taxes"),
            ("Profit After Tax", "Profit After Tax"),
        ]

        # Extract all values
        field_values = {}
        for display_name, api_field in bank_field_defs:
            field_values[display_name] = []
            for period_key in periods:
                value = self._extract_field_value(data_items, api_field, period_key, key_type)
                field_values[display_name].append(value if value else "N/A")

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 3: ANNUAL INCOME STATEMENT (BANK)")
        lines.append("=" * 80)
        lines.append("")
        lines.append("All amounts in Rs. Crores")
        lines.append("=" * 80)
        lines.append("")

        # Header
        header = "Year:               "
        for label in labels:
            header += f"{label:12}"
        lines.append(header)
        lines.append("-" * len(header))

        # Interest Earned
        row = "Interest Earned:    "
        for val in field_values["Interest Earned"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Other Income
        row = "Other Income:       "
        for val in field_values["Other Income"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Total Income
        row = "Total Income:       "
        for val in field_values["Total Income"]:
            row += f"{val:12}"
        lines.append(row)

        # YoY Growth for Total Income
        row = "YoY Growth (%):     "
        for i in range(len(periods)):
            if i == len(periods) - 1:  # Last period (oldest)
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_yoy_growth(field_values["Total Income"][i], field_values["Total Income"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        lines.append("")

        # Interest Expended
        row = "Interest Expended:  "
        for val in field_values["Interest Expended"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Provisions and contingencies
        lines.append("Provisions and")
        row = "contingencies:      "
        for val in field_values["Provisions and Contingencies"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Profit Before Tax
        row = "Profit Before Tax:  "
        for val in field_values["Profit Before Tax"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Taxes
        row = "Taxes:              "
        for val in field_values["Taxes"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Profit After Tax
        row = "Profit After Tax:   "
        for val in field_values["Profit After Tax"]:
            row += f"{val:12}"
        lines.append(row)

        # YoY Growth for Profit After Tax
        row = "YoY Growth (%):     "
        for i in range(len(periods)):
            if i == len(periods) - 1:  # Last period (oldest)
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_yoy_growth(field_values["Profit After Tax"][i], field_values["Profit After Tax"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 3 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 3 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 3 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section3Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section3_output.txt")

    output_file = f"section3_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 3 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section3_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
