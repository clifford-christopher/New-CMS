"""
SECTION 7: VALUATION METRICS Builder
Dynamically builds valuation metrics using API data
"""
import requests
import json
import re
from datetime import datetime

# Try importing MongoDB handler
try:
    from mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    print("[WARNING] MongoDB handler not available. Valuation history will not be fetched.")
    MONGODB_AVAILABLE = False

class Section7Builder:
    def __init__(self, stock_id, exchange=0, use_mongodb=True):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.recommendation_api_url = "https://frapi.marketsmojo.com/apiv1/recommendation/getRecoData"
        self.summary_api_url = "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary"
        self.pricemovement_api_url = "https://frapi.marketsmojo.com/apiv1/price/priceupdates"
        self.return_api_url = f"https://frapi.marketsmojo.com/stocks_Returnanalysis/returnAnalysis?se=&cardlist=&period=&alphabet=&sid={stock_id}&exchange={exchange}&page=1&cards=4&1y&cid=34"

        self.recommendation_data = {}
        self.summary_data = {}
        self.pricemovement_data = {}
        self.return_data = {}

        # Will import from Section 6 if needed
        self.dividend_payout = None

        # MongoDB handler for valuation history
        self.use_mongodb = use_mongodb and MONGODB_AVAILABLE
        self.mongo_handler = None
        if self.use_mongodb:
            try:
                self.mongo_handler = MongoDBHandler()
            except Exception as e:
                print(f"[WARNING] MongoDB connection failed: {e}")
                self.use_mongodb = False

    def fetch_recommendation_data(self):
        """Fetch recommendation data for valuation multiples"""
        print(f"[1/3] Fetching recommendation data...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange,
                "fornews": 1
            }

            response = requests.post(self.recommendation_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == '200' and 'data' in result:
                self.recommendation_data = result['data']
                print(f"[OK] Recommendation API successful")
                return True
        except Exception as e:
            print(f"[WARNING] Recommendation API failed: {e}")

        return False

    def fetch_summary_data(self):
        """Fetch summary data for dividend, 52-week range"""
        print(f"[2/3] Fetching summary data...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange
            }

            response = requests.post(self.summary_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == '200' and 'data' in result:
                self.summary_data = result['data']
                print(f"[OK] Summary API successful")
                return True
        except Exception as e:
            print(f"[WARNING] Summary API failed: {e}")

        return False

    def fetch_pricemovement_data(self):
        """Fetch price movement data for current price"""
        print(f"[3/4] Fetching price movement data...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange
            }

            response = requests.post(self.pricemovement_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == '200' and 'data' in result:
                self.pricemovement_data = result['data']
                print(f"[OK] Price movement API successful")
                return True
        except Exception as e:
            print(f"[WARNING] Price movement API failed: {e}")

        return False

    def fetch_return_data(self):
        """Fetch return analysis data for dividend information"""
        print(f"[4/4] Fetching return analysis data...")

        try:
            response = requests.get(self.return_api_url, timeout=30)
            response.raise_for_status()
            result = response.json()

            code = str(result.get('code'))
            if code == '200' and 'data' in result:
                self.return_data = result['data']
                print(f"[OK] Return analysis API successful")
                return True
        except Exception as e:
            print(f"[WARNING] Return analysis API failed: {e}")

        return False

    def fetch_all_data(self):
        """Fetch all required data"""
        print("=" * 80)
        print("FETCHING DATA FROM 4 APIS...")
        print("=" * 80)

        self.fetch_recommendation_data()
        self.fetch_summary_data()
        self.fetch_pricemovement_data()
        self.fetch_return_data()

        print("=" * 80)
        print("DATA FETCH COMPLETE")
        print("=" * 80)
        print()

    def _extract_from_valuation_api(self, field_name):
        """Extract field from recommendation or summary API valuation tables"""
        # Try recommendation API first
        if self.recommendation_data:
            valuation_tbl = self.recommendation_data.get('valuation', {}).get('valuation_tbl', {})
            valuation_list = valuation_tbl.get('list', [])
            for item in valuation_list:
                if item.get('name') == field_name:
                    return item.get('value')

        # Fallback to summary API
        if self.summary_data:
            valuation_tbl = self.summary_data.get('key_factors', {}).get('valuation', {}).get('valuation_tbl', {})
            valuation_list = valuation_tbl.get('list', [])
            for item in valuation_list:
                if item.get('name') == field_name:
                    return item.get('value')

        # Fallback to DNA section for some fields
        if self.summary_data:
            dna_list = self.summary_data.get('dna', {}).get('list', [])
            for item in dna_list:
                if item.get('field') == field_name:
                    return item.get('value')

        return None

    def _get_current_price_and_date(self):
        """Get current price and date"""
        # Try pricemovement API first
        if self.pricemovement_data:
            main_header = self.pricemovement_data.get('main_header', {})
            cmp = main_header.get('cmp', '')
            curr_date = main_header.get('curr_date', '')

            if cmp and curr_date:
                # Parse date - format is "Oct 16"
                try:
                    # Add current year
                    curr_year = datetime.now().year
                    date_str = f"{curr_date} {curr_year}"
                    parsed_date = datetime.strptime(date_str, "%b %d %Y")
                    formatted_date = parsed_date.strftime("%d-%b-%Y")
                    return cmp, formatted_date
                except:
                    return cmp, curr_date

        # Fallback to summary API
        if self.summary_data:
            main_header = self.summary_data.get('main_header', {})
            return main_header.get('cmp', 'N/A'), main_header.get('curr_date', 'N/A')

        return 'N/A', 'N/A'

    def _get_dividend_payout(self):
        """Get dividend payout - try to extract from Section 6 or quality table"""
        # Try recommendation API quality table
        if self.recommendation_data:
            quality_tbl = self.recommendation_data.get('quality', {}).get('quality_tbl', {})
            quality_list = quality_tbl.get('list', [])
            for item in quality_list:
                if item.get('name') == 'Dividend Payout Ratio':
                    return item.get('value')

        # Fallback to summary API
        if self.summary_data:
            quality_tbl = self.summary_data.get('key_factors', {}).get('quality', {}).get('quality_tbl', {})
            quality_list = quality_tbl.get('list', [])
            for item in quality_list:
                if item.get('name') == 'Dividend Payout Ratio':
                    return item.get('value')

        return None

    def _parse_dividend_info(self):
        """Parse dividend information from corporate actions"""
        try:
            corp_actions = self.summary_data.get('corporate_actions', [])

            for action in corp_actions:
                if action.get('title') == 'DIVIDEND':
                    data = action.get('data', [])
                    if data and len(data) > 0:
                        latest_div = data[0]
                        txt = latest_div.get('txt', '')
                        dt = latest_div.get('dt', '')

                        # Parse dividend percentage from text like "1100%"
                        match = re.search(r'<strong>(\d+)%</strong>', txt)
                        if match:
                            div_percent = int(match.group(1))
                            # Assuming face value is Rs.1, dividend per share = div_percent / 100
                            div_per_share = div_percent / 100

                            # Parse ex-date
                            if dt:
                                try:
                                    parsed_date = datetime.strptime(dt, "%Y-%m-%d")
                                    formatted_ex_date = parsed_date.strftime("%b-%d-%Y")
                                except:
                                    formatted_ex_date = dt
                            else:
                                # Try to extract from text
                                ex_match = re.search(r'ex-date:\s*(\d+\s+\w+\s+\d+)', txt)
                                if ex_match:
                                    formatted_ex_date = ex_match.group(1)
                                else:
                                    formatted_ex_date = "N/A"

                            # Use float formatting instead of int() to preserve decimal values
                            return f"Rs.{div_per_share:.2f}", formatted_ex_date

            return None, None
        except:
            return None, None

    def _parse_dividend_from_return_api(self):
        """Parse dividend info from returnAnalysis API - PRIMARY METHOD"""
        try:
            return_summary = self.return_data.get('return_summary_card', {})
            messages = return_summary.get('messages', [])

            for msg in messages:
                prefix = msg.get('prefix', '')
                suffix = msg.get('suffix', '')

                # Look for dividend message
                if 'Dividend Yield' in prefix or 'dividend' in suffix.lower():
                    # suffix format: "latest dividend: 2.7 per share ex-dividend date: Mar-07-2025"
                    div_match = re.search(r'latest dividend:\s*([\d.]+)', suffix)
                    date_match = re.search(r'ex-dividend date:\s*([\w]+-\d+-\d+)', suffix)

                    if div_match:
                        div_value = div_match.group(1)
                        ex_date = date_match.group(1) if date_match else None
                        return f"Rs.{div_value}", ex_date

            return None, None
        except Exception as e:
            print(f"[WARNING] Error parsing dividend from return API: {e}")
            return None, None

    def _get_52week_range(self):
        """Get 52-week high and low"""
        # Try summary API first
        if self.summary_data:
            hw = self.summary_data.get('52wk_highlow', {})
            high = hw.get('52wk_high')
            low = hw.get('52wk_low')
            if high and low:
                return high, low

        # Fallback to pricemovement API
        if self.pricemovement_data:
            price_stats = self.pricemovement_data.get('TODAY_PRICE_STATS', [])
            if price_stats:
                # Use BSE data (first entry)
                high = price_stats[0].get('52wk_high')
                low = price_stats[0].get('52wk_low')
                if high and low:
                    return high, low

        return None, None

    def _calculate_distance_from_52w(self, current_price, high, low):
        """Calculate distance from 52-week high and low"""
        try:
            # Clean price strings
            cmp = float(str(current_price).replace(',', ''))
            high_val = float(str(high).replace(',', ''))
            low_val = float(str(low).replace(',', ''))

            # Distance from high (usually negative)
            dist_from_high = ((cmp - high_val) / high_val) * 100

            # Distance from low (usually positive)
            dist_from_low = ((cmp - low_val) / low_val) * 100

            # Format with sign
            high_str = f"{dist_from_high:+.2f}%"
            low_str = f"{dist_from_low:+.2f}%"

            return high_str, low_str
        except:
            return "N/A", "N/A"

    def _get_valuation_grade_history(self):
        """Get valuation grade history from MongoDB"""
        if not self.use_mongodb or not self.mongo_handler:
            return None, None

        try:
            # Get current grade
            current_grade = self.mongo_handler.get_current_valuation_grade(int(self.stock_id))

            # Get grade history
            history = self.mongo_handler.get_valuation_grade_history(int(self.stock_id), limit=5)

            return current_grade, history
        except Exception as e:
            print(f"[WARNING] Error fetching valuation history: {e}")
            return None, None

    def build_section(self):
        """Build SECTION 7 from API data"""
        # Fetch all data first
        self.fetch_all_data()

        # Get current price and date
        current_price, current_date = self._get_current_price_and_date()

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append(f"SECTION 7: VALUATION METRICS (as of {current_date}, Price: Rs.{current_price})")
        lines.append("=" * 80)
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

        # VALUATION MULTIPLES
        lines.append("VALUATION MULTIPLES:")
        lines.append("-" * 20)

        # P/E Ratio
        pe = self._extract_from_valuation_api("P/E Ratio")
        lines.append(f"P/E Ratio (TTM):                      {pe}x" if pe else "P/E Ratio (TTM):                      N/A")

        # Price to Book Value
        pbv = self._extract_from_valuation_api("Price to Book Value")
        if not pbv:
            pbv = self._extract_from_valuation_api("Price to Book")
        lines.append(f"Price to Book Value (P/BV):           {pbv}x" if pbv else "Price to Book Value (P/BV):           N/A")

        # EV/EBITDA
        ev_ebitda = self._extract_from_valuation_api("EV to EBITDA")
        lines.append(f"EV/EBITDA:                            {ev_ebitda}x" if ev_ebitda else "EV/EBITDA:                            N/A")

        # EV/EBIT
        ev_ebit = self._extract_from_valuation_api("EV to EBIT")
        lines.append(f"EV/EBIT:                              {ev_ebit}x" if ev_ebit else "EV/EBIT:                              N/A")

        # EV/Sales
        ev_sales = self._extract_from_valuation_api("EV to Sales")
        lines.append(f"EV/Sales:                             {ev_sales}x" if ev_sales else "EV/Sales:                             N/A")

        # EV/Capital Employed
        ev_ce = self._extract_from_valuation_api("EV to Capital Employed")
        lines.append(f"EV/Capital Employed:                  {ev_ce}x" if ev_ce else "EV/Capital Employed:                  N/A")

        # PEG Ratio
        peg = self._extract_from_valuation_api("PEG Ratio")
        lines.append(f"PEG Ratio:                            {peg}x" if peg else "PEG Ratio:                            N/A")

        lines.append("")

        # DIVIDEND METRICS
        lines.append("DIVIDEND METRICS:")
        lines.append("-" * 17)

        # Dividend Yield
        div_yield = self._extract_from_valuation_api("Dividend Yield")
        lines.append(f"Dividend Yield:                       {div_yield}" if div_yield else "Dividend Yield:                       N/A")

        # Latest Dividend and Ex-Date - Multi-tier fallback approach
        # Method 1: Try returnAnalysis API first (most reliable - structured data)
        div_per_share, ex_date = self._parse_dividend_from_return_api()

        # Method 2: Fallback to tot_returns sentence (getSummary API)
        if not div_per_share:
            try:
                tot_returns = self.summary_data.get('tot_returns', {})
                sentence = tot_returns.get('sentence', '')
                div_match = re.search(r'Latest dividend:\s*([\d.]+)', sentence)
                date_match = re.search(r'ex-dividend date:\s*([\w]+-\d+-\d+)', sentence)
                if div_match:
                    div_per_share = f"Rs.{div_match.group(1)}"
                    if date_match and not ex_date:
                        ex_date = date_match.group(1)
            except:
                pass

        # Method 3: Calculate from dividend yield and current price (fallback 2)
        if not div_per_share:
            try:
                div_yield_val = self._extract_from_valuation_api("Dividend Yield")
                main_header = self.summary_data.get('main_header', {})
                cmp = main_header.get('cmp', '')

                if div_yield_val and cmp:
                    yield_val = float(div_yield_val.replace('%', ''))
                    price_val = float(str(cmp).replace(',', ''))
                    dividend = (yield_val * price_val) / 100
                    div_per_share = f"Rs.{dividend:.2f}"
                    print(f"[INFO] Calculated dividend from yield: {div_per_share}")
            except:
                pass

        # Method 4: Corporate actions with int() (last resort - fallback 3)
        if not div_per_share:
            div_per_share, ex_date = self._parse_dividend_info()

        lines.append(f"Latest Dividend:                      {div_per_share} per share" if div_per_share else "Latest Dividend:                      N/A")
        lines.append(f"Ex-Dividend Date:                     {ex_date}" if ex_date else "Ex-Dividend Date:                     N/A")

        # Dividend Payout
        div_payout = self._get_dividend_payout()
        lines.append(f"Dividend Payout:                      {div_payout}" if div_payout else "Dividend Payout:                      N/A")

        lines.append("")

        # VALUATION ASSESSMENT
        lines.append("VALUATION ASSESSMENT:")
        lines.append("-" * 21)

        # Get valuation grade and history from MongoDB
        current_grade, grade_history = self._get_valuation_grade_history()

        # Overall Valuation
        if current_grade:
            lines.append(f"Overall Valuation:                    {current_grade.upper()}")
        else:
            lines.append(f"Overall Valuation:                    Data Not Available")

        # Valuation Grade History
        if grade_history and len(grade_history) > 0:
            lines.append(f"Valuation Grade History:")
            for change in grade_history:
                from_grade = self.mongo_handler._format_valuation_grade(change['from_grade'])
                to_grade = self.mongo_handler._format_valuation_grade(change['to_grade'])
                date = change['formatted_date']
                lines.append(f"- Changed to {to_grade} from {from_grade}: {date}")
        else:
            lines.append(f"Valuation Grade History:              Data Not Available")

        lines.append("")

        # 52-WEEK RANGE
        lines.append("52-WEEK RANGE:")
        lines.append("-" * 14)

        high_52w, low_52w = self._get_52week_range()

        if high_52w:
            lines.append(f"52-Week High:                         Rs.{high_52w}")
        else:
            lines.append(f"52-Week High:                         N/A")

        if low_52w:
            lines.append(f"52-Week Low:                          Rs.{low_52w}")
        else:
            lines.append(f"52-Week Low:                          N/A")

        # Calculate distances
        if high_52w and low_52w and current_price != 'N/A':
            dist_high, dist_low = self._calculate_distance_from_52w(current_price, high_52w, low_52w)
            lines.append(f"Current Distance from High:           {dist_high}")
            lines.append(f"Current Distance from Low:            {dist_low}")
        else:
            lines.append(f"Current Distance from High:           N/A")
            lines.append(f"Current Distance from Low:            N/A")

        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 7 saved to: {output_file}")
        return section_text

    def cleanup(self):
        """Clean up resources"""
        if self.mongo_handler:
            self.mongo_handler.close()


def main():
    """Test the Section 7 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 7 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section7Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section7_output.txt")

    output_file = f"section7_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 7 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section7_output.txt")
    print(f"  - {output_file}")

    # Cleanup MongoDB connection
    builder.cleanup()


if __name__ == "__main__":
    main()
