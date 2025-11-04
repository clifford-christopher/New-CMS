"""
SECTION 8: SHAREHOLDING PATTERN Builder
Dynamically builds shareholding pattern using API data
"""
import requests
import json
from datetime import datetime

class Section8Builder:
    def __init__(self, stock_id, exchange=0):
        self.stock_id = str(stock_id)
        self.exchange = exchange
        self.shareholding_api_url = "https://frapi.marketsmojo.com/apiv1/financials/get-shareholdings"

        self.shareholding_data = {}

    def fetch_shareholding_data(self):
        """Fetch shareholding data"""
        print(f"Fetching shareholding data...")

        try:
            payload = {
                "sid": int(self.stock_id),
                "exchange": self.exchange
            }

            response = requests.post(self.shareholding_api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Handle both string and int codes
            code = str(result.get('code'))
            if code == '200' and 'data' in result:
                self.shareholding_data = result['data']
                print(f"[OK] Shareholding API successful")
                return True
            else:
                print(f"[WARNING] API returned code: {code}")
        except Exception as e:
            print(f"[WARNING] Shareholding API failed: {e}")

        return False

    def _extract_quarterly_holdings(self):
        """Extract quarterly holdings for all categories from shareholding_graphs.data"""
        try:
            graphs_data = self.shareholding_data.get('shareholding_graphs', {}).get('data', [])

            if not graphs_data or len(graphs_data) == 0:
                return None

            # shareholding_graphs.data is an array of 6 categories
            # Each category has: title, data (dict with quarter keys like "202506")

            # Map category titles to our standard names
            category_mapping = {
                'Promoter holding': 'Promoter',
                'FII Holdings': 'FII',
                'MF Holdings': 'MF',
                'Insurance Holdings': 'Insurance',
                'Other DII Holdings': 'Other DII',
                'NIIs Holdings': 'Non-Institutional'
            }

            # Initialize structure for 6 categories
            categories = {
                'Promoter': [],
                'FII': [],
                'MF': [],
                'Insurance': [],
                'Other DII': [],
                'Non-Institutional': []
            }

            # Extract quarters from first category to get chronological order
            if graphs_data and len(graphs_data) > 0:
                first_cat_data = graphs_data[0].get('data', {})
                # Get quarter keys sorted in reverse (most recent first)
                all_quarters = sorted(first_cat_data.keys(), reverse=True)
                # Take only first 5 quarters
                quarters_to_use = all_quarters[:5]
            else:
                return None

            # For each category in the API
            for cat_obj in graphs_data:
                title = cat_obj.get('title', '')

                # Extract category name from title like "Shareholding - Promoter holding"
                cat_name = None
                for key_phrase, std_name in category_mapping.items():
                    if key_phrase in title:
                        cat_name = std_name
                        break

                if not cat_name:
                    continue

                # Get quarterly data for this category
                quarter_data_dict = cat_obj.get('data', {})

                # Extract values for each quarter
                for q_key in quarters_to_use:
                    q_info = quarter_data_dict.get(q_key, {})
                    quarter_label = q_info.get('date', 'N/A')  # Like "Jun 2025"
                    value = q_info.get('value', 0)

                    # Format value as percentage
                    formatted_value = f"{value:.2f}%"

                    categories[cat_name].append({
                        'quarter': quarter_label,
                        'value': formatted_value
                    })

            return categories
        except Exception as e:
            print(f"[WARNING] Error extracting quarterly holdings: {e}")
            return None

    def _calculate_qoq_change(self, current, previous):
        """Calculate QoQ change between two values"""
        try:
            if current == 'N/A' or previous == 'N/A':
                return 'N/A'

            curr_val = float(str(current).replace('%', '').strip())
            prev_val = float(str(previous).replace('%', '').strip())

            change = curr_val - prev_val

            if change > 0:
                return f"+{change:.2f}"
            elif change < 0:
                return f"{change:.2f}"
            else:
                return "0.00"
        except:
            return 'N/A'

    def _extract_promoter_details(self):
        """Extract individual promoter holdings (only those with holdings > 0%)"""
        try:
            promoter_data = self.shareholding_data.get('promoter_holding', {}).get('data', [])

            promoters = []
            for i, p in enumerate(promoter_data):
                # Skip header row (first row)
                if i == 0:
                    continue

                name = p.get('shp_name', '')
                holding = p.get('shp_perc', '0')

                # Filter only those with holdings > 0%
                try:
                    holding_val = float(str(holding).replace('%', '').strip())
                    if holding_val > 0:
                        promoters.append({'name': name, 'holding': holding})
                except:
                    continue

            return promoters
        except:
            return []

    def _extract_institutional_activity(self):
        """Extract institutional activity from rhs array"""
        try:
            import re
            rhs_data = self.shareholding_data.get('shareholding', {}).get('rhs', [])

            activity = {
                'fii_count': 'N/A',
                'mf_count': 'N/A',
                'insurance_count': 'N/A'
            }

            for item in rhs_data:
                prefix = item.get('prefix', '')
                suffix = item.get('suffix', '')

                # Extract FII count from "Held by 1547 FIIs (11.47%)"
                if 'FII' in prefix:
                    match = re.search(r'(\d+)\s+FII', suffix)
                    if match:
                        activity['fii_count'] = match.group(1)

                # Extract MF count from "Held by 40 Schemes (5.13%)"
                elif 'Mutual Fund' in prefix:
                    match = re.search(r'(\d+)\s+Scheme', suffix)
                    if match:
                        activity['mf_count'] = match.group(1)

                # Insurance - check if there's similar pattern
                elif 'Insurance' in prefix:
                    match = re.search(r'(\d+)', suffix)
                    if match:
                        activity['insurance_count'] = match.group(1)

            return activity
        except:
            return {
                'fii_count': 'N/A',
                'mf_count': 'N/A',
                'insurance_count': 'N/A'
            }

    def _extract_pledging_info(self):
        """Extract pledging information"""
        try:
            # Check RHS first for pledging status
            rhs_data = self.shareholding_data.get('shareholding', {}).get('rhs', [])

            for item in rhs_data:
                prefix = item.get('prefix', '')
                suffix = item.get('suffix', '')

                if 'Pledged' in prefix:
                    if suffix.lower() == 'none':
                        return "No pledging"
                    else:
                        return suffix

            # Fallback: check pledged_shares.details
            pledged_data = self.shareholding_data.get('pledged_shares', {}).get('details', {})

            if pledged_data:
                alert = pledged_data.get('data', {}).get('alert', '')
                if 'No' in alert:
                    return "No pledging"

            return "No pledging"
        except:
            return "Data Not Available"

    def build_section(self):
        """Build SECTION 8 from API data"""
        # Fetch all data first (if not already loaded)
        if not self.shareholding_data:
            if not self.fetch_shareholding_data():
                return "ERROR: Failed to fetch shareholding data"

        # Extract quarterly holdings
        categories = self._extract_quarterly_holdings()

        if not categories:
            return "ERROR: Failed to extract quarterly holdings"

        # Build output
        lines = []
        lines.append("=" * 80)
        lines.append("SECTION 8: SHAREHOLDING PATTERN (Last 5 Quarters)")
        lines.append("=" * 80)
        lines.append("")

        # Get quarter labels from the first category
        quarters = []
        if categories.get('Promoter') and len(categories['Promoter']) > 0:
            quarters = [q['quarter'] for q in categories['Promoter']]

        # Format quarters as "Jun'25" instead of "Jun 2025"
        quarters_formatted = []
        for q in quarters:
            q_parts = q.split()
            if len(q_parts) == 2:
                month = q_parts[0][:3]  # First 3 letters
                year = q_parts[1][2:]   # Last 2 digits
                quarters_formatted.append(f"{month}'{year}")
            else:
                quarters_formatted.append(q)

        # Header row
        lines.append("")
        header = "Quarter:                "
        for q in quarters_formatted:
            header += f"{q:<8}"
        lines.append(header)

        # Separator
        lines.append("-" * 62)

        # For each category, print holdings and QoQ changes
        category_labels = {
            'Promoter': 'Promoter Holding:',
            'FII': 'FII Holding:',
            'MF': 'Mutual Fund Holding:',
            'Insurance': 'Insurance Holdings:',
            'Other DII': 'Other DII Holdings:',
            'Non-Institutional': 'Non-Institutional:'
        }

        for cat_name, cat_label in category_labels.items():
            cat_data = categories.get(cat_name, [])

            if len(cat_data) == 0:
                continue

            # Holdings row
            row = f"{cat_label:<24}"
            for q in cat_data:
                val = q.get('value', 'N/A')
                row += f"{val:<8}"
            lines.append(row)

            # QoQ change row
            change_row = f"{'Change (Sequential):':<24}"
            for i, q in enumerate(cat_data):
                if i == len(cat_data) - 1:
                    # Oldest quarter - no previous data
                    change_row += f"{'N/A':<8}"
                else:
                    # Calculate change from next quarter (older)
                    current = q.get('value', 'N/A')
                    previous = cat_data[i + 1].get('value', 'N/A')
                    change = self._calculate_qoq_change(current, previous)
                    # Add % sign if not N/A
                    if change != 'N/A':
                        change = f"{change}%"
                    change_row += f"{change:<8}"

            lines.append(change_row)
            lines.append("")

        # PROMOTER DETAILS
        lines.append("KEY PROMOTER DETAILS:")
        lines.append("-" * 21)

        promoters = self._extract_promoter_details()
        if promoters and len(promoters) > 0:
            for p in promoters:
                name = p['name']
                holding = p['holding']
                # Left-aligned format like reference
                lines.append(f"{name:<45} {holding}")
        else:
            lines.append("  Data Not Available")

        lines.append("")

        # INSTITUTIONAL ACTIVITY
        lines.append("INSTITUTIONAL ACTIVITY:")
        lines.append("-" * 23)

        activity = self._extract_institutional_activity()
        lines.append(f"Number of FIIs:                      {activity['fii_count']}")
        lines.append(f"Number of MFs:                       {activity['mf_count']}")
        lines.append(f"Number of Insurance Companies:       {activity['insurance_count']}")

        lines.append("")

        # PLEDGING INFORMATION
        lines.append("PROMOTER PLEDGING:")
        lines.append("-" * 18)

        pledging = self._extract_pledging_info()
        lines.append(f"Pledged Shares:                      {pledging}")

        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def save_to_file(self, output_file):
        """Build section and save to file"""
        section_text = self.build_section()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"\n[OK] Section 8 saved to: {output_file}")
        return section_text


def main():
    """Test the Section 8 builder"""
    stock_id = 513374  # TCS

    print("=" * 80)
    print("SECTION 8 BUILDER - Testing with TCS")
    print("=" * 80)
    print()

    builder = Section8Builder(stock_id)
    section_text = builder.build_section()

    # Save to file
    builder.save_to_file("section8_output.txt")

    output_file = f"section8_stock_{stock_id}.txt"
    builder.save_to_file(output_file)

    print("\n" + "=" * 80)
    print("SECTION 8 OUTPUT SAVED")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - section8_output.txt")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
