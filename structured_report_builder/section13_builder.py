"""
SECTION 13: PROPRIETARY SCORE & ADVISORY Builder
Dynamically builds proprietary score and advisory using API data
"""
import requests
import json
from datetime import datetime

# Try importing MongoDB handler
try:
    from mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    print("[WARNING] MongoDB handler not available. Score history will be limited.")
    MONGODB_AVAILABLE = False

class Section13Builder:
    def __init__(self, stock_id, exchange=0, use_mongodb=True):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.recommendation_api_url = "https://frapi.marketsmojo.com/apiv1/recommendation/getRecoData"
        self.summary_api_url = "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary"

        self.recommendation_data = {}
        self.summary_data = {}

        # MongoDB handler for score history
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

    def _get_score_category(self, score):
        """Get score category based on score value"""
        try:
            score_val = int(score)
            if score_val >= 70:
                return "BUY", f"BUY (Score 70-100)"
            elif score_val >= 50:
                return "HOLD", f"HOLD (Score 50-70)"
            elif score_val >= 30:
                return "SELL", f"SELL (Score 30-50)"
            else:
                return "STRONG SELL", f"STRONG SELL (Score 0-30)"
        except:
            return "N/A", "N/A"

    def _get_recommendation_text(self, rating):
        """Get recommendation text based on rating"""
        rating_upper = rating.upper() if rating else ""

        if "BUY" in rating_upper:
            if "STRONG" in rating_upper:
                return ["Strongly recommended for fresh buy", "Excellent opportunity"]
            else:
                return ["Recommended for fresh buy", "Good investment opportunity"]
        elif "HOLD" in rating_upper:
            return ["Not recommended for fresh buy", "You can continue to hold"]
        elif "SELL" in rating_upper:
            if "STRONG" in rating_upper:
                return ["Strongly consider selling", "Exit recommended"]
            else:
                return ["Consider selling", "Look for exit opportunities"]
        else:
            return ["Review investment decision", "Monitor closely"]

    def _extract_current_advisory(self):
        """Extract current advisory information"""
        try:
            score_data = self.recommendation_data.get('score', {})

            # Get current score and rating
            current_score = score_data.get('score', 'N/A')
            score_text = score_data.get('scoreText', 'N/A')

            # Get category
            rating, category = self._get_score_category(current_score)

            # Get recommendation text
            recommendation = self._get_recommendation_text(score_text)

            # Get previous category info
            prev_from = score_data.get('from', '')
            prev_to = score_data.get('to', '')
            change_date = score_data.get('ch_date', '')
            change_price = score_data.get('ch_price', '')

            # Format change date
            if change_date:
                try:
                    # Convert "22nd Apr 2025" to "22-Apr-2025"
                    change_date = change_date.replace('st ', '-').replace('nd ', '-').replace('rd ', '-').replace('th ', '-')
                except:
                    pass

            # Get current price from summary main_header
            current_price = self.summary_data.get('main_header', {}).get('cmp', 'N/A')
            if current_price == 'N/A':
                # Fallback - try recommendation data main header
                current_price = self.recommendation_data.get('main_header', {}).get('cmp', 'N/A')

            # Clean up price format (remove commas)
            if current_price != 'N/A':
                current_price = current_price.replace(',', '')

            # Clean up change price format
            if change_price:
                change_price = change_price.replace(',', '')

            # Get previous category (just the name, no score range)
            if prev_from:
                prev_category = prev_from.upper()
            else:
                prev_category = 'N/A'

            return {
                'score': current_score,
                'rating': score_text.upper() if score_text else 'N/A',
                'category': category,
                'recommendation': recommendation,
                'prev_category': prev_category,
                'change_date': change_date,
                'change_price': change_price,
                'current_price': current_price
            }
        except Exception as e:
            print(f"[WARNING] Error extracting advisory: {e}")
            return None

    def _build_score_history(self):
        """Build score history table"""
        try:
            # Try MongoDB first for comprehensive history
            if self.use_mongodb and self.mongo_handler:
                try:
                    history = self.mongo_handler.get_score_history(int(self.stock_id), limit=5)
                    if history and len(history) > 0:
                        return history
                except Exception as e:
                    print(f"[WARNING] MongoDB score history failed: {e}")

            # Fallback to API data (limited history)
            score_data = self.recommendation_data.get('score', {})
            history = []

            # Add current score
            current_score = score_data.get('score', 'N/A')
            score_text = score_data.get('scoreText', 'N/A')

            history.append({
                'formatted_date': 'Current',
                'score': current_score,
                'rating': score_text,
                'change_from': '-'
            })

            # Add previous change if available
            change_date = score_data.get('ch_date', '')
            if change_date:
                prev_from = score_data.get('from', '')
                prev_to = score_data.get('to', '')

                # Format date
                formatted_date = change_date.replace('st ', '-').replace('nd ', '-').replace('rd ', '-').replace('th ', '-')

                history.append({
                    'formatted_date': formatted_date,
                    'score': current_score,  # Same score as it changed to this
                    'rating': prev_to,
                    'change_from': f"{prev_from}→{prev_to}" if prev_from and prev_to else '-'
                })

            return history
        except Exception as e:
            print(f"[WARNING] Error building score history: {e}")
            return []

    def _extract_key_strengths(self):
        """Extract key strengths from dashboard data"""
        try:
            strengths = []
            dashboard = self.recommendation_data.get('dashboard', [])

            # Extract strengths from dashboard
            for item in dashboard:
                if isinstance(item, dict):
                    main_text = item.get('text', '')
                    sub_texts = item.get('sub_text', [])

                    # Check for positive indicators in main text
                    positive_keywords = ['Strong', 'Healthy', 'High', 'Good', 'Excellent', 'Attractive', 'Low Debt']
                    if any(keyword in main_text for keyword in positive_keywords):
                        strengths.append(main_text)

                    # Add relevant sub-texts
                    for sub in sub_texts:
                        if any(keyword in sub for keyword in positive_keywords):
                            strengths.append(sub)

            # Add valuation strengths if attractive
            valuation_data = self.recommendation_data.get('valuation', {})
            valuation_score = valuation_data.get('valuation_score', {})
            if valuation_score.get('v_txt', '').lower() == 'attractive':
                strengths.append("Attractive valuation at current price")

            # Add dividend yield if high
            valuation_tbl = valuation_data.get('valuation_tbl', {})
            for item in valuation_tbl.get('list', []):
                if item.get('name') == 'Dividend Yield':
                    div_yield = item.get('value', '')
                    if div_yield:
                        try:
                            yield_val = float(div_yield.replace('%', ''))
                            if yield_val > 3:
                                strengths.append(f"High Dividend Yield: {div_yield}")
                        except:
                            pass

            # Add institutional holdings from quality data (only if not already in strengths)
            if not any('Institutional Holdings' in s for s in strengths):
                quality_data = self.recommendation_data.get('quality', {})
                quality_tbl = quality_data.get('quality_tbl', {})
                for item in quality_tbl.get('list', []):
                    if item.get('name') == 'Institutional Holding':
                        inst_holding = item.get('value', '')
                        if inst_holding:
                            try:
                                holding_val = float(inst_holding.replace('%', ''))
                                if holding_val > 20:
                                    strengths.append(f"High Institutional Holdings: {inst_holding}")
                            except:
                                pass

            return strengths[:7]  # Limit to 7 key strengths
        except Exception as e:
            print(f"[WARNING] Error extracting strengths: {e}")
            return []

    def _extract_key_concerns(self):
        """Extract key concerns from data"""
        try:
            concerns = []

            # Check PEG ratio
            valuation_data = self.recommendation_data.get('valuation', {})
            valuation_tbl = valuation_data.get('valuation_tbl', {})
            for item in valuation_tbl.get('list', []):
                if item.get('name') == 'PEG Ratio':
                    peg = item.get('value', '')
                    if peg:
                        try:
                            peg_val = float(peg)
                            if peg_val > 2:
                                concerns.append(f"PEG Ratio: {peg} (high relative to growth)")
                        except:
                            pass

            # Check technical trend
            dot = self.recommendation_data.get('financial_trend_card', {}).get('dot', {})
            tech_txt = dot.get('tech_txt', '')
            if 'bearish' in tech_txt.lower():
                concerns.append("Stock in bearish technical trend")

            # Check financial trend
            f_txt = dot.get('f_txt', '')
            if 'flat' in f_txt.lower():
                concerns.append("Flat financial performance in recent quarter")
            elif 'negative' in f_txt.lower():
                concerns.append("Negative financial trend")

            # Check for negative factors in dashboard
            dashboard = self.recommendation_data.get('dashboard', [])
            for item in dashboard:
                if isinstance(item, dict):
                    main_text = item.get('text', '')

                    # Check for negative indicators
                    negative_keywords = ['Underperform', 'Weak', 'Poor', 'Flat results', 'Lowest', 'Declined']
                    if any(keyword in main_text for keyword in negative_keywords):
                        concerns.append(main_text)

            # Check for consistent underperformance
            if 'Consistent Underperformance' in str(dashboard):
                concerns.append("Consistent underperformance against benchmark")

            return concerns[:5]  # Limit to 5 key concerns
        except Exception as e:
            print(f"[WARNING] Error extracting concerns: {e}")
            return []

    def _build_mojo_analysis(self):
        """Build Mojo 4 dots analysis"""
        try:
            dot = self.recommendation_data.get('financial_trend_card', {}).get('dot', {})

            # Extract 4 dots
            quality = dot.get('q_txt', 'N/A')
            valuation = dot.get('v_txt', 'N/A')
            financial = dot.get('f_txt', 'N/A')
            technical = dot.get('tech_txt', 'N/A')

            # Format financial trend
            if financial.lower() == 'flat':
                financial = 'Flat'
            elif 'positive' in financial.lower():
                financial = 'Positive'
            elif 'negative' in financial.lower():
                financial = 'Negative'

            # Determine near term drivers status
            near_term = 'NEUTRAL'
            if 'positive' in financial.lower() and 'bullish' in technical.lower():
                near_term = 'POSITIVE'
            elif 'negative' in financial.lower() or 'bearish' in technical.lower():
                if 'negative' in financial.lower() and 'bearish' in technical.lower():
                    near_term = 'NEGATIVE'
                else:
                    near_term = 'MIXED'

            return {
                'quality': quality,
                'valuation': valuation,
                'financial': financial,
                'technical': technical,
                'near_term': near_term
            }
        except Exception as e:
            print(f"[WARNING] Error building Mojo analysis: {e}")
            return None

    def build_section(self):
        """Build SECTION 13 from API data"""
        # Fetch data if not already loaded
        if not self.recommendation_data:
            if not self.fetch_recommendation_data():
                return "ERROR: Failed to fetch recommendation data"

        if not self.summary_data:
            self.fetch_summary_data()  # Optional, for current price

        # Extract components
        advisory = self._extract_current_advisory()
        history = self._build_score_history()
        strengths = self._extract_key_strengths()
        concerns = self._extract_key_concerns()
        mojo = self._build_mojo_analysis()

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 13: PROPRIETARY SCORE & ADVISORY")
        lines.append("=" * 80)
        lines.append("")
        lines.append("")

        # Get current date
        current_date = datetime.now().strftime("%d-%b-%Y")

        # CURRENT ADVISORY
        if advisory:
            lines.append(f"CURRENT ADVISORY (as of {current_date}):")
            lines.append("-" * 38)
            lines.append(f"Overall Score:{''.ljust(32)}{advisory.get('score', 'N/A')} / 100")
            lines.append(f"Advisory Rating:{''.ljust(30)}{advisory.get('rating', 'N/A')}")

            # Recommendation text
            rec_texts = advisory.get('recommendation', ['N/A', 'N/A'])
            lines.append(f"Recommendation:{''.ljust(31)}{rec_texts[0]}")
            if len(rec_texts) > 1:
                lines.append(f"{''.ljust(46)}{rec_texts[1]}")

            lines.append("")
            lines.append(f"Score Category:{''.ljust(31)}{advisory.get('category', 'N/A')}")

            # Previous category
            prev_cat = advisory.get('prev_category', 'N/A')
            change_date = advisory.get('change_date', '')
            change_price = advisory.get('change_price', '')
            if change_date and change_price:
                lines.append(f"Previous Category:{''.ljust(28)}{prev_cat} on {change_date} at ₹{change_price}")
            else:
                lines.append(f"Previous Category:{''.ljust(28)}{prev_cat}")

            lines.append("")

        # SCORE HISTORY
        if history and len(history) > 0:
            lines.append("SCORE HISTORY:")
            lines.append("-" * 14)
            lines.append(f"{'Date':<16}{'Score':<8}{'Rating':<16}Change From")
            lines.append("-" * 56)

            for entry in history[:5]:  # Limit to 5 entries as requested
                date = entry.get('formatted_date', entry.get('date', 'N/A'))
                score = entry.get('score', 'N/A')
                rating = entry.get('rating', 'N/A')
                change = entry.get('change_from', entry.get('change', '-'))

                lines.append(f"{date:<16}{score:<8}{rating:<16}{change}")

            lines.append("")

        # KEY STRENGTHS
        if strengths and len(strengths) > 0:
            lines.append("KEY STRENGTHS (Supporting the Score):")
            lines.append("-" * 38)

            for strength in strengths:
                # Clean up the text
                strength_text = strength.strip()
                if strength_text:
                    lines.append(f"✓ {strength_text}")

            lines.append("")

        # KEY CONCERNS
        if concerns and len(concerns) > 0:
            lines.append("KEY CONCERNS (Limiting the Score):")
            lines.append("-" * 35)

            for concern in concerns:
                concern_text = concern.strip()
                if concern_text:
                    lines.append(f"✗ {concern_text}")

            lines.append("")
        elif not strengths:
            lines.append("KEY CONCERNS (Limiting the Score):")
            lines.append("-" * 35)
            lines.append("✗ No significant concerns identified")
            lines.append("")

        # MOJO 4 DOTS ANALYSIS
        if mojo:
            lines.append("MOJO 4 DOTS ANALYSIS:")
            lines.append("-" * 21)

            # Near term drivers
            lines.append(f"1. NEAR TERM DRIVERS:{''.ljust(25)}{mojo.get('near_term', 'N/A')}")

            financial = mojo.get('financial', 'N/A')
            technical = mojo.get('technical', 'N/A')

            # Add checkmark or cross based on status
            fin_symbol = "✓" if "Positive" in financial else ("✗" if "Negative" in financial else "")
            tech_symbol = "✓" if "Bullish" in technical else "✗"

            lines.append(f"   - Quarterly Financial Trend:{''.ljust(7)}{financial} {fin_symbol}")
            lines.append(f"   - Technicals:{''.ljust(22)}{technical} {tech_symbol}")
            lines.append("")

            # Quality
            quality = mojo.get('quality', 'N/A')
            quality_symbol = "✓✓" if "Excellent" in quality else ("✓" if "Good" in quality else "")
            lines.append(f"2. QUALITY:{''.ljust(35)}{quality.upper()} {quality_symbol}")

            # Add quality description
            if "Excellent" in quality:
                lines.append("   - Excellent quality company")

                # Check if largest in sector
                dashboard = self.recommendation_data.get('dashboard', [])
                for item in dashboard:
                    if isinstance(item, dict):
                        text = item.get('text', '')
                        if 'Largest' in text or 'largest' in text:
                            lines.append("   - Largest company in sector")
                            break
            elif "Good" in quality:
                lines.append("   - Good quality fundamentals")

            lines.append("")

            # Valuation
            valuation = mojo.get('valuation', 'N/A')
            val_symbol = "✓" if "Attractive" in valuation else ""
            lines.append(f"3. VALUATION:{''.ljust(33)}{valuation.upper()} {val_symbol}")

            if "Attractive" in valuation:
                lines.append("   - At current price and performance")
                lines.append("   - Stock has attractive valuation")
            elif "Fair" in valuation:
                lines.append("   - Reasonably valued at current levels")
            elif "Expensive" in valuation:
                lines.append("   - Trading at premium valuation")

            lines.append("")

            # Overall Assessment
            lines.append(f"4. Overall Assessment:{''.ljust(24)}{'MIXED' if mojo.get('near_term') == 'MIXED' else 'POSITIVE' if mojo.get('near_term') == 'POSITIVE' else 'CAUTIOUS'}")

            # Add assessment description
            if "Excellent" in quality and "Attractive" in valuation:
                if "Bearish" in technical:
                    lines.append("   - Strong fundamentals but weak momentum")
                else:
                    lines.append("   - Strong fundamentals with good valuation")
            else:
                lines.append("   - Mixed signals across parameters")

            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 13 saved to: {output_file}")
        return section_text

    def cleanup(self):
        """Clean up resources"""
        if self.mongo_handler:
            self.mongo_handler.close()


def main():
    """Test the Section 13 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 13 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section13Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section13_output.txt")

    output_file = f"section13_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 13 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section13_output.txt")
    print(f"  - {output_file}")

    # Cleanup MongoDB connection
    builder.cleanup()


if __name__ == "__main__":
    main()