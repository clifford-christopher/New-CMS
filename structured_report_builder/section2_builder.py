"""
SECTION 2: QUARTERLY INCOME STATEMENT Builder
Dynamically builds quarterly income statement using API data
"""
import requests
import json
import re

class Section2Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.api_url = "https://frapi.marketsmojo.com/apiv1/financials/get-financials"
        self.summary_url = "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary"
        self.data = {}
        self.summary_data = {}

    def _is_bank_stock(self):
        """Check if the stock is a bank based on industry name"""
        try:
            main_header = self.summary_data.get('main_header', {})
            ind_name = main_header.get('ind_name', '').lower()
            # Check for bank but exclude NBFCs
            is_bank = 'bank' in ind_name and 'nbfc' not in ind_name and 'non banking' not in ind_name
            return is_bank
        except:
            return False

    def fetch_data(self):
        """Fetch quarterly financial data from API"""
        print(f"Fetching quarterly financial data for Stock ID: {self.stock_id}")

        # First fetch summary data to get industry info
        try:
            summary_payload = {"sid": int(self.stock_id), "exchange": self.exchange}
            summary_response = requests.post(self.summary_url, json=summary_payload, timeout=30)
            summary_response.raise_for_status()
            summary_result = summary_response.json()

            if summary_result.get('code') == '200' and 'data' in summary_result:
                self.summary_data = summary_result['data']
                print(f"[OK] Summary API successful")
        except Exception as e:
            print(f"[WARNING] Summary API failed: {e}")
            self.summary_data = {}

        # Now fetch financial data
        try:
            payload = {
                "sid": self.stock_id,
                "exchange": self.exchange,
                "card": "1",
                "period": "q"
            }

            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == '200' and 'data' in result:
                self.data = result['data']
                print(f"[OK] Quarterly financial API successful")
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

    def _calculate_growth(self, current, previous):
        """Calculate growth percentage between two values"""
        try:
            curr_val = float(str(current).replace(',', '').replace('%', ''))
            prev_val = float(str(previous).replace(',', '').replace('%', ''))

            if prev_val == 0:
                return "N/A"

            growth = ((curr_val - prev_val) / prev_val) * 100

            # Add + sign for positive growth, - is already included for negative
            if growth > 0:
                return f"+{growth:.2f}%"
            elif growth < 0:
                return f"{growth:.2f}%"  # Already has minus sign
            else:
                return "0.00%"
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
            return f"{rate:.2f}%"
        except:
            return "N/A"

    def build_section(self):
        """Build SECTION 2 from API data - branches to bank or non-bank logic"""
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

        print(f"[INFO] Found {len(periods)} quarters: {labels}")

        data_items = data_source.get(key_type, [])

        # Branch based on stock type
        if is_bank:
            return self._build_bank_section(periods, labels, data_items, key_type)
        else:
            return self._build_non_bank_section(periods, labels, data_items, key_type)

    def _build_bank_section(self, periods, labels, data_items, key_type):
        """Build Section 2 for bank stocks with bank-specific fields"""
        # Bank-specific field definitions
        bank_field_defs = [
            ("Interest Earned", "Interest Earned"),
            ("Income On Investments", "Income On Investments"),
            ("Interest On Balances With RBI", "Interest On Balances With Rbi Other Inter Bank Funds"),
            ("Interest / Discount On Advances", "Interest / Discount On Advances / Bills"),
            ("Others", "Others"),
            ("Other Income", "Other Income"),
            ("Total Income", "Total Income"),
            ("Interest Expended", "Interest Expended"),
            ("Net Interest Income", "Net Interest Income"),
            ("Operating Profit Before Provisions", "Operating Profit Before Provisions and Contingencies"),
            ("Provisions and contingencies", "Provisions and contingencies"),
            ("Profit Before Tax", "Profit Before Tax"),
            ("Tax", "Tax"),
            ("Net Profit", "Net Profit"),
            ("Net Interest Margin", "Net Interest Margin"),
            ("CASA", "CASA (%)"),
            ("Capital Adequacy Ratio (Total)", "Capital Adequacy Ratio (Total)"),
            ("Capital Adequacy Ratio (Tier 1)", "Capital Adequacy Ratio (Tier 1)"),
            ("Provision Coverage Ratio", "Provision Coverage Ratio (%)"),
            ("% of Net NPAs", "% of Net NPAs"),
            ("% of Gross NPAs", "% of Gross NPAs"),
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
        lines.append("SECTION 2: QUARTERLY INCOME STATEMENT (BANK)")
        lines.append("=" * 80)
        lines.append("")
        lines.append("All amounts in Rs. Crores")
        lines.append("=" * 80)
        lines.append("")

        # Header
        header = "Quarter:                        "
        for label in labels:
            header += f"{label:12}"
        lines.append(header)
        lines.append("-" * len(header))

        # Interest Earned
        row = "Interest Earned:                "
        for val in field_values["Interest Earned"]:
            row += f"{val:12}"
        lines.append(row)

        # Income On Investments
        row = "Income On Investments:          "
        for val in field_values["Income On Investments"]:
            row += f"{val:12}"
        lines.append(row)

        # Interest On Balances With RBI
        row = "Interest On Balances With RBI:  "
        for val in field_values["Interest On Balances With RBI"]:
            row += f"{val:12}"
        lines.append(row)

        # Interest / Discount On Advances
        row = "Interest / Discount On Advances:"
        for val in field_values["Interest / Discount On Advances"]:
            row += f"{val:12}"
        lines.append(row)

        # Others
        row = "Others:                         "
        for val in field_values["Others"]:
            row += f"{val:12}"
        lines.append(row)

        # Other Income
        row = "Other Income:                   "
        for val in field_values["Other Income"]:
            row += f"{val:12}"
        lines.append(row)

        # Total Income
        row = "Total Income:                   "
        for val in field_values["Total Income"]:
            row += f"{val:12}"
        lines.append(row)

        # QoQ Growth for Total Income
        row = "QoQ Growth (%):                 "
        for i in range(len(periods)):
            if i == len(periods) - 1:  # Last period (oldest)
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_growth(field_values["Total Income"][i], field_values["Total Income"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        # YoY Growth for Total Income
        row = "YoY Growth (%):                 "
        for i in range(len(periods)):
            yoy_index = i + 4  # 4 quarters back for YoY
            if yoy_index < len(periods):
                growth = self._calculate_growth(field_values["Total Income"][i], field_values["Total Income"][yoy_index])
                row += f"{growth:12}"
            else:
                row += f"{'N/A':12}"
        lines.append(row)

        lines.append("")

        # Interest Expended
        row = "Interest Expended:              "
        for val in field_values["Interest Expended"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Net Interest Income
        row = "Net Interest Income:            "
        for val in field_values["Net Interest Income"]:
            row += f"{val:12}"
        lines.append(row)

        # QoQ Growth for Net Interest Income
        row = "QoQ Growth (%):                 "
        for i in range(len(periods)):
            if i == len(periods) - 1:
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_growth(field_values["Net Interest Income"][i], field_values["Net Interest Income"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        # YoY Growth for Net Interest Income
        row = "YoY Growth (%):                 "
        for i in range(len(periods)):
            yoy_index = i + 4
            if yoy_index < len(periods):
                growth = self._calculate_growth(field_values["Net Interest Income"][i], field_values["Net Interest Income"][yoy_index])
                row += f"{growth:12}"
            else:
                row += f"{'N/A':12}"
        lines.append(row)

        lines.append("")

        # Operating Profit Before Provisions
        lines.append("Operating Profit Before")
        row = "Provisions and Contingencies:   "
        for val in field_values["Operating Profit Before Provisions"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Provisions and contingencies
        row = "Provisions and contingencies:   "
        for val in field_values["Provisions and contingencies"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Profit Before Tax
        row = "Profit Before Tax:              "
        for val in field_values["Profit Before Tax"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Tax
        row = "Tax:                            "
        for val in field_values["Tax"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Net Profit
        row = "Net Profit:                     "
        for val in field_values["Net Profit"]:
            row += f"{val:12}"
        lines.append(row)

        # QoQ Growth for Net Profit
        row = "QoQ Growth (%):                 "
        for i in range(len(periods)):
            if i == len(periods) - 1:
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_growth(field_values["Net Profit"][i], field_values["Net Profit"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        # YoY Growth for Net Profit
        row = "YoY Growth (%):                 "
        for i in range(len(periods)):
            yoy_index = i + 4
            if yoy_index < len(periods):
                growth = self._calculate_growth(field_values["Net Profit"][i], field_values["Net Profit"][yoy_index])
                row += f"{growth:12}"
            else:
                row += f"{'N/A':12}"
        lines.append(row)

        lines.append("")

        # Net Interest Margin (%)
        row = "Net Interest Margin (%):        "
        for val in field_values["Net Interest Margin"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # CASA (%)
        row = "CASA (%):                       "
        for val in field_values["CASA"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Capital Adequacy Ratio (Total)
        lines.append("Capital Adequacy Ratio")
        row = "(Total):                        "
        for val in field_values["Capital Adequacy Ratio (Total)"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Capital Adequacy Ratio (Tier 1)
        lines.append("Capital Adequacy Ratio")
        row = "(Tier 1):                       "
        for val in field_values["Capital Adequacy Ratio (Tier 1)"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Provision Coverage Ratio (%)
        row = "Provision Coverage Ratio (%):   "
        for val in field_values["Provision Coverage Ratio"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # % of Net NPAs
        row = "% of Net NPAs:                  "
        for val in field_values["% of Net NPAs"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # % of Gross NPAs
        row = "% of Gross NPAs:                "
        for val in field_values["% of Gross NPAs"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        return "\n".join(lines)

    def _build_non_bank_section(self, periods, labels, data_items, key_type):
        """Build Section 2 for non-bank stocks with standard financial fields"""
        # Field definitions: (display_name, api_field_name)
        field_defs = [
            ("Net Sales", "Net Sales"),
            ("Employee Cost", "Employee Cost"),
            ("Operating Profit (PBDIT) excl OI", "Operating Profit (PBDIT) excl Other Income"),
            ("Other Income", "Other Income"),
            ("Operating Profit (PBDIT)", "Operating Profit (PBDIT)"),
            ("Interest", "Interest"),
            ("Depreciation", "Depreciation"),
            ("Profit Before Tax", "Profit Before Tax"),
            ("Tax", "Tax"),
            ("Net Profit (PAT)", "Profit After Tax"),
            ("Consolidated Net Profit", "Consolidated Net Profit"),
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
        lines.append("SECTION 2: QUARTERLY INCOME STATEMENT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("All amounts in Rs. Crores")
        lines.append("=" * 80)
        lines.append("")

        # Header
        header = "Quarter:            "
        for label in labels:
            header += f"{label:12}"
        lines.append(header)
        lines.append("-" * len(header))

        # Net Sales
        row = "Net Sales:          "
        for val in field_values["Net Sales"]:
            row += f"{val:12}"
        lines.append(row)

        # QoQ Growth for Net Sales
        row = "QoQ Growth (%):     "
        for i in range(len(periods)):
            if i == len(periods) - 1:  # Last period (oldest)
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_growth(field_values["Net Sales"][i], field_values["Net Sales"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        # YoY Growth for Net Sales
        row = "YoY Growth (%):     "
        for i in range(len(periods)):
            yoy_index = i + 4  # 4 quarters back for YoY
            if yoy_index < len(periods):
                growth = self._calculate_growth(field_values["Net Sales"][i], field_values["Net Sales"][yoy_index])
                row += f"{growth:12}"
            else:
                row += f"{'N/A':12}"
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
        for val in field_values["Operating Profit (PBDIT) excl OI"]:
            row += f"{val:12}"
        lines.append(row)

        # Margin %
        row = "Margin (%):         "
        for val in field_values["Operating Profit Margin (Excl OI)"]:
            row += f"{val:12}"
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
        for val in field_values["Tax"]:
            row += f"{val:12}"
        lines.append(row)

        # Tax Rate %
        row = "Tax Rate (%):       "
        for i in range(len(periods)):
            tax_rate = self._calculate_tax_rate(field_values["Tax"][i], field_values["Profit Before Tax"][i])
            row += f"{tax_rate:12}"
        lines.append(row)

        lines.append("")

        # Net Profit (PAT)
        row = "Net Profit (PAT):   "
        for val in field_values["Net Profit (PAT)"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Consolidated Net Profit
        lines.append("Consolidated Net")
        row = "Profit:             "
        for val in field_values["Consolidated Net Profit"]:
            row += f"{val:12}"
        lines.append(row)

        # QoQ Growth for Consolidated Net Profit
        row = "QoQ Growth (%):     "
        for i in range(len(periods)):
            if i == len(periods) - 1:
                row += f"{'N/A':12}"
            else:
                growth = self._calculate_growth(field_values["Consolidated Net Profit"][i], field_values["Consolidated Net Profit"][i+1])
                row += f"{growth:12}"
        lines.append(row)

        # YoY Growth for Consolidated Net Profit
        row = "YoY Growth (%):     "
        for i in range(len(periods)):
            yoy_index = i + 4
            if yoy_index < len(periods):
                growth = self._calculate_growth(field_values["Consolidated Net Profit"][i], field_values["Consolidated Net Profit"][yoy_index])
                row += f"{growth:12}"
            else:
                row += f"{'N/A':12}"
        lines.append(row)

        lines.append("")

        # Operating Margin (Excl OI) %
        lines.append("Operating Margin")
        row = "(Excl OI) %:        "
        for val in field_values["Operating Profit Margin (Excl OI)"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # Gross Profit Margin %
        lines.append("Gross Profit")
        row = "Margin %:           "
        for val in field_values["Gross Profit Margin"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        # PAT Margin %
        row = "PAT Margin %:       "
        for val in field_values["PAT Margin"]:
            row += f"{val:12}"
        lines.append(row)

        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 2 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 2 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 2 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section2Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section2_output.txt")

    output_file = f"section2_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 2 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section2_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
