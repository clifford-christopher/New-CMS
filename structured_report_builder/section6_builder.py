"""
SECTION 6: KEY FINANCIAL RATIOS & METRICS Builder
Dynamically builds financial ratios using Quality and Valuation data from APIs
Simplified version - uses pre-calculated ratios from stocksummary/getRecoData APIs
"""
import requests
import json
from api_utils import post_with_retry

class Section6Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.recommendation_api_url = "https://frapi.marketsmojo.com/apiv1/recommendation/getRecoData"
        self.summary_api_url = "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary"

        self.recommendation_data = {}
        self.summary_data = {}
        self.quality_ratios = []
        self.valuation_ratios = []

    def _is_bank_stock(self):
        """Check if the stock is a bank based on industry name (excluding NBFCs)"""
        try:
            # Try from recommendation data first
            if self.recommendation_data:
                main_header = self.recommendation_data.get('main_header', {})
                ind_name = main_header.get('ind_name', '').lower()
                if ind_name:
                    # Check for bank but exclude NBFCs
                    is_bank = 'bank' in ind_name and 'nbfc' not in ind_name and 'non banking' not in ind_name
                    return is_bank

            # Fallback to summary data
            if self.summary_data:
                main_header = self.summary_data.get('main_header', {})
                ind_name = main_header.get('ind_name', '').lower()
                # Check for bank but exclude NBFCs
                is_bank = 'bank' in ind_name and 'nbfc' not in ind_name and 'non banking' not in ind_name
                return is_bank

            return False
        except:
            return False

    def _is_financial_sector(self):
        """Check if the stock belongs to financial sector (Banks, NBFCs, Insurance, etc.)"""
        try:
            # List of exact financial sector industry names
            financial_sectors = [
                "Finance",
                "Housing Finance Company",
                "Insurance",
                "Non Banking Financial Company (NBFC)",
                "Other Bank",
                "Private Sector Bank",
                "Public Sector Bank"
            ]

            # Try from recommendation data first
            if self.recommendation_data:
                main_header = self.recommendation_data.get('main_header', {})
                ind_name = main_header.get('ind_name', '')
                if ind_name in financial_sectors:
                    return True

            # Fallback to summary data
            if self.summary_data:
                main_header = self.summary_data.get('main_header', {})
                ind_name = main_header.get('ind_name', '')
                if ind_name in financial_sectors:
                    return True

            return False
        except:
            return False

    def fetch_quality_valuation_data(self):
        """Fetch Quality and Valuation ratios from APIs"""
        print("=" * 80)
        print("FETCHING QUALITY & VALUATION DATA FROM APIS...")
        print("=" * 80)

        # Fetch Recommendation API (primary source)
        print(f"[1/2] Fetching recommendation data...")
        payload = {
            "sid": int(self.stock_id),
            "exchange": self.exchange,
            "fornews": 1
        }

        result = post_with_retry(
            url=self.recommendation_api_url,
            json_data=payload,
            description="Recommendation API",
            max_retries=5,
            timeout=30,
            required_fields=[],  # Don't validate specific fields
            check_main_header=False  # Don't require main_header for ratios
        )

        if result and str(result.get('code')) == '200' and 'data' in result:
            self.recommendation_data = result['data']

            # Extract quality ratios
            quality_tbl = self.recommendation_data.get('quality', {}).get('quality_tbl', {})
            self.quality_ratios = quality_tbl.get('list', [])

            # Extract valuation ratios
            valuation_tbl = self.recommendation_data.get('valuation', {}).get('valuation_tbl', {})
            self.valuation_ratios = valuation_tbl.get('list', [])

            print(f"   Found {len(self.quality_ratios)} quality ratios")
            print(f"   Found {len(self.valuation_ratios)} valuation ratios")

        # Fetch Summary API (fallback source)
        print(f"[2/2] Fetching summary data (fallback)...")
        payload = {
            "sid": int(self.stock_id),
            "exchange": self.exchange
        }

        result = post_with_retry(
            url=self.summary_api_url,
            json_data=payload,
            description="Summary API",
            max_retries=5,
            timeout=30,
            required_fields=[],  # Don't validate specific fields
            check_main_header=False  # Don't require main_header for ratios
        )

        if result and str(result.get('code')) == '200' and 'data' in result:
            self.summary_data = result['data']

            # If no quality ratios from recommendation API, try summary
            if not self.quality_ratios:
                quality_tbl = self.summary_data.get('key_factors', {}).get('quality', {}).get('quality_tbl', {})
                self.quality_ratios = quality_tbl.get('list', [])
                print(f"   Fallback: Found {len(self.quality_ratios)} quality ratios")

            # If no valuation ratios from recommendation API, try summary
            if not self.valuation_ratios:
                valuation_tbl = self.summary_data.get('key_factors', {}).get('valuation', {}).get('valuation_tbl', {})
                self.valuation_ratios = valuation_tbl.get('list', [])
                print(f"   Fallback: Found {len(self.valuation_ratios)} valuation ratios")

        print("=" * 80)
        print("DATA FETCH COMPLETE")
        print("=" * 80)
        print()

    def _categorize_ratios(self):
        """
        Categorize ratios into subsections based on keywords in ratio names.
        Returns dictionary with categorized ratios.
        """
        categories = {
            'profitability': [],
            'growth': [],
            'leverage': [],
            'efficiency': [],
            'valuation': [],
            'banking': [],  # Special category for bank-specific ratios
            'other': []
        }

        # Categorize quality ratios
        for ratio in self.quality_ratios:
            name = ratio.get('name', '').lower()

            # Banking-specific ratios
            if any(keyword in name for keyword in ['npa', 'gnpa', 'nnpa', 'car', 'nim', 'casa', 'advances', 'deposits']):
                categories['banking'].append(ratio)
            # Profitability indicators
            elif any(keyword in name for keyword in ['roe', 'roa', 'roce', 'margin', 'profit']):
                categories['profitability'].append(ratio)
            # Growth indicators
            elif any(keyword in name for keyword in ['growth', 'cagr']):
                categories['growth'].append(ratio)
            # Leverage indicators
            elif any(keyword in name for keyword in ['debt', 'interest', 'ebitda', 'coverage']):
                categories['leverage'].append(ratio)
            # Efficiency indicators
            elif any(keyword in name for keyword in ['capital employed', 'turnover', 'asset', 'working capital']):
                categories['efficiency'].append(ratio)
            # Tax and payout
            elif any(keyword in name for keyword in ['tax', 'dividend', 'payout']):
                categories['other'].append(ratio)
            else:
                categories['other'].append(ratio)

        # All valuation ratios go to valuation category
        categories['valuation'] = self.valuation_ratios

        return categories

    def _format_ratio_line(self, ratio_name, ratio_value, max_width=42):
        """Format a ratio line with proper alignment"""
        # Ensure value is not None
        if ratio_value is None or ratio_value == '':
            ratio_value = 'N/A'

        # Calculate spacing
        name_width = max_width - len(str(ratio_value))
        formatted_name = ratio_name.ljust(name_width)

        return f"{formatted_name}{ratio_value}"

    def build_section(self):
        """Build SECTION 6 from Quality and Valuation data"""
        # Fetch data first
        self.fetch_quality_valuation_data()

        # Categorize ratios
        categories = self._categorize_ratios()

        # Check if this is a bank stock
        is_bank = self._is_bank_stock()

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 6: KEY FINANCIAL RATIOS & METRICS")
        lines.append("=" * 80)
        lines.append("")
        lines.append("")
        lines.append("")

        # PROFITABILITY RATIOS
        if categories['profitability'] or (is_bank and categories['banking']):
            lines.append("PROFITABILITY RATIOS")
            lines.append("-" * 20)
            lines.append("")

            # For banks, show banking ratios first
            if is_bank and categories['banking']:
                for ratio in categories['banking']:
                    # Filter for profitability-related banking ratios
                    name = ratio.get('name', '').lower()
                    if any(keyword in name for keyword in ['nim', 'roe', 'roa', 'roce']):
                        ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                        lines.append(ratio_line)

            # Add general profitability ratios
            for ratio in categories['profitability']:
                ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                lines.append(ratio_line)

            if not categories['profitability'] and not (is_bank and categories['banking']):
                lines.append("No profitability ratios available")

            lines.append("")
            lines.append("")

        # GROWTH RATIOS
        if categories['growth']:
            lines.append("GROWTH RATIOS")
            lines.append("-" * 13)
            lines.append("")

            for ratio in categories['growth']:
                ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                lines.append(ratio_line)

            lines.append("")
            lines.append("")

        # LEVERAGE & SOLVENCY (Only for non-financial sector stocks)
        # Financial sector stocks (Banks, NBFCs, Insurance, Housing Finance) should not show debt metrics
        if not self._is_financial_sector() and categories['leverage']:
            lines.append("LEVERAGE & SOLVENCY")
            lines.append("-" * 19)
            lines.append("")

            for ratio in categories['leverage']:
                ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                lines.append(ratio_line)

            lines.append("")
            lines.append("")

        # EFFICIENCY RATIOS
        if categories['efficiency']:
            lines.append("EFFICIENCY RATIOS")
            lines.append("-" * 17)
            lines.append("")

            for ratio in categories['efficiency']:
                ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                lines.append(ratio_line)

            lines.append("")
            lines.append("")

        # BANKING-SPECIFIC METRICS (For banks only, non-profitability metrics)
        if is_bank and categories['banking']:
            # Check if there are non-profitability banking ratios
            non_profit_banking = [r for r in categories['banking']
                                 if not any(kw in r.get('name', '').lower() for kw in ['nim', 'roe', 'roa', 'roce'])]

            if non_profit_banking:
                lines.append("BANKING-SPECIFIC METRICS")
                lines.append("-" * 24)
                lines.append("")

                for ratio in non_profit_banking:
                    ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                    lines.append(ratio_line)

                lines.append("")
                lines.append("")

        # VALUATION METRICS
        if categories['valuation']:
            lines.append("VALUATION METRICS")
            lines.append("-" * 17)
            lines.append("")

            for ratio in categories['valuation']:
                ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                lines.append(ratio_line)

            lines.append("")
            lines.append("")

        # OTHER METRICS (Tax, Dividend Payout, etc.)
        if categories['other']:
            lines.append("OTHER METRICS")
            lines.append("-" * 13)
            lines.append("")

            for ratio in categories['other']:
                ratio_line = self._format_ratio_line(ratio.get('name', 'N/A'), ratio.get('value', 'N/A'))
                lines.append(ratio_line)

            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 6 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 6 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 6 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section6Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section6_output.txt")

    output_file = f"section6_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 6 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section6_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
