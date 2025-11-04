"""
SECTION 1: COMPANY INFORMATION Builder
Dynamically builds Section 1 using API data
"""
import requests
import json
from datetime import datetime
from api_utils import post_with_retry

class Section1Builder:
    def __init__(self, stock_id, exchange=0, main_header_fallback=None):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.apis = {
            "summary": "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary",
            "company_cv": "https://frapi.marketsmojo.com/apiv1/company_cv/getCompanyCvDetails",
            "balance_sheet": "https://frapi.marketsmojo.com/apiv1/financials/get-balancesheet"
        }
        self.data = {}
        self.main_header_fallback = main_header_fallback  # Store fallback header from other sections

    def _is_bank_stock(self):
        """
        Check if the stock is a bank based on industry name.
        Banks require standalone data preference over consolidated.

        Returns:
            Boolean: True if bank stock, False otherwise
        """
        try:
            summary_data = self.data.get('summary', {})
            main_header = summary_data.get('main_header', {})
            ind_name = main_header.get('ind_name', '').lower()

            # Check if 'bank' is in the industry name
            return 'bank' in ind_name
        except:
            return False

    def _get_most_recent_period(self, period_dates):
        """
        Get the most recent period key from period_dates array.
        The first item is usually a label, second item is the most recent period.

        Args:
            period_dates: List of period date objects with 'key' and 'label'

        Returns:
            String key of the most recent period (e.g., 'mar25') or None
        """
        try:
            if not period_dates or len(period_dates) < 2:
                return None

            # Skip first item (label), return second item's key (most recent period)
            for i, period in enumerate(period_dates):
                if i > 0:  # Skip index 0 which is the label
                    return period.get('key')
            return None
        except:
            return None

    def fetch_data(self):
        """Fetch data from all required APIs"""
        print(f"Fetching data for Stock ID: {self.stock_id}")

        # Fetch Summary API
        summary_payload = {"sid": int(self.stock_id), "exchange": self.exchange}
        self.data['summary'] = self._call_api("summary", summary_payload)

        # Fetch CompanyCv API
        company_cv_payload = {"sid": int(self.stock_id), "exchange": self.exchange}
        self.data['company_cv'] = self._call_api("company_cv", company_cv_payload)

        # Fetch Balance Sheet API (Annual)
        balance_sheet_payload = {"sid": self.stock_id, "exchange": self.exchange, "period": "y"}
        self.data['balance_sheet'] = self._call_api("balance_sheet", balance_sheet_payload)

        return self.data

    def _call_api(self, api_name, payload):
        """Make API call with retry logic, validation and return data"""
        url = self.apis[api_name]

        # Define required fields for each API
        required_fields = {
            'summary': [],  # main_header is checked by default
            'company_cv': ['know_your_company'],
            'balance_sheet': ['snapshot']
        }

        # Use retry logic with validation
        result = post_with_retry(
            url=url,
            json_data=payload,
            description=f"{api_name} API",
            max_retries=5,
            timeout=30,
            required_fields=required_fields.get(api_name, [])
        )

        if result and result.get('code') == '200' and 'data' in result:
            data = result['data']

            # Store main_header for fallback if available
            if 'main_header' in data and data['main_header']:
                if not self.main_header_fallback or not self.main_header_fallback.get('stock_name'):
                    self.main_header_fallback = data['main_header']
                    print(f"[INFO] Stored main_header from {api_name} API for fallback")

            return data
        else:
            # If we got a response but not valid data
            if result:
                print(f"[WARNING] {api_name} API returned code: {result.get('code', 'unknown')} or invalid data")
            return {}

    def build_section(self):
        """Build SECTION 1 from API data"""
        if not self.data:
            self.fetch_data()

        # Extract data from APIs
        summary_data = self.data.get('summary', {})
        company_cv_data = self.data.get('company_cv', {})
        balance_sheet_data = self.data.get('balance_sheet', {})

        # Get main header data with fallback logic
        main_header = summary_data.get('main_header', {})

        # If summary API didn't provide main_header, try other sources
        if not main_header or not main_header.get('stock_name'):
            # Try from company_cv
            if company_cv_data and 'main_header' in company_cv_data:
                main_header = company_cv_data.get('main_header', {})
                print("[INFO] Using main_header from company_cv API")
            # Try from balance_sheet
            elif balance_sheet_data and 'main_header' in balance_sheet_data:
                main_header = balance_sheet_data.get('main_header', {})
                print("[INFO] Using main_header from balance_sheet API")
            # Use the stored fallback
            elif self.main_header_fallback:
                main_header = self.main_header_fallback
                print("[INFO] Using fallback main_header stored during API calls")

        # Get company CV data
        know_your_company = company_cv_data.get('know_your_company', {})
        company_coordinates = company_cv_data.get('company_coordinates', {}).get('company_details', {})

        # Handle case where company_details is a string (e.g., "No Company Details Available")
        if not isinstance(company_coordinates, dict):
            company_coordinates = {}

        # Get balance sheet snapshot (latest year)
        bs_snapshot = balance_sheet_data.get('snapshot', {})

        # Get DNA data for additional metrics
        dna_data = summary_data.get('dna', {})

        # Build the section text
        section_lines = []
        section_lines.append("=" * 80)
        section_lines.append("SECTION 1: COMPANY INFORMATION")
        section_lines.append("=" * 80)
        section_lines.append("")
        section_lines.append("")

        # Company Name
        full_name = main_header.get('full_name', 'N/A')
        section_lines.append(f"Company Name: {full_name}")

        # Ticker Symbol
        stock_name = main_header.get('stock_name', 'N/A')
        scripcode = main_header.get('scripcode', 'N/A')
        symbol_nse = main_header.get('symbol', 'N/A')
        section_lines.append(f"Ticker Symbol: {symbol_nse} (NSE), {scripcode} (BSE)")

        # ISIN
        isin = main_header.get('isin', 'N/A')
        section_lines.append(f"ISIN: {isin}")

        # Industry
        ind_name = main_header.get('ind_name', 'N/A')
        section_lines.append(f"Industry: {ind_name}")

        # Market Capitalization
        mcapval = main_header.get('mcapval', 'N/A')
        section_lines.append(f"Market Capitalization: {mcapval}")

        # Current Market Price
        cmp = main_header.get('cmp', 'N/A')
        curr_date = main_header.get('curr_date', 'N/A')
        traded_date = main_header.get('traded_date', 'N/A')
        section_lines.append(f"Current Market Price: {cmp} (as of {traded_date})")

        # Price Change (1D)
        chgp = main_header.get('chgp', 'N/A')
        section_lines.append(f"Price Change (1D): {chgp}")

        # Face Value - Need to get from balance sheet or capital structure
        face_value = self._get_face_value(company_cv_data, balance_sheet_data)
        section_lines.append(f"Face Value: {face_value}")

        # Company Size
        mcap = main_header.get('mcap', 'N/A')
        section_lines.append(f"Company Size: {mcap}")

        # Sector Position - From quality data
        sector_position = self._get_sector_position(summary_data)
        if sector_position:
            section_lines.append(f"Sector Position: {sector_position}")

        section_lines.append("")

        # Equity Capital and Shares
        equity_capital, num_shares = self._get_equity_data(company_cv_data)
        if equity_capital:
            section_lines.append(f"Equity Capital: {equity_capital} Crores")
        if num_shares:
            section_lines.append(f"Number of Shares: {num_shares} Crores shares")

        # Book Value per Share
        book_value = self._get_book_value(balance_sheet_data)
        if book_value and book_value != "N/A":
            section_lines.append(f"Book Value per Share: {book_value}")

        section_lines.append("")

        # Company Address
        section_lines.append("Company Address:")
        address = company_coordinates.get('address', 'N/A')
        section_lines.append(address)

        # Email
        email = company_coordinates.get('Email', 'N/A')
        section_lines.append(f"Email: {email}")

        # Website
        website = company_coordinates.get('Website', 'N/A')
        section_lines.append(f"Website: {website}")

        section_lines.append("")

        # Company History
        section_lines.append("Company History:")
        about_company = know_your_company.get('about_the_company', 'N/A')
        section_lines.append(f"- {about_company}")

        section_lines.append("")
        section_lines.append("")

        return "\n".join(section_lines)

    def _get_face_value(self, company_cv_data, balance_sheet_data):
        """Get face value from capital structure"""
        try:
            capital_structure = company_cv_data.get('capital_structure', {})
            if capital_structure:
                sentences = capital_structure.get('sentence', [])
                for item in sentences:
                    if item.get('text') == 'Face Value':
                        value = item.get('value', 'N/A')
                        # Extract just the number (e.g., "INR 1.0" -> "₹1")
                        if 'INR' in value:
                            num_part = value.replace('INR', '').strip()
                            return f"₹{num_part}"
                        return value
            return "N/A"
        except:
            return "N/A"

    def _get_sector_position(self, summary_data):
        """Get sector position from quality message"""
        try:
            quality = summary_data.get('key_factors', {}).get('quality', {}).get('quality', {})
            messages = quality.get('q_msg', [])

            for msg in messages:
                if 'company in' in msg.lower() and 'sector' in msg.lower():
                    return msg
            return None
        except:
            return None

    def _get_equity_data(self, company_cv_data):
        """Get equity capital and number of shares from capital structure"""
        try:
            capital_structure = company_cv_data.get('capital_structure', {})
            if capital_structure:
                sentences = capital_structure.get('sentence', [])

                equity_capital = None
                num_shares = None

                for item in sentences:
                    text = item.get('text', '')
                    value = item.get('value', '')

                    if text == 'Present Equity Capital':
                        # Extract value (e.g., "INR 361.81 Cr" -> "₹361.81")
                        equity_capital = value.replace('INR', '₹').replace(' Cr', '')

                    elif text == 'Number of Shares':
                        # Extract value (e.g., "361.81 Cr" -> "361.81")
                        num_shares = value.replace(' Cr', '')

                return equity_capital, num_shares
            return None, None
        except:
            return None, None

    def _get_book_value(self, balance_sheet_data):
        """
        Get book value per share from balance sheet - always use most recent period.
        For banks: Prefer standalone, fallback to consolidated.
        For non-banks: Prefer consolidated, fallback to standalone.
        """
        try:
            snapshot = balance_sheet_data.get('snapshot', {})
            is_bank = self._is_bank_stock()

            # Determine order of preference based on stock type
            if is_bank:
                # Banks: Standalone first, then consolidated
                data_sources = [
                    ('standalone', snapshot.get('standalone', {}).get('data', {}), 'standalone'),
                    ('consolidate', snapshot.get('consolidate', {}).get('data', {}), 'consolidate')
                ]
                print(f"[INFO] Bank stock detected - preferring standalone data")
            else:
                # Non-banks: Consolidated first, then standalone
                data_sources = [
                    ('consolidate', snapshot.get('consolidate', {}).get('data', {}), 'consolidate'),
                    ('standalone', snapshot.get('standalone', {}).get('data', {}), 'standalone')
                ]

            # Try each data source in order of preference
            for source_name, data, key_name in data_sources:
                if not data:
                    continue

                # Get the most recent period dynamically
                period_dates = data.get('period_dates', [])
                recent_period_key = self._get_most_recent_period(period_dates)

                if recent_period_key:
                    # Find book value in the data
                    items = data.get(key_name, [])
                    for item in items:
                        if item.get(key_name) == 'Book Value per share (adjusted)':
                            book_value = item.get(recent_period_key)
                            if book_value:
                                # Check if book value is 0 or "0"
                                if str(book_value) == "0" or book_value == 0:
                                    print(f"[INFO] Book value is 0 - treating as N/A")
                                    continue  # Try next data source
                                print(f"[INFO] Book value fetched from {source_name} data: Rs.{book_value}")
                                return f"₹{book_value}"

            return "N/A"
        except Exception as e:
            print(f"[DEBUG] Book value error: {e}")
            return "N/A"

    def get_main_header(self):
        """Return the main_header for other sections to use"""
        return self.main_header_fallback

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 1 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 1 builder"""
    # TCS Stock ID
    stock_id = 513374

    print("=" * 80)
    print("SECTION 1 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section1Builder(stock_id)
    section_text = builder.build_section()

    # Save to file first
    builder.save_to_file("section1_output.txt")

    # Also save with stock ID in filename
    output_file = f"section1_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 1 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section1_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
