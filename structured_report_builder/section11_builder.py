"""
SECTION 11: QUALITY ASSESSMENT Builder
Dynamically builds quality assessment using API data
"""
import requests
import json
from datetime import datetime

# Try importing MongoDB handler
try:
    from mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    print("[WARNING] MongoDB handler not available. Quality history will not be fetched.")
    MONGODB_AVAILABLE = False

class Section11Builder:
    def __init__(self, stock_id, exchange=0, use_mongodb=True):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.recommendation_api_url = "https://frapi.marketsmojo.com/apiv1/recommendation/getRecoData"

        self.recommendation_data = {}

        # MongoDB handler for quality history
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

    def _extract_overall_quality(self):
        """Extract overall quality grade and status"""
        try:
            quality_data = self.recommendation_data.get('quality', {})
            quality_score = quality_data.get('quality_score', {})

            # Extract current quality
            current_quality = quality_score.get('q_txt', 'N/A').upper()

            # Extract quality messages
            quality_msgs = quality_score.get('q_msg', [])
            quality_status = quality_msgs[0] if quality_msgs else 'Quality assessment based on financial performance'

            # Extract quality factors
            q_factors = quality_score.get('q_factor', {})

            # Build quality info
            quality_info = {
                'current_quality': current_quality,
                'quality_status': quality_status,
                'management_risk': q_factors.get('managementrisk', {}).get('grade', 'N/A'),
                'growth': q_factors.get('growth', {}).get('grade', 'N/A'),
                'capital_structure': q_factors.get('capitalstructure', {}).get('grade', 'N/A'),
                'extra_message': quality_score.get('extra_message', ''),
                'quality_msgs': quality_msgs
            }

            return quality_info
        except Exception as e:
            print(f"[WARNING] Error extracting overall quality: {e}")
            return None

    def _extract_key_quality_factors(self):
        """Extract key quality factors and metrics"""
        try:
            quality_data = self.recommendation_data.get('quality', {})
            quality_tbl = quality_data.get('quality_tbl', {})
            factors_list = quality_tbl.get('list', [])

            # Map API field names to display names
            field_mapping = {
                'Sales Growth (5y)': '5-Year Sales Growth',
                'EBIT Growth (5y)': '5-Year EBIT Growth',
                'EBIT to Interest (avg)': 'Average EBIT to Interest',
                'Debt to EBITDA (avg)': 'Average Debt to EBITDA',
                'Net Debt to Equity (avg)': 'Average Net Debt to Equity',
                'Sales to Capital Employed (avg)': 'Average Sales to Capital Employed',
                'Tax Ratio': 'Tax Ratio',
                'Dividend Payout Ratio': 'Dividend Payout Ratio',
                'Pledged Shares': 'Pledge Shares',
                'Institutional Holding': 'Institutional Holdings',
                'ROCE (avg)': 'Average ROCE',
                'ROE (avg)': 'Average ROE'
            }

            factors = {}
            for item in factors_list:
                api_name = item.get('name', '')
                value = item.get('value', 'N/A')

                # Map to display name
                display_name = field_mapping.get(api_name, api_name)

                # Add qualitative descriptors based on values
                descriptor = ''
                if api_name == 'EBIT to Interest (avg)':
                    try:
                        val = float(str(value).replace('x', ''))
                        if val > 50:
                            descriptor = ' (Very Strong)'
                        elif val > 20:
                            descriptor = ' (Strong)'
                        elif val > 5:
                            descriptor = ' (Adequate)'
                        else:
                            descriptor = ' (Weak)'
                    except:
                        pass
                elif api_name == 'Debt to EBITDA (avg)':
                    try:
                        val = float(value)
                        if val < 0.5:
                            descriptor = ' (Negligible debt)'
                        elif val < 2:
                            descriptor = ' (Low debt)'
                        elif val < 4:
                            descriptor = ' (Moderate debt)'
                        else:
                            descriptor = ' (High debt)'
                    except:
                        pass
                elif api_name == 'Net Debt to Equity (avg)':
                    try:
                        val = float(value)
                        if val < 0:
                            descriptor = ' (Net Cash Company)'
                        elif val < 0.5:
                            descriptor = ' (Low leverage)'
                        elif val < 1:
                            descriptor = ' (Moderate leverage)'
                        else:
                            descriptor = ' (High leverage)'
                    except:
                        pass
                elif api_name == 'Pledged Shares':
                    try:
                        val = float(value)
                        if val == 0:
                            descriptor = ' (No pledging)'
                    except:
                        pass
                elif api_name == 'Institutional Holding':
                    try:
                        val = float(str(value).replace('%', ''))
                        if val > 20:
                            descriptor = ' (High)'
                        elif val > 10:
                            descriptor = ' (Moderate)'
                        else:
                            descriptor = ' (Low)'
                    except:
                        pass
                elif api_name == 'ROCE (avg)':
                    try:
                        val = float(str(value).replace('%', ''))
                        if val > 50:
                            descriptor = ' (Exceptional)'
                        elif val > 30:
                            descriptor = ' (Very Strong)'
                        elif val > 20:
                            descriptor = ' (Strong)'
                        elif val > 15:
                            descriptor = ' (Good)'
                        else:
                            descriptor = ' (Weak)'
                    except:
                        pass
                elif api_name == 'ROE (avg)':
                    try:
                        val = float(str(value).replace('%', ''))
                        if val > 30:
                            descriptor = ' (Very Strong)'
                        elif val > 20:
                            descriptor = ' (Strong)'
                        elif val > 15:
                            descriptor = ' (Good)'
                        else:
                            descriptor = ' (Weak)'
                    except:
                        pass

                # Format value with unit
                if api_name in ['EBIT to Interest (avg)', 'Sales to Capital Employed (avg)']:
                    # Add 'x' suffix if not present
                    if 'x' not in str(value):
                        value = f"{value}x"
                elif api_name == 'Pledged Shares':
                    # Format as percentage
                    value = f"{value}%"

                # Ensure value is a string before concatenation
                factors[display_name] = str(value) + descriptor

            return factors
        except Exception as e:
            print(f"[WARNING] Error extracting quality factors: {e}")
            return {}

    def _get_quality_grade_history(self):
        """Get quality grade history from MongoDB"""
        if not self.use_mongodb or not self.mongo_handler:
            return None

        try:
            # Get quality history
            history = self.mongo_handler.get_quality_grade_history(int(self.stock_id), limit=5)
            return history
        except Exception as e:
            print(f"[WARNING] Error fetching quality grade history: {e}")
            return None

    def _build_quality_indicators(self, factors):
        """Build quality indicators checklist based on factors"""
        indicators = []

        # Check for zero/minimal debt
        net_debt = factors.get('Average Net Debt to Equity', '')
        if 'Net Cash' in net_debt or '-' in net_debt:
            indicators.append("✓ Zero/Minimal Debt Company")

        # Check ROCE
        roce = factors.get('Average ROCE', '')
        try:
            roce_val = float(roce.split('%')[0])
            if roce_val > 50:
                indicators.append(f"✓ High and stable ROCE (>{int(roce_val)}%)")
            elif roce_val > 20:
                indicators.append(f"✓ Good ROCE ({int(roce_val)}%)")
        except:
            pass

        # Check ROE
        roe = factors.get('Average ROE', '')
        if 'Very Strong' in roe or 'Strong' in roe:
            indicators.append("✓ Strong return on equity")

        # Check interest coverage
        ebit_to_int = factors.get('Average EBIT to Interest', '')
        if 'Very Strong' in ebit_to_int or 'Strong' in ebit_to_int:
            indicators.append("✓ Strong interest coverage")

        # Check sales growth
        sales_growth = factors.get('5-Year Sales Growth', '')
        try:
            growth_val = float(sales_growth.replace('%', ''))
            if growth_val > 8:
                indicators.append(f"✓ Healthy long-term growth (Sales CAGR: {sales_growth})")
        except:
            pass

        # Check pledging
        pledge = factors.get('Pledge Shares', '')
        if 'No pledging' in pledge or pledge == '0.00%':
            indicators.append("✓ No promoter pledging")

        # Check institutional holding
        inst_holding = factors.get('Institutional Holdings', '')
        if 'High' in inst_holding:
            indicators.append("✓ Healthy institutional participation")

        # Check dividend payout
        div_payout = factors.get('Dividend Payout Ratio', '')
        try:
            div_val = float(div_payout.replace('%', ''))
            if div_val > 30:
                indicators.append("✓ Consistent dividend payer")
        except:
            pass

        # Add market position if mentioned in quality messages
        quality_msgs = self._extract_overall_quality()
        if quality_msgs:
            msgs = quality_msgs.get('quality_msgs', [])
            for msg in msgs:
                if 'Largest' in msg or 'largest' in msg:
                    indicators.append("✓ Market leader in sector")
                    break

        # Check debt to EBITDA
        debt_ebitda = factors.get('Average Debt to EBITDA', '')
        if 'Negligible' in debt_ebitda or 'Low debt' in debt_ebitda:
            indicators.append("✓ Strong balance sheet")

        # Add consistent profitability (assumed if ROCE and ROE are strong)
        if len(indicators) > 5:
            indicators.insert(1, "✓ Consistent profitability")

        return indicators

    def build_section(self):
        """Build SECTION 11 from API data"""
        # Fetch data if not already loaded
        if not self.recommendation_data:
            if not self.fetch_recommendation_data():
                return "ERROR: Failed to fetch recommendation data"

        # Extract components
        quality_info = self._extract_overall_quality()
        factors = self._extract_key_quality_factors()
        indicators = self._build_quality_indicators(factors)

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 11: QUALITY ASSESSMENT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("")

        # OVERALL QUALITY GRADE
        if quality_info:
            lines.append("OVERALL QUALITY GRADE:")
            lines.append("-" * 22)
            lines.append(f"Current Quality:{''.ljust(30)}{quality_info.get('current_quality', 'N/A')}")
            lines.append(f"Quality Status:{''.ljust(31)}{quality_info.get('quality_status', 'N/A')}")

            # Add extra message if available
            extra_msg = quality_info.get('extra_message', '')
            if extra_msg:
                lines.append(f"{''.ljust(46)}({extra_msg})")

            lines.append("")

            # Quality History from MongoDB (show max 3 records as periods)
            lines.append("Quality History:")
            quality_history = self._get_quality_grade_history()

            # Get current quality grade - try MongoDB first, then API
            current_quality_grade = None
            if self.mongo_handler:
                try:
                    current_quality_grade = self.mongo_handler.get_current_quality_grade(int(self.stock_id))
                except:
                    pass

            # Fallback to API if MongoDB doesn't have it
            if not current_quality_grade:
                current_quality_grade = quality_info.get('current_quality', 'N/A')

            if quality_history and len(quality_history) > 0:
                from datetime import datetime, timedelta

                # Check if the grade has been stable for a long time
                first_change = quality_history[0]
                try:
                    # Parse the date string from the history
                    change_date_str = first_change.get('date', '')
                    if change_date_str:
                        change_date = datetime.strptime(change_date_str, '%Y-%m-%d')
                        months_since_change = (datetime.now() - change_date).days / 30

                        # If stable for more than 3 months, show recent period instead of actual change date
                        if months_since_change > 3:
                            # Show last 3 months as current period
                            recent_date = datetime.now() - timedelta(days=90)
                            recent_month_year = recent_date.strftime('%b-%Y')

                            # Use the grade from history (what it changed TO, not the current from API)
                            stable_grade = first_change.get('grade_change', current_quality_grade)
                            previous_grade = first_change.get('previous_grade')

                            lines.append(f"- {recent_month_year} to Current:{''.ljust(18)}{stable_grade}")

                            # Only show previous grade if it's different from current
                            if previous_grade and previous_grade != stable_grade:
                                change_month_year = change_date.strftime('%b-%Y')
                                lines.append(f"- Prior to {change_month_year}:{''.ljust(18)}{previous_grade}")

                                # Add third line only if we have more history AND it's different
                                if len(quality_history) > 1:
                                    second_change = quality_history[1]
                                    second_grade = second_change.get('grade_change')
                                    second_prev = second_change.get('previous_grade')
                                    # Only show if second_prev is different from both previous_grade and stable_grade
                                    if second_prev and second_prev != previous_grade and second_prev != stable_grade:
                                        lines.append(f"- Prior:{''.ljust(38)}{second_prev} (long-term)")
                        else:
                            # Recent change, show actual dates
                            lines.append(f"- {first_change['formatted_date']} to Current:{''.ljust(18)}{first_change['grade_change']}")
                            if first_change.get('previous_grade'):
                                lines.append(f"- Prior to {first_change['formatted_date']}:{''.ljust(18)}{first_change['previous_grade']}")
                except Exception as e:
                    # Fallback to simple display
                    lines.append(f"- Current:{''.ljust(36)}{current_quality_grade}")
                    lines.append(f"- Previous periods:{''.ljust(27)}Data not available")
            else:
                # Fallback to sub-factors if MongoDB not available
                lines.append(f"- Management Risk:{''.ljust(28)}{quality_info.get('management_risk', 'N/A')}")
                lines.append(f"- Growth:{''.ljust(37)}{quality_info.get('growth', 'N/A')}")
                lines.append(f"- Capital Structure:{''.ljust(26)}{quality_info.get('capital_structure', 'N/A')}")
            lines.append("")

        # KEY QUALITY FACTORS
        if factors:
            lines.append("KEY QUALITY FACTORS:")
            lines.append("-" * 20)

            # Define order for display
            factor_order = [
                '5-Year Sales Growth',
                '5-Year EBIT Growth',
                'Average EBIT to Interest',
                'Average Debt to EBITDA',
                'Average Net Debt to Equity',
                'Average Sales to Capital Employed',
                'Tax Ratio',
                'Dividend Payout Ratio',
                'Pledge Shares',
                'Institutional Holdings',
                'Average ROCE',
                'Average ROE'
            ]

            for factor_name in factor_order:
                if factor_name in factors:
                    value = factors[factor_name]
                    lines.append(f"{factor_name}:{''.ljust(38 - len(factor_name))}{value}")

            lines.append("")

        # QUALITY INDICATORS
        if indicators and len(indicators) > 0:
            lines.append("QUALITY INDICATORS:")
            lines.append("-" * 19)
            for indicator in indicators:
                lines.append(indicator)
            lines.append("")

        lines.append("")
        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 11 saved to: {output_file}")
        return section_text

    def cleanup(self):
        """Clean up resources"""
        if self.mongo_handler:
            self.mongo_handler.close()


def main():
    """Test the Section 11 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 11 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section11Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section11_output.txt")

    output_file = f"section11_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 11 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section11_output.txt")
    print(f"  - {output_file}")

    # Cleanup MongoDB connection
    builder.cleanup()


if __name__ == "__main__":
    main()