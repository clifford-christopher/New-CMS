"""
SECTION 12: FINANCIAL TREND ANALYSIS Builder
Dynamically builds financial trend analysis using API data
"""
import requests
import json
from datetime import datetime

# Try importing MongoDB handler
try:
    from mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    print("[WARNING] MongoDB handler not available. Financial trend history will not be fetched.")
    MONGODB_AVAILABLE = False

class Section12Builder:
    def __init__(self, stock_id, exchange=0, use_mongodb=True):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.recommendation_api_url = "https://frapi.marketsmojo.com/apiv1/recommendation/getRecoData"

        self.recommendation_data = {}

        # MongoDB handler for financial trend history
        self.use_mongodb = use_mongodb and MONGODB_AVAILABLE
        self.mongo_handler = None
        if self.use_mongodb:
            try:
                self.mongo_handler = MongoDBHandler()
            except Exception as e:
                print(f"[WARNING] MongoDB connection failed: {e}")
                self.use_mongodb = False

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

    def _format_quarter(self, quarter_num):
        """Convert quarter number like 202509 to Sep'25"""
        try:
            quarter_str = str(quarter_num)
            if len(quarter_str) == 6:
                year = quarter_str[:4]
                month = quarter_str[4:6]

                # Map month numbers to quarter names
                month_map = {
                    '03': 'Mar',
                    '06': 'Jun',
                    '09': 'Sep',
                    '12': 'Dec'
                }

                month_name = month_map.get(month, month)
                year_short = year[2:]  # Last 2 digits of year

                return f"{month_name}'{year_short}"
            return str(quarter_num)
        except:
            return str(quarter_num)

    def _extract_financial_trend(self):
        """Extract current financial trend information"""
        try:
            fin_trend_card = self.recommendation_data.get('financial_trend_card', {})
            dot = fin_trend_card.get('dot', {})
            fin_trend = fin_trend_card.get('fin_trend', {})

            # Extract current trend
            trend_text = dot.get('f_txt', 'N/A').upper()
            if trend_text == 'FLAT':
                trend_text = 'FLAT'
            elif 'POSITIVE' in trend_text.upper():
                trend_text = 'POSITIVE'
            elif 'NEGATIVE' in trend_text.upper():
                trend_text = 'NEGATIVE'

            # Extract quarter
            quarter = fin_trend_card.get('quarter', '')
            formatted_quarter = self._format_quarter(quarter)

            # Extract trend message
            trend_msg = fin_trend.get('scrmsg', '')

            return {
                'trend': trend_text,
                'quarter': formatted_quarter,
                'message': trend_msg
            }
        except Exception as e:
            print(f"[WARNING] Error extracting financial trend: {e}")
            return {
                'trend': 'N/A',
                'quarter': 'N/A',
                'message': ''
            }

    def _format_metric_name(self, metric):
        """Format metric names to match reference format"""
        # Mapping for common metrics
        metric_map = {
            'OPERATING CF(Y)': 'Operating Cash Flow (Annual)',
            'OPERATING CF(HY)': 'Operating Cash Flow (Half-Yearly)',
            'NET SALES(Q)': 'Net Sales (Quarterly)',
            'NET SALES(HY)': 'Net Sales (Half-Yearly)',
            'NET SALES(Y)': 'Net Sales (Annual)',
            'PBDIT(Q)': 'Pbdit (Quarterly)',
            'PBDIT(HY)': 'Pbdit (Half-Yearly)',
            'PBDIT(Y)': 'Pbdit (Annual)',
            'OPERATING PROFIT TO NET SALES(Q)': 'Operating Profit to Net Sales (Quarterly)',
            'PBT LESS OI(Q)': 'Pbt Less Oi (Quarterly)',
            'PBT LESS OI(HY)': 'Pbt Less Oi (Half-Yearly)',
            'PAT(Q)': 'PAT (Quarterly)',
            'PAT(HY)': 'PAT (Half-Yearly)',
            'PAT(Y)': 'PAT (Annual)',
            'DEBTORS TURNOVER RATIO(HY)': 'DEBTORS TURNOVER RATIO(HY)',
            'DEBTORS TURNOVER RATIO(Y)': 'DEBTORS TURNOVER RATIO(Y)',
            'CURRENT RATIO(Q)': 'Current Ratio (Quarterly)',
            'CURRENT RATIO(HY)': 'Current Ratio (Half-Yearly)',
        }

        # Return mapped name or original if not in map
        return metric_map.get(metric, metric)

    def _format_value(self, value_str):
        """Format value strings to match reference format"""
        try:
            # Replace Rs with ₹ symbol
            value_str = value_str.replace('Rs ', '₹')
            value_str = value_str.replace('Rs. ', '₹')

            # Standardize Cr/Crores
            value_str = value_str.replace(' Cr', ' Crores')
            value_str = value_str.replace(' cr', ' Crores')
            value_str = value_str.replace(' cr.', ' Crores')
            value_str = value_str.replace(' Cr.', ' Crores')

            return value_str
        except:
            return value_str

    def _extract_positive_factors(self):
        """Extract key positive factors"""
        try:
            fin_trend_card = self.recommendation_data.get('financial_trend_card', {})
            fin_trend = fin_trend_card.get('fin_trend', {})
            pos = fin_trend.get('pos', {})

            factors = []
            for msg in pos.get('msg', []):
                metric = msg.get('txt1', '')
                value = msg.get('txt2', '')

                # Format metric name
                formatted_metric = self._format_metric_name(metric)

                # Format value
                formatted_value = self._format_value(value)

                factors.append({
                    'metric': formatted_metric,
                    'value': formatted_value
                })

            return factors
        except Exception as e:
            print(f"[WARNING] Error extracting positive factors: {e}")
            return []

    def _extract_negative_factors(self):
        """Extract key negative factors"""
        try:
            fin_trend_card = self.recommendation_data.get('financial_trend_card', {})
            fin_trend = fin_trend_card.get('fin_trend', {})
            neg = fin_trend.get('neg', {})

            factors = []
            for msg in neg.get('msg', []):
                metric = msg.get('txt1', '')
                value = msg.get('txt2', '')

                # Format metric name
                formatted_metric = self._format_metric_name(metric)

                # Format value
                formatted_value = self._format_value(value)

                factors.append({
                    'metric': formatted_metric,
                    'value': formatted_value
                })

            return factors
        except Exception as e:
            print(f"[WARNING] Error extracting negative factors: {e}")
            return []

    def _build_trend_history(self):
        """Build trend history from MongoDB"""
        if not self.use_mongodb or not self.mongo_handler:
            return None

        try:
            # Get financial trend history
            history = self.mongo_handler.get_financial_trend_history(int(self.stock_id), limit=5)
            return history
        except Exception as e:
            print(f"[WARNING] Error fetching financial trend history: {e}")
            return None

    def build_section(self):
        """Build SECTION 12 from API data"""
        # Fetch data if not already loaded
        if not self.recommendation_data:
            if not self.fetch_recommendation_data():
                return "ERROR: Failed to fetch recommendation data"

        # Extract components
        trend_info = self._extract_financial_trend()
        positive_factors = self._extract_positive_factors()
        negative_factors = self._extract_negative_factors()
        trend_history = self._build_trend_history()

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 12: FINANCIAL TREND ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        lines.append("")
        lines.append("")

        # SHORT-TERM FINANCIAL TREND
        lines.append("SHORT-TERM FINANCIAL TREND:")
        lines.append("-" * 27)

        quarter = trend_info.get('quarter', 'N/A')
        trend = trend_info.get('trend', 'N/A')
        lines.append(f"Current Trend ({quarter}):{''.ljust(39 - len(quarter))}{trend}")
        lines.append("")

        # KEY POSITIVE FACTORS
        if positive_factors and len(positive_factors) > 0:
            lines.append("KEY POSITIVE FACTORS:")
            lines.append("-" * 21)

            for factor in positive_factors:
                metric = factor.get('metric', '')
                value = factor.get('value', '')

                # Calculate spacing to align values
                # Max metric length is about 35 chars, align value at column 40
                metric_display = f"✓ {metric}:"
                spacing = max(1, 42 - len(metric_display))
                lines.append(f"{metric_display}{' ' * spacing}{value}")

            lines.append("")

        # KEY NEGATIVE FACTORS
        if negative_factors and len(negative_factors) > 0:
            lines.append("KEY NEGATIVE FACTORS:")
            lines.append("-" * 21)

            for factor in negative_factors:
                metric = factor.get('metric', '')
                value = factor.get('value', '')

                # Align similar to positive factors
                metric_display = f"✗ {metric}"
                # Don't add colon after metric for negative factors to match reference
                spacing = max(1, 42 - len(metric_display))
                lines.append(f"{metric_display}{' ' * spacing}{value}")

            lines.append("")
        elif not positive_factors:
            # If no positive factors either, show a message
            lines.append("KEY NEGATIVE FACTORS:")
            lines.append("-" * 21)
            lines.append("✗ No significant negative factors")
            lines.append("")

        # TREND HISTORY
        lines.append("TREND HISTORY:")
        lines.append("-" * 14)

        if trend_history and len(trend_history) > 0:
            # Display header for table format (without Price column)
            lines.append(f"{'Quarter':<12}{'Trend':<15}{'Date':<12}Previous Trend")
            lines.append("-" * 52)

            # Display financial trend history from MongoDB in table format
            for change in trend_history:
                quarter_raw = change.get('quarter', 'N/A')
                trend = change.get('trend', 'N/A')
                date = change.get('formatted_date', 'N/A')
                previous = change.get('previous_trend', 'N/A')

                # Format quarter from Q3 FY25 to Jun'25 format
                if quarter_raw and quarter_raw != 'N/A':
                    # Convert Q3 FY26 to Sep'25 format
                    try:
                        parts = quarter_raw.split()
                        if len(parts) == 2:
                            q_part = parts[0]  # Q3
                            fy_part = parts[1]  # FY26

                            # Map quarters to months
                            q_to_month = {
                                'Q1': 'Jun',
                                'Q2': 'Sep',
                                'Q3': 'Dec',
                                'Q4': 'Mar'
                            }

                            month = q_to_month.get(q_part, q_part)

                            # Extract year from FY26 -> '25
                            if fy_part.startswith('FY'):
                                year = fy_part[2:]  # Gets 26 from FY26
                                # Convert to previous year for proper format
                                year_int = int('20' + year) - 1
                                year_str = str(year_int)[-2:]
                                quarter_formatted = f"{month}'{year_str}"
                            else:
                                quarter_formatted = quarter_raw
                        else:
                            quarter_formatted = quarter_raw
                    except:
                        quarter_formatted = quarter_raw
                else:
                    quarter_formatted = quarter_raw

                # Format previous trend with quarter if available
                previous_formatted = previous

                # Format as table row (without price column)
                lines.append(f"{quarter_formatted:<12}{trend:<15}{date:<12}{previous_formatted}")
        else:
            # Show as not available if no MongoDB data
            lines.append("Data Not Available")

        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 12 saved to: {output_file}")
        return section_text

    def cleanup(self):
        """Clean up resources"""
        if self.mongo_handler:
            self.mongo_handler.close()


def main():
    """Test the Section 12 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 12 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section12Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section12_output.txt")

    output_file = f"section12_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 12 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section12_output.txt")
    print(f"  - {output_file}")

    # Cleanup MongoDB connection
    builder.cleanup()


if __name__ == "__main__":
    main()