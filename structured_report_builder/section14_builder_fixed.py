"""
SECTION 14: PEER COMPARISON Builder
Dynamically builds peer comparison using comparePeer API data directly
"""
import requests
import json
from datetime import datetime

class Section14Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.peer_api_url = "https://frapi.marketsmojo.com/apiv1/price/comparePeer"
        self.summary_api_url = "https://frapi.marketsmojo.com/apiv1/stocksummary/getStockSummary"
        self.peer_data = {}
        self.summary_data = {}

    def fetch_peer_data(self):
        """Fetch peer comparison data"""
        print(f"Fetching peer comparison data for stock {self.stock_id}...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange
            }

            response = requests.post(self.peer_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            code = str(result.get('code'))
            if code == '200' and 'data' in result:
                self.peer_data = result['data']
                print(f"[OK] Peer comparison API successful")
                return True
            else:
                print(f"[WARNING] Peer comparison API returned code: {code}")
        except Exception as e:
            print(f"[WARNING] Peer comparison API failed: {e}")

        return False

    def fetch_summary_data(self):
        """Fetch stock summary data to get industry"""
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
                return True
        except Exception as e:
            print(f"[WARNING] Summary API failed: {e}")
            self.summary_data = {}

        return False

    def _get_industry_name(self):
        """Extract industry name from summary data"""
        try:
            main_header = self.summary_data.get('main_header', {})
            return main_header.get('ind_name', '')
        except:
            return ''

    def _extract_metrics_from_lists(self):
        """Extract metrics for all stocks from comparePeer API lists"""
        if not self.peer_data or 'list' not in self.peer_data:
            return []

        list_data = self.peer_data['list']

        # Get main header for the requested stock
        main_header = list_data.get('main_header', {})

        # Extract data from various lists
        valuation_list = list_data.get('valuation', [])
        quality_list = list_data.get('quality', [])
        return_list = list_data.get('return_r', [])

        # Build metrics dictionary for each stock
        metrics_dict = {}

        # Process valuation list (has PE, PB, PEG)
        for item in valuation_list:
            sid = item.get('sid')
            if sid:
                if sid not in metrics_dict:
                    metrics_dict[sid] = {
                        'sid': sid,
                        'name': item.get('sname', 'N/A'),
                        'mcap': item.get('mcap', 'N/A'),
                        'url': item.get('url', '')
                    }
                metrics_dict[sid]['pe_ttm'] = item.get('pe', 'N/A')
                metrics_dict[sid]['peg'] = item.get('peg', 'N/A')

        # Process quality list (has ROE, quality score)
        for item in quality_list:
            sid = item.get('sid')
            if sid and sid in metrics_dict:
                metrics_dict[sid]['quality'] = item.get('quality', 'N/A')
                metrics_dict[sid]['quality_score'] = item.get('score', 'N/A')
                # ROE might be in quality text or score
                quality_text = item.get('quality_txt', '')
                if 'ROE' in quality_text:
                    # Try to extract ROE value from text
                    import re
                    roe_match = re.search(r'ROE[:\s]+(\d+\.?\d*)%?', quality_text)
                    if roe_match:
                        metrics_dict[sid]['roe'] = roe_match.group(1) + '%'

        # Process return list (has returns and dividend yield)
        for item in return_list:
            sid = item.get('sid')
            if sid and sid in metrics_dict:
                # Extract dividend yield if available
                div_yield = item.get('div_yield', item.get('dividend_yield', 'N/A'))
                metrics_dict[sid]['div_yield'] = div_yield

                # Store returns
                metrics_dict[sid]['return_1y'] = item.get('return_1y', 'N/A')

        # Now we need to fetch additional metrics from recommendation API
        # But first, let's check if we can get P/B and debt ratios from existing data

        # Convert to list and ensure main stock is first
        metrics_list = []
        main_sid = int(self.stock_id)

        # Add main stock first if it exists
        if main_sid in metrics_dict:
            main_metrics = metrics_dict[main_sid]
            main_metrics['is_main'] = True
            metrics_list.append(main_metrics)

        # Add peers (top 5 only)
        peer_count = 0
        for sid, metrics in metrics_dict.items():
            if sid != main_sid and peer_count < 5:
                metrics['is_main'] = False
                metrics_list.append(metrics)
                peer_count += 1

        return metrics_list

    def _fetch_additional_metrics(self, metrics_list):
        """Fetch P/B, ROE, Debt ratios from recommendation API for each stock"""
        recommendation_api_url = "https://frapi.marketsmojo.com/apiv1/recommendation/getRecoData"

        for metrics in metrics_list:
            sid = metrics['sid']
            name = metrics['name']

            print(f"Fetching detailed metrics for {name} ({sid})...")

            try:
                payload = {
                    "sid": int(sid),
                    "exchange": self.exchange,
                    "fornews": 1
                }

                response = requests.post(recommendation_api_url, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()

                if result.get('code') == '200' and 'data' in result:
                    data = result['data']

                    # Extract P/B from valuation
                    valuation = data.get('valuation', {})
                    valuation_tbl = valuation.get('valuation_tbl', {})
                    val_list = valuation_tbl.get('list', [])

                    for item in val_list:
                        item_name = item.get('name', '')
                        value = item.get('value', 'N/A')

                        if 'Price to Book' in item_name:
                            metrics['pb'] = value
                        elif 'Dividend Yield' in item_name and metrics.get('div_yield') == 'N/A':
                            metrics['div_yield'] = value
                        elif 'ROE (Latest)' in item_name or item_name == 'ROE':
                            metrics['roe'] = value

                    # Extract ROE and Debt from quality
                    quality = data.get('quality', {})
                    quality_tbl = quality.get('quality_tbl', {})
                    qual_list = quality_tbl.get('list', [])

                    for item in qual_list:
                        item_name = item.get('name', '')
                        value = item.get('value', 'N/A')

                        if 'ROE' in item_name or item_name == 'ROE (avg)':
                            metrics['roe'] = value
                        elif 'ROA' in item_name:  # For banks
                            metrics['roa'] = value
                            if metrics.get('roe') == 'N/A':  # Use ROA for banks if ROE not available
                                metrics['roe'] = value
                        elif 'Net Debt to Equity' in item_name:
                            metrics['debt_to_equity'] = value
                        elif 'Gross NPA' in item_name:  # For banks
                            metrics['gross_npa'] = value

            except Exception as e:
                print(f"[WARNING] Failed to fetch details for {name}: {e}")

            # Set defaults if not found
            if 'pb' not in metrics:
                metrics['pb'] = 'N/A'
            if 'roe' not in metrics:
                metrics['roe'] = 'N/A'
            if 'debt_to_equity' not in metrics:
                metrics['debt_to_equity'] = 'N/A'
            if 'div_yield' not in metrics:
                metrics['div_yield'] = 'N/A'

        return metrics_list

    def _safe_float(self, value, default=None):
        """Safely convert value to float, handling NA variations"""
        if value in ['N/A', 'NA', None, '']:
            return default

        try:
            # Handle string values
            if isinstance(value, str):
                # Check for NA variations (case-insensitive)
                upper_value = value.upper()
                if 'NA' in upper_value or 'N/A' in upper_value or 'LOSS' in upper_value:
                    return default
                # Remove formatting
                value = value.replace(',', '').replace('%', '').strip()

            return float(value)
        except (ValueError, TypeError):
            return default

    def _format_number(self, value, decimals=2):
        """Format number for display"""
        if value == 'N/A' or value is None or value == '':
            return 'N/A'

        # Use safe float conversion
        num = self._safe_float(value, default=None)

        if num is None:
            return 'N/A'

        # For regular numbers
        if decimals == 0:
            return str(int(num))
        else:
            return f"{num:.{decimals}f}"

    def _calculate_peer_averages(self, peers_list):
        """Calculate average metrics for peers (excluding main stock)"""
        totals = {'pe': 0, 'div_yield': 0, 'roe': 0, 'pb': 0}
        counts = {'pe': 0, 'div_yield': 0, 'roe': 0, 'pb': 0}

        for peer in peers_list:
            if peer.get('is_main'):
                continue  # Skip main stock

            # PE - use safe float conversion
            pe_val = self._safe_float(peer.get('pe_ttm'), default=None)
            if pe_val is not None:
                totals['pe'] += pe_val
                counts['pe'] += 1

            # Dividend Yield - use safe float conversion
            div_val = self._safe_float(peer.get('div_yield'), default=None)
            if div_val is not None:
                totals['div_yield'] += div_val
                counts['div_yield'] += 1

            # ROE - use safe float conversion
            roe_val = self._safe_float(peer.get('roe'), default=None)
            if roe_val is not None:
                totals['roe'] += roe_val
                counts['roe'] += 1

            # P/B - use safe float conversion
            pb_val = self._safe_float(peer.get('pb'), default=None)
            if pb_val is not None:
                totals['pb'] += pb_val
                counts['pb'] += 1

        averages = {}
        for key in totals:
            if counts[key] > 0:
                averages[key] = totals[key] / counts[key]
            else:
                averages[key] = None

        return averages

    def build_section(self):
        """Build SECTION 14 from API data"""
        # Fetch data if not already loaded
        if not self.peer_data:
            if not self.fetch_peer_data():
                return "ERROR: Failed to fetch peer comparison data"

        # Fetch summary data to get industry
        if not self.summary_data:
            self.fetch_summary_data()

        # Extract metrics from the comparePeer API response
        metrics_list = self._extract_metrics_from_lists()

        if not metrics_list:
            return "ERROR: No peer data available"

        # Fetch additional metrics (P/B, ROE, Debt) from recommendation API
        metrics_list = self._fetch_additional_metrics(metrics_list)

        # Get main stock (first in list)
        main_stock = None
        for item in metrics_list:
            if item.get('is_main'):
                main_stock = item
                break

        if not main_stock:
            return "ERROR: Main stock data not found"

        # Calculate averages
        averages = self._calculate_peer_averages(metrics_list)

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 14: PEER COMPARISON")
        lines.append("=" * 80)
        lines.append("")
        lines.append("")

        # Get industry name from summary data
        industry = self._get_industry_name()

        if industry:
            # Use the full industry name as provided by the API
            peer_group_label = f"PEER GROUP - {industry.upper()}"
        else:
            # Fallback if no industry data
            peer_group_label = "PEER GROUP COMPANIES"

        lines.append(f"{peer_group_label}:")
        lines.append("-" * len(f"{peer_group_label}:"))

        # Build comparison table
        lines.append("Company             PE(TTM)     Div Yield   Return on Equity  Debt to Equity  Price to Book")
        lines.append("-" * 95)

        for peer in metrics_list:
            # Format company name (max 20 chars)
            name = peer['name'][:18] if len(peer['name']) > 18 else peer['name']

            # Format PE
            pe = self._format_number(peer.get('pe_ttm', 'N/A'), 2)
            if pe != 'N/A':
                pe = pe.rjust(6)
            else:
                pe = 'N/A'.rjust(6)

            # Format Dividend Yield
            div_yield = peer.get('div_yield', 'N/A')
            if div_yield != 'N/A':
                if '%' not in str(div_yield):
                    div_yield = f"{div_yield}%"
                div_yield = div_yield.rjust(10)
            else:
                div_yield = 'N/A'.rjust(10)

            # Format ROE
            roe = peer.get('roe', 'N/A')
            if roe != 'N/A':
                if '%' not in str(roe):
                    roe = f"{roe}%"
                roe = roe.rjust(15)
            else:
                roe = 'N/A'.rjust(15)

            # Format Debt to Equity
            debt_eq = self._format_number(peer.get('debt_to_equity', 'N/A'), 2)
            debt_eq = debt_eq.rjust(15)

            # Format P/B
            pb = self._format_number(peer.get('pb', 'N/A'), 2)
            pb = pb.rjust(13)

            lines.append(f"{name:<20}{pe}      {div_yield}  {roe}  {debt_eq}  {pb}")

        lines.append("")

        # RELATIVE POSITIONING
        if main_stock and averages:
            lines.append("RELATIVE POSITIONING:")
            lines.append("-" * 21)
            lines.append(f"{main_stock['name']} vs Peers:")

            # ROE comparison - use safe float conversion
            main_roe = self._safe_float(main_stock.get('roe'), default=None)
            avg_roe = averages.get('roe')
            if main_roe is not None and avg_roe is not None:
                if main_roe > avg_roe:
                    lines.append(f"- Higher ROE ({main_roe:.1f}% vs peer avg ~{avg_roe:.0f}%)")
                else:
                    lines.append(f"- Lower ROE ({main_roe:.1f}% vs peer avg ~{avg_roe:.0f}%)")

            # P/BV comparison - use safe float conversion
            main_pb = self._safe_float(main_stock.get('pb'), default=None)
            avg_pb = averages.get('pb')
            if main_pb is not None and avg_pb is not None:
                if main_pb > avg_pb:
                    lines.append(f"- Higher P/BV ({main_pb:.2f}x vs peer avg ~{avg_pb:.1f}x)")
                else:
                    lines.append(f"- Lower P/BV ({main_pb:.2f}x vs peer avg ~{avg_pb:.1f}x)")

            # PE comparison - use safe float conversion
            main_pe = self._safe_float(main_stock.get('pe_ttm'), default=None)
            avg_pe = averages.get('pe')
            if main_pe is not None and avg_pe is not None:
                if main_pe > avg_pe:
                    lines.append(f"- Higher PE ({main_pe:.2f}x vs peer avg ~{avg_pe:.0f}x)")
                else:
                    lines.append(f"- Lower PE ({main_pe:.2f}x vs peer avg ~{avg_pe:.0f}x)")

            # Dividend Yield comparison - use safe float conversion
            main_div = self._safe_float(main_stock.get('div_yield'), default=None)
            avg_div = averages.get('div_yield')
            if main_div is not None and avg_div is not None:
                if main_div > avg_div:
                    lines.append(f"- Higher Dividend Yield ({main_div:.2f}% vs peer avg ~{avg_div:.0f}%)")
                else:
                    lines.append(f"- Lower Dividend Yield ({main_div:.2f}% vs peer avg ~{avg_div:.0f}%)")

            lines.append("")

        # KEY OBSERVATIONS
        if main_stock:
            lines.append("KEY OBSERVATIONS:")
            lines.append("-" * 17)

            # ROE observation - use safe float conversion
            roe_val = self._safe_float(main_stock.get('roe'), default=None)
            if roe_val is not None:
                if roe_val > 40:
                    lines.append(f"✓ {main_stock['name']} has strong ROE of {roe_val:.1f}%")
                elif roe_val > 20:
                    lines.append(f"✓ {main_stock['name']} has healthy ROE of {roe_val:.1f}%")
                else:
                    lines.append(f"✓ {main_stock['name']} has ROE of {roe_val:.1f}%")

            # P/BV observation - use safe float conversion
            pb_val = self._safe_float(main_stock.get('pb'), default=None)
            roe_val = self._safe_float(main_stock.get('roe'), default=None)
            if pb_val is not None and roe_val is not None:
                if pb_val > 5 and roe_val > 30:
                    lines.append(f"✓ {main_stock['name']} P/BV justified by ROE")

            # Dividend Yield observation - use safe float conversion
            div_val = self._safe_float(main_stock.get('div_yield'), default=None)
            if div_val is not None:
                if div_val > 3:
                    lines.append(f"✓ {main_stock['name']} offers dividend yield of {div_val:.2f}%")

            # PE observation - use safe float conversion
            pe_val = self._safe_float(main_stock.get('pe_ttm'), default=None)
            if pe_val is not None:
                if pe_val < 25:
                    lines.append(f"✓ {main_stock['name']} PE at reasonable {pe_val:.2f}x")
                elif pe_val < 35:
                    lines.append(f"✓ {main_stock['name']} PE at moderate {pe_val:.2f}x")
                else:
                    lines.append(f"✓ {main_stock['name']} PE at elevated {pe_val:.2f}x")

            lines.append("")

        # MARKET CAP RANKING
        if main_stock:
            lines.append("MARKET CAP RANKING:")
            lines.append("-" * 19)

            # Format market cap
            mcap = main_stock.get('mcap', 'N/A')
            if mcap != 'N/A':
                try:
                    mcap_val = float(mcap)
                    if mcap_val > 1000:
                        mcap_str = f"₹{mcap_val:,.0f} Crores"
                    else:
                        mcap_str = f"₹{mcap_val:.2f} Crores"
                except:
                    mcap_str = f"₹{mcap} Crores"
            else:
                mcap_str = "N/A"

            lines.append(f"{main_stock['name']} Market Cap:       {mcap_str}")

            # Add ranking among peers
            sorted_peers = sorted(metrics_list,
                                key=lambda x: self._safe_float(x.get('mcap'), default=0),
                                reverse=True)

            rank = 1
            for i, peer in enumerate(sorted_peers):
                if peer['sid'] == main_stock['sid']:
                    rank = i + 1
                    break

            if rank == 1:
                lines.append("Position:             Largest among peer group")
            else:
                lines.append(f"Position:             #{rank} among peer group")

        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 14 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 14 builder"""
    stock_id = 291436  # Bank of Maharashtra

    print("=" * 80)
    print(f"SECTION 14 BUILDER - Testing with Bank of Maharashtra ({stock_id})")
    print("=" * 80)
    print()

    builder = Section14Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section14_output_fixed.txt")

    output_file = f"section14_stock_{stock_id}_fixed.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 14 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section14_output_fixed.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()