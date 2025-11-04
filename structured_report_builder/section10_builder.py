"""
SECTION 10: TECHNICAL ANALYSIS Builder
Dynamically builds technical analysis using API data
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
    print("[WARNING] MongoDB handler not available. Technical trend history will not be fetched.")
    MONGODB_AVAILABLE = False

class Section10Builder:
    def __init__(self, stock_id, exchange=0, use_mongodb=True):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.price_api_url = "https://frapi.marketsmojo.com/apiv1/price/priceupdates"
        self.summary_api_url = "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary"
        self.recommendation_api_url = "https://frapi.marketsmojo.com/apiv1/recommendation/getRecoData"

        self.price_data = {}
        self.summary_data = {}
        self.recommendation_data = {}

        # MongoDB handler for technical trend history
        self.use_mongodb = use_mongodb and MONGODB_AVAILABLE
        self.mongo_handler = None
        if self.use_mongodb:
            try:
                self.mongo_handler = MongoDBHandler()
            except Exception as e:
                print(f"[WARNING] MongoDB connection failed: {e}")
                self.use_mongodb = False

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

    def fetch_summary_data(self):
        """Fetch summary data"""
        print(f"Fetching summary data...")

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

    def fetch_recommendation_data(self):
        """Fetch recommendation data"""
        print(f"Fetching recommendation data...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange,
                "fornews": 1
            }

            response = requests.post(self.recommendation_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            code = str(result.get('code'))
            if code == '200' and 'data' in result:
                self.recommendation_data = result['data']
                print(f"[OK] Recommendation API successful")
                return True
            else:
                print(f"[WARNING] Recommendation API returned code: {code}")
        except Exception as e:
            print(f"[WARNING] Recommendation API failed: {e}")

        return False

    def _extract_technical_trend(self):
        """Extract overall technical trend from recommendation API"""
        try:
            technicals = self.recommendation_data.get('technicals', {})
            tech_factors = technicals.get('technical_key_factors', {})

            # Parse header message: "TCS turned Bearish from Mildly Bearish on 10 Oct 2025 at INR 3028.4"
            header_msg = tech_factors.get('header_msg', '')
            current_trend = tech_factors.get('tech_text', 'N/A')

            trend_info = {
                'current_trend': current_trend.upper(),
                'trend_change_date': 'N/A',
                'trend_change_price': 'N/A',
                'previous_trend': 'N/A',
                'price_change_pct': 'N/A'
            }

            # Parse the header message
            # Format: "turned X from Y on DATE at INR PRICE"
            if 'turned' in header_msg and 'from' in header_msg:
                # Extract previous trend
                match = re.search(r'from\s+([^on]+)\s+on', header_msg)
                if match:
                    trend_info['previous_trend'] = match.group(1).strip()

                # Extract date
                match = re.search(r'on\s+([\d\s\w]+)\s+at', header_msg)
                if match:
                    date_str = match.group(1).strip()
                    # Convert "10 Oct 2025" to "10-Oct-2025"
                    try:
                        dt = datetime.strptime(date_str, '%d %b %Y')
                        trend_info['trend_change_date'] = dt.strftime('%d-%b-%Y')
                    except:
                        trend_info['trend_change_date'] = date_str

                # Extract price
                match = re.search(r'at\s+INR\s+([\d,.]+)', header_msg)
                if match:
                    price_str = match.group(1).strip()
                    trend_info['trend_change_price'] = price_str

                    # Calculate price change since trend change
                    # Get current price from summary
                    try:
                        current_price_str = self.summary_data.get('ticker', {}).get('price', '0')
                        current_price = float(current_price_str.replace(',', ''))
                        trend_price = float(price_str.replace(',', ''))

                        price_change = ((current_price - trend_price) / trend_price) * 100
                        trend_info['price_change_pct'] = f"{price_change:+.2f}%"
                    except:
                        trend_info['price_change_pct'] = 'N/A'

            return trend_info
        except Exception as e:
            print(f"[WARNING] Error extracting technical trend: {e}")
            return None

    def _extract_technical_indicators(self):
        """Extract technical indicator summary"""
        try:
            technicals = self.recommendation_data.get('technicals', {})
            tech_factors = technicals.get('technical_key_factors', {})
            details = tech_factors.get('details', [])

            indicators = []
            for item in details:
                indicator_name = item.get('text1', 'N/A')

                # Some indicators have weekly/monthly, some have only daily
                weekly = item.get('grade_w', item.get('grade', 'N/A'))
                monthly = item.get('grade_m', '')

                # "No Signal" and "No Trend" should be displayed as-is from API
                # (previously these were hidden, but website shows them)

                indicators.append({
                    'name': indicator_name,
                    'weekly': weekly,
                    'monthly': monthly
                })

            return indicators
        except Exception as e:
            print(f"[WARNING] Error extracting technical indicators: {e}")
            return []

    def _extract_technical_levels(self):
        """Extract key technical levels"""
        try:
            # Get 52-week high/low
            highlow = self.summary_data.get('52wk_highlow', {})
            wk52_high = highlow.get('52wk_high', 'N/A')
            wk52_low = highlow.get('52wk_low', 'N/A')

            # Get moving averages
            ma_data = self.price_data.get('MOVING_AVERAGES', [])

            # Use BSE data if available, else NSE
            ma_info = None
            for item in ma_data:
                if item.get('exch', '').upper() == 'BSE':
                    ma_info = item
                    break
            if not ma_info and len(ma_data) > 0:
                ma_info = ma_data[0]

            ma_values = {}
            if ma_info:
                for item in ma_info.get('data', []):
                    field = item.get('field', '')
                    value = item.get('value', 'N/A')
                    if 'Days' in field:
                        ma_values[field] = value

            levels = {
                'immediate_support': f"₹{wk52_low} (52W Low)" if wk52_low != 'N/A' else 'N/A',
                'immediate_resistance': f"₹{ma_values.get('20 Days', 'N/A')} (20 DMA area)" if '20 Days' in ma_values else 'N/A',
                'major_resistance': f"₹{ma_values.get('100 Days', 'N/A')} (100 DMA)" if '100 Days' in ma_values else 'N/A',
                'strong_resistance': f"₹{ma_values.get('200 Days', 'N/A')} (200 DMA)" if '200 Days' in ma_values else 'N/A',
                'wk52_high': f"₹{wk52_high} (Far resistance)" if wk52_high != 'N/A' else 'N/A'
            }

            return levels
        except Exception as e:
            print(f"[WARNING] Error extracting technical levels: {e}")
            return None

    def _get_technical_trend_history(self):
        """Get technical trend history from MongoDB"""
        if not self.use_mongodb or not self.mongo_handler:
            return None

        try:
            # Get trend history
            history = self.mongo_handler.get_technical_trend_history(int(self.stock_id), limit=5)
            return history
        except Exception as e:
            print(f"[WARNING] Error fetching technical trend history: {e}")
            return None

    def _extract_delivery_volumes(self):
        """Extract delivery volumes data"""
        try:
            delivery_data = self.price_data.get('DELIVERY_VOLUMES', {})

            # Extract header messages for 1-month and 1-day changes
            header_msgs = delivery_data.get('header_msg', {})

            month_change = 'N/A'
            day_change = 'N/A'

            # Parse 1-month change
            if '0' in header_msgs:
                msg = header_msgs['0'].get('msg', '')
                # Format: "1 Month: Delivery volume increased by 26.72%"
                match = re.search(r'by\s+([\d.]+)%', msg)
                if match:
                    pct = match.group(1)
                    direction = 'increased' if 'increased' in msg else 'decreased'
                    month_change = f"{pct}%"

            # Parse 1-day change
            if '1' in header_msgs:
                msg = header_msgs['1'].get('msg', '')
                # Format: "1 Day: Delivery volume increased by 18.89% over 5 day average"
                match = re.search(r'by\s+([\d.]+)%', msg)
                if match:
                    pct = match.group(1)
                    direction = 'increased' if 'increased' in msg else 'decreased'
                    day_change = f"{pct}% vs 5-day avg"

            # Extract table details
            table_details = delivery_data.get('table_details', [])
            volume_table = []
            for row in table_details:
                period = row.get('text', 'N/A')
                volume = row.get('delv_vol_avg', 'N/A')
                pct_total = row.get('delv_perc', 'N/A')

                volume_table.append({
                    'period': period,
                    'volume': volume,
                    'pct_total': pct_total
                })

            # Extract footer messages
            footer_msgs = delivery_data.get('footer_msg', [])
            trailing_period = footer_msgs[0] if len(footer_msgs) > 0 else 'N/A'
            previous_period = footer_msgs[1] if len(footer_msgs) > 1 else 'N/A'

            return {
                'month_change': month_change,
                'day_change': day_change,
                'volume_table': volume_table,
                'trailing_period': trailing_period,
                'previous_period': previous_period
            }
        except Exception as e:
            print(f"[WARNING] Error extracting delivery volumes: {e}")
            return None

    def build_section(self):
        """Build SECTION 10 from API data"""
        # Fetch all data first (if not already loaded)
        if not self.price_data:
            if not self.fetch_price_data():
                return "ERROR: Failed to fetch price data"

        if not self.summary_data:
            if not self.fetch_summary_data():
                return "ERROR: Failed to fetch summary data"

        if not self.recommendation_data:
            if not self.fetch_recommendation_data():
                return "ERROR: Failed to fetch recommendation data"

        # Extract all components
        trend_info = self._extract_technical_trend()
        indicators = self._extract_technical_indicators()
        levels = self._extract_technical_levels()
        delivery = self._extract_delivery_volumes()

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 10: TECHNICAL ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

        # OVERALL TECHNICAL TREND
        if trend_info:
            lines.append("OVERALL TECHNICAL TREND:")
            lines.append("-" * 24)
            lines.append(f"Current Trend:{''.ljust(32)}   {trend_info.get('current_trend', 'N/A')}")

            date_str = trend_info.get('trend_change_date', 'N/A')
            price_str = trend_info.get('trend_change_price', 'N/A')
            if price_str != 'N/A':
                price_str = f"₹{price_str}"
            lines.append(f"Trend Changed:{''.ljust(32)}   {date_str} at {price_str}")
            lines.append(f"Previous Trend:{''.ljust(31)}   {trend_info.get('previous_trend', 'N/A')}")
            lines.append("")

        # TECHNICAL INDICATOR SUMMARY
        if indicators and len(indicators) > 0:
            lines.append("TECHNICAL INDICATOR SUMMARY:")
            lines.append("-" * 28)
            lines.append(f"{'Indicator':<24}{'Weekly':<16}Monthly")
            lines.append("-" * 49)

            for ind in indicators:
                name = ind['name'] + ":"
                weekly = ind['weekly'] if ind['weekly'] else ''
                monthly = ind['monthly'] if ind['monthly'] else ''

                # Handle special cases where only one period is shown
                if not monthly and not weekly:
                    # Show "Daily X" in the weekly column
                    lines.append(f"{name:<24}{weekly:<16}{monthly}")
                elif not monthly:
                    # Show weekly reading
                    lines.append(f"{name:<24}{weekly:<16}{monthly}")
                elif not weekly:
                    # Show monthly reading in monthly column, leave weekly empty
                    lines.append(f"{name:<24}{'':<16}{monthly}")
                else:
                    # Show both
                    lines.append(f"{name:<24}{weekly:<16}{monthly}")

            lines.append("")

        # KEY TECHNICAL LEVELS
        if levels:
            lines.append("KEY TECHNICAL LEVELS:")
            lines.append("-" * 21)
            lines.append(f"Immediate Support:{''.ljust(24)}   {levels.get('immediate_support', 'N/A')}")
            lines.append(f"Immediate Resistance:{''.ljust(21)}   {levels.get('immediate_resistance', 'N/A')}")
            lines.append(f"Major Resistance:{''.ljust(25)}   {levels.get('major_resistance', 'N/A')}")
            lines.append(f"Strong Resistance:{''.ljust(24)}   {levels.get('strong_resistance', 'N/A')}")
            lines.append(f"52-Week High:{''.ljust(29)}   {levels.get('wk52_high', 'N/A')}")
            lines.append("")

        # TREND HISTORY
        lines.append("TREND HISTORY:")
        lines.append("-" * 14)

        # Get trend history from MongoDB
        trend_history = self._get_technical_trend_history()
        if trend_history and len(trend_history) > 0:
            for change in trend_history:
                date = change['formatted_date']
                trend_change = change['trend_change']
                previous_trend = change['previous_trend']
                lines.append(f"{date}: Changed to {trend_change} from {previous_trend}")
        else:
            lines.append("Data Not Available")

        lines.append("")

        # DELIVERY VOLUMES
        if delivery:
            lines.append("DELIVERY VOLUMES (Recent Trend):")
            lines.append("-" * 33)
            lines.append(f"1-Month Delivery Change:{''.ljust(18)}   {delivery.get('month_change', 'N/A')}")
            lines.append(f"1-Day Delivery Change:{''.ljust(20)}   {delivery.get('day_change', 'N/A')}")
            lines.append("")

            # Footer dates
            lines.append(delivery.get('trailing_period', ''))
            lines.append(delivery.get('previous_period', ''))
            lines.append("")

            # Delivery Volume Summary Table
            lines.append("Delivery Volume Summary:")
            lines.append("-" * 70)
            lines.append(f"{'Period':<26}{'Volume':<21}% of Total Volume   ")
            lines.append("-" * 70)

            for row in delivery.get('volume_table', []):
                period = row['period']
                volume = row['volume']
                pct = row['pct_total']
                lines.append(f"{period:<26}{volume:<21}{pct:<16}")

            lines.append("")

        lines.append("")
        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 10 saved to: {output_file}")
        return section_text

    def cleanup(self):
        """Clean up resources"""
        if self.mongo_handler:
            self.mongo_handler.close()


def main():
    """Test the Section 10 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 10 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section10Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section10_output.txt")

    output_file = f"section10_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 10 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section10_output.txt")
    print(f"  - {output_file}")

    # Cleanup MongoDB connection
    builder.cleanup()


if __name__ == "__main__":
    main()
