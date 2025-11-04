"""
SECTION 9: STOCK PRICE & RETURNS ANALYSIS Builder
Dynamically builds stock price and returns analysis using API data
"""
import requests
import json
from datetime import datetime

class Section9Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.price_api_url = "https://frapi.marketsmojo.com/apiv1/price/priceupdates"
        self.return_api_url = f"https://frapi.marketsmojo.com/stocks_Returnanalysis/returnAnalysis?se=&cardlist=&period=&alphabet=&sid={stock_id}&exchange={exchange}&page=1&cards=4&1y&cid=34"
        self.summary_api_url = "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary"

        self.price_data = {}
        self.return_data = {}
        self.summary_data = {}

    def fetch_price_data(self):
        """Fetch price movement data"""
        print(f"Fetching price movement data...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange
            }

            response = requests.post(self.price_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Handle both string and int codes
            code = str(result.get('code'))
            if code == '200' and 'data' in result:
                self.price_data = result['data']
                print(f"[OK] Price API successful")
                return True
            else:
                print(f"[WARNING] Price API returned code: {code}")
        except Exception as e:
            print(f"[WARNING] Price API failed: {e}")

        return False

    def fetch_return_data(self):
        """Fetch return analysis data"""
        print(f"Fetching return analysis data...")

        try:
            response = requests.get(self.return_api_url, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Handle both string and int codes
            code = str(result.get('code'))
            if code == '200' and 'data' in result:
                self.return_data = result['data']
                print(f"[OK] Return API successful")
                return True
            else:
                print(f"[WARNING] Return API returned code: {code}")
        except Exception as e:
            print(f"[WARNING] Return API failed: {e}")

        return False

    def fetch_summary_data(self):
        """Fetch stock summary data to get stock name and industry"""
        print(f"Fetching stock summary data...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange
            }

            response = requests.post(self.summary_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            code = str(result.get('code'))
            if code == '200' and 'data' in result:
                self.summary_data = result['data']
                print(f"[OK] Summary API successful")
                return True
            else:
                print(f"[WARNING] Summary API returned code: {code}")
        except Exception as e:
            print(f"[WARNING] Summary API failed: {e}")

        return False

    def _get_stock_name_and_sector(self):
        """Extract stock name and industry from summary data"""
        try:
            main_header = self.summary_data.get('main_header', {})
            stock_name = main_header.get('stock_name', 'Stock')
            ind_name = main_header.get('ind_name', 'Industry')

            # Return stock name, industry name (for backward compatibility), and full industry
            return stock_name, ind_name, ind_name
        except:
            return "Stock", "Industry", ""

    def _extract_current_price_data(self):
        """Extract current price data from TODAY_PRICE_STATS"""
        try:
            price_stats = self.price_data.get('TODAY_PRICE_STATS', [])

            # Use BSE data if available, else NSE
            stats = None
            for item in price_stats:
                if item.get('exch', '').upper() == 'BSE':
                    stats = item
                    break

            if not stats and len(price_stats) > 0:
                stats = price_stats[0]  # Fallback to first available

            if not stats:
                return None

            # Extract fields
            price_info = {
                'date': stats.get('date', 'N/A'),
                'last_traded_price': stats.get('price', 'N/A'),
                'prev_close': 'N/A',
                'open': 'N/A',
                'day_high': stats.get('today_high', 'N/A'),
                'day_low': stats.get('today_low', 'N/A'),
                'volume': 'N/A',
                'weighted_avg': 'N/A'
            }

            # Extract from fields array
            for field_obj in stats.get('fields', []):
                name = field_obj.get('name', '')
                value = field_obj.get('value', '')

                if 'Prev. Close' in name:
                    price_info['prev_close'] = value
                elif 'Open Price' in name:
                    price_info['open'] = value
                elif 'Volume traded' in name:
                    price_info['volume'] = value
                elif 'Weighted Avg Price' in name:
                    price_info['weighted_avg'] = value

            return price_info
        except Exception as e:
            print(f"[WARNING] Error extracting price data: {e}")
            return None

    def _extract_moving_averages(self):
        """Extract moving averages from MOVING_AVERAGES"""
        try:
            ma_data = self.price_data.get('MOVING_AVERAGES', [])

            # Use BSE data if available, else NSE
            ma_info = None
            for item in ma_data:
                if item.get('exch', '').upper() == 'BSE':
                    ma_info = item
                    break

            if not ma_info and len(ma_data) > 0:
                ma_info = ma_data[0]  # Fallback to first available

            if not ma_info:
                return None

            # Extract MA values
            ma_values = {}
            for item in ma_info.get('data', []):
                field = item.get('field', '')
                value = item.get('value', 'N/A')

                if 'Days' in field:
                    ma_values[field] = value

            # Get position message
            msg = ma_info.get('msg', '')
            position = 'N/A'
            if 'lower' in msg.lower():
                position = 'Stock BELOW'
            elif 'higher' in msg.lower():
                position = 'Stock ABOVE'

            return {'values': ma_values, 'position': position}
        except Exception as e:
            print(f"[WARNING] Error extracting moving averages: {e}")
            return None

    def _extract_returns_table(self):
        """Extract returns comparison from stock_vs_sensex_card"""
        try:
            vs_sensex = self.return_data.get('stock_vs_sensex_card', {})

            # Map period keys to display names
            period_mapping = {
                '1D': '1 day',
                '1W': '1 week',
                '1M': '1 month',
                '3M': '3 month',
                '6M': '6 month',
                'YTD': 'YTD',
                '1Y': '1 year',
                '2Y': '2 years',
                '3Y': '3 years',
                '4Y': '4 year',
                '5Y': '5 years',
                '10Y': '10 year'
            }

            returns_table = []
            for key, display in period_mapping.items():
                period_data = vs_sensex.get(key, {})
                stock_data = period_data.get('STOCK', {})
                sensex_data = period_data.get('SENSEX', {})

                stock_val = stock_data.get('value', 'N/A')
                stock_dir = stock_data.get('dir', 0)
                sensex_val = sensex_data.get('value', 'N/A')
                sensex_dir = sensex_data.get('dir', 0)

                # Treat "0.00" with dir=0 as missing data (not truly 0% return)
                if stock_val == "0.00" and stock_dir == 0:
                    stock_val = 'N/A'
                if sensex_val == "0.00" and sensex_dir == 0:
                    sensex_val = 'N/A'

                # Calculate alpha - ONLY if both stock and sensex have valid data
                alpha = 'N/A'
                if stock_val != 'N/A' and sensex_val != 'N/A':
                    try:
                        stock_num = float(stock_val)
                        sensex_num = float(sensex_val)
                        alpha_num = stock_num - sensex_num
                        alpha = f"{alpha_num:+.2f}%"  # With sign
                    except:
                        alpha = 'N/A'

                # Format percentages
                stock_return = f"{stock_val}%" if stock_val != 'N/A' else 'N/A'
                sensex_return = f"{sensex_val}%" if sensex_val != 'N/A' else 'N/A'

                returns_table.append({
                    'period': display,
                    'stock_return': stock_return,
                    'sensex_return': sensex_return,
                    'alpha': alpha
                })

            return returns_table
        except Exception as e:
            print(f"[WARNING] Error extracting returns table: {e}")
            return []

    def _extract_sector_comparison(self):
        """Extract sector comparison from return_summary_card"""
        try:
            summary = self.return_data.get('return_summary_card', {})

            sector_info = summary.get('sector_return', {})
            stock_return = summary.get('stock_return', {}).get('sentence2', 'N/A')

            # Parse sector return from sentence like "SECTOR -19.37"
            sector_sentence = sector_info.get('sentence2', '')
            sector_return = 'N/A'
            if 'SECTOR' in sector_sentence:
                parts = sector_sentence.split('SECTOR')
                if len(parts) > 1:
                    sector_return = parts[1].strip()

            # Parse underperformance from sentence like "UNDERPERFORMED BY -8.42"
            perf_sentence = sector_info.get('sentence1', '')
            performance = 'N/A'
            if 'BY' in perf_sentence:
                parts = perf_sentence.split('BY')
                if len(parts) > 1:
                    performance = parts[1].strip()

            return {
                'stock_return': f"{stock_return}%",
                'sector_return': f"{sector_return}%",
                'performance': performance
            }
        except Exception as e:
            print(f"[WARNING] Error extracting sector comparison: {e}")
            return None

    def _extract_risk_adjusted_returns(self):
        """Extract risk-adjusted returns from risk_card"""
        try:
            risk_card = self.return_data.get('risk_card', {})

            # Get period (default to 1Y)
            periods = risk_card.get('periods', [])
            selected_period = '1Y' if '1Y' in periods else (periods[0] if periods else '1Y')

            # Get table data
            table = risk_card.get('table', [])
            if len(table) < 3:
                return None

            # Table structure: [headers, TCS row, Sensex row]
            stock_row = table[1] if len(table) > 1 else []
            sensex_row = table[2] if len(table) > 2 else []

            risk_info = {
                'stock_absolute': stock_row[1] if len(stock_row) > 1 else 'N/A',
                'stock_risk_adjusted': stock_row[2] if len(stock_row) > 2 else 'N/A',
                'stock_volatility': stock_row[3] if len(stock_row) > 3 else 'N/A',
                'sensex_absolute': sensex_row[1] if len(sensex_row) > 1 else 'N/A',
                'sensex_risk_adjusted': sensex_row[2] if len(sensex_row) > 2 else 'N/A',
                'sensex_volatility': sensex_row[3] if len(sensex_row) > 3 else 'N/A',
                'risk_category': risk_card.get('sub_header', 'N/A')
            }

            return risk_info
        except Exception as e:
            print(f"[WARNING] Error extracting risk-adjusted returns: {e}")
            return None

    def _extract_beta_info(self):
        """Extract beta information from return_summary_card messages"""
        try:
            summary = self.return_data.get('return_summary_card', {})
            messages = summary.get('messages', [])

            beta_info = {
                'beta': 'N/A',
                'classification': 'N/A',
                'interpretation': 'N/A'
            }

            for msg in messages:
                prefix = msg.get('prefix', '')
                suffix = msg.get('suffix', '')

                if 'Beta' in prefix:
                    # Extract classification from prefix like "Medium Beta Stock"
                    beta_info['classification'] = prefix

                    # Extract beta value from suffix like "TCS has a beta(adjusted beta) of 1.00 with SENSEX"
                    if 'beta' in suffix:
                        import re
                        match = re.search(r'of\s+([\d.]+)', suffix)
                        if match:
                            beta_info['beta'] = match.group(1)

                    # Set interpretation based on classification
                    if 'High' in prefix:
                        beta_info['interpretation'] = 'More volatile than the market'
                    elif 'Medium' in prefix:
                        beta_info['interpretation'] = 'Generally rise and fall in line with the market'
                    elif 'Low' in prefix:
                        beta_info['interpretation'] = 'Less volatile than the market'

            return beta_info
        except Exception as e:
            print(f"[WARNING] Error extracting beta info: {e}")
            return None

    def build_section(self):
        """Build SECTION 9 from API data"""
        # Fetch all data first (if not already loaded)
        if not self.price_data:
            if not self.fetch_price_data():
                return "ERROR: Failed to fetch price data"

        if not self.return_data:
            if not self.fetch_return_data():
                return "ERROR: Failed to fetch return data"

        # Fetch summary data to get stock name and sector
        if not self.summary_data:
            self.fetch_summary_data()

        # Get stock name and sector
        stock_name, sector_name, full_industry = self._get_stock_name_and_sector()

        # Extract all components
        price_info = self._extract_current_price_data()
        ma_info = self._extract_moving_averages()
        returns_table = self._extract_returns_table()
        sector_comp = self._extract_sector_comparison()
        risk_info = self._extract_risk_adjusted_returns()
        beta_info = self._extract_beta_info()

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 9: STOCK PRICE & RETURNS ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        lines.append("")

        # CURRENT PRICE DATA
        if price_info:
            lines.append(f"CURRENT PRICE DATA ({price_info.get('date', 'N/A')}):")
            lines.append("-" * 33)
            lines.append(f"Last Traded Price:                    ₹{price_info.get('last_traded_price', 'N/A')},")
            lines.append(f"Previous Close:                       ₹{price_info.get('prev_close', 'N/A')}")
            lines.append(f"Open:                                 ₹{price_info.get('open', 'N/A')}")
            lines.append(f"Day's High:                           ₹{price_info.get('day_high', 'N/A')}")
            lines.append(f"Day's Low:                            ₹{price_info.get('day_low', 'N/A')}")
            lines.append(f"Volume Traded:                        {price_info.get('volume', 'N/A')} shares")
            lines.append(f"Weighted Avg Price:                   ₹{price_info.get('weighted_avg', 'N/A')}")
            lines.append("")

        # MOVING AVERAGES
        if ma_info:
            lines.append("MOVING AVERAGES:")
            lines.append("-" * 16)
            ma_values = ma_info.get('values', {})
            position = ma_info.get('position', 'N/A')

            for field in ['5 Days', '20 Days', '50 Days', '100 Days', '200 Days']:
                value = ma_values.get(field, 'N/A')
                lines.append(f"{field} MA:{''.ljust(34 - len(field))}₹{value} ({position})")
            lines.append("")

        # PRICE RETURNS
        if returns_table and len(returns_table) > 0:
            lines.append("PRICE RETURNS:")
            lines.append("-" * 14)
            lines.append(f"{'Period':<16}{'Stock Return':<16}{'Sensex Return':<16}Alpha")
            lines.append("-" * 54)

            for row in returns_table:
                period = row['period']
                stock = row['stock_return']
                sensex = row['sensex_return']
                alpha = row['alpha']
                lines.append(f"{period:<16}{stock:<16}{sensex:<16}{alpha}")
            lines.append("")

        # SECTOR COMPARISON
        if sector_comp:
            lines.append("SECTOR COMPARISON:")
            lines.append("-" * 18)
            # Use dynamic stock name, pad to 25 chars for alignment
            stock_label = f"1 Year Return ({stock_name}):"
            stock_label = stock_label.ljust(38)
            lines.append(f"{stock_label}{sector_comp.get('stock_return', 'N/A')}")

            # Use dynamic sector name
            sector_label = f"{full_industry if full_industry else sector_name} Return:"
            sector_label = sector_label.ljust(38)
            lines.append(f"{sector_label}{sector_comp.get('sector_return', 'N/A')}")

            lines.append(f"Underperformance vs Sector:           {sector_comp.get('performance', 'N/A')}")
            lines.append("")
            lines.append("")

        # RISK-ADJUSTED RETURNS
        if risk_info:
            lines.append("RISK-ADJUSTED RETURNS (1 Year):")
            lines.append("-" * 32)
            lines.append(f"Stock Absolute Return:                {risk_info.get('stock_absolute', 'N/A')}")
            lines.append(f"Risk-Adjusted Return:                 {risk_info.get('stock_risk_adjusted', 'N/A')}")
            lines.append(f"Volatility:                           {risk_info.get('stock_volatility', 'N/A')}")
            lines.append(f"Sharpe Ratio:                         {'Negative' if '-' in str(risk_info.get('stock_risk_adjusted', '')) else 'Positive'}")
            lines.append(f"Risk Category:                        {risk_info.get('risk_category', 'N/A').upper()}")
            lines.append("")
            lines.append(f"Sensex Absolute Return:               {risk_info.get('sensex_absolute', 'N/A')}")
            lines.append(f"Sensex Risk-Adjusted Return:          {risk_info.get('sensex_risk_adjusted', 'N/A')}")
            lines.append(f"Sensex Volatility:                    {risk_info.get('sensex_volatility', 'N/A')}")
            lines.append("")

        # BETA & RISK
        if beta_info:
            lines.append("BETA & RISK:")
            lines.append("-" * 12)
            classification = beta_info.get('classification', 'N/A')
            beta_val = beta_info.get('beta', 'N/A')

            # Extract just the beta category from classification
            beta_category = 'N/A'
            if 'Medium Beta' in classification:
                beta_category = 'Medium Beta'
            elif 'High Beta' in classification:
                beta_category = 'High Beta'
            elif 'Low Beta' in classification:
                beta_category = 'Low Beta'

            lines.append(f"Beta (Adjusted):                      {beta_val} ({beta_category})")
            lines.append(f"Classification:                       {classification}")
            lines.append(f"Interpretation:                       {beta_info.get('interpretation', 'N/A')}")
            lines.append("")

        lines.append("")
        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 9 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 9 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 9 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section9Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section9_output.txt")

    output_file = f"section9_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 9 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section9_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
