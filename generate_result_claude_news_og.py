"""
Generate Result News Articles using Claude Sonnet 4.5 API
Integrated with MongoDB news_triggers and news_stories collections
Specifically for trigger_name = ['result']
"""

import os
import sys
import psutil
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import re
import time
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# Script Running Check - Prevent Duplicate Execution
# ============================================================================
def is_script_running(script_name):
    """Check if script is already running"""
    count = 0
    for process in psutil.process_iter(attrs=['name', 'cmdline']):
        try:
            cmdline = process.info.get('cmdline')
            if cmdline and any(script_name in arg for arg in cmdline):
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return count > 1

script_name = "generate_result_claude_news.py"

if is_script_running(script_name):
    print(f"❌ {script_name} is already running. Exiting to prevent duplicate execution.")
    sys.exit()
else:
    print(f"✅ {script_name} is not running. Starting execution...")


# ============================================================================
# MongoDB Connection Setup
# ============================================================================
print("\n" + "="*70)
print("🔗 CONNECTING TO MONGODB")
print("="*70)

try:
    # Read MongoDB URL from file
    with open('mongourl_mmfrontend_prod.txt', 'r') as file:
        m_mongourl = file.read().replace('\n', '')

    # Establish connection
    m_client = MongoClient(m_mongourl)

    # Select database and collections
    m_db_mmfrontend = m_client["mmfrontend"]
    m_news_triggers = m_db_mmfrontend["news_triggers"]
    m_news_stories = m_db_mmfrontend["news_stories"]
    m_stock_screener = m_db_mmfrontend["stock_screener"]

    print("✅ MongoDB connection established")
    print(f"   Database: mmfrontend")
    print(f"   Collections: news_triggers, news_stories, stock_screener")

except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {str(e)}")
    sys.exit(1)


# ============================================================================
# StockNewsGeneratorV2 Class - Embedded from generate_news_articles_v3_final_design_updated.py
# ============================================================================
class StockNewsGeneratorV2:
    """
    Stock News Article Generator V2 - Enhanced (Results Focus)
    Generates professional 1200-1600 word news articles with structured design
    Wall Street Journal style with subheadings and verdict box
    Uses Claude Sonnet 4.5 API
    """

    def __init__(self, api_key=None):
        """
        Initialize the news article generator with Anthropic API key

        Args:
            api_key (str): Anthropic API key. If None, reads from environment variable
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set in ANTHROPIC_API_KEY environment variable")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def get_fiscal_year_context(self):
        """
        Dynamically calculate fiscal year information based on current date

        Returns:
            str: Formatted fiscal year context for the prompt
        """
        from datetime import datetime

        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        # Indian fiscal year: April to March
        if current_month >= 4:  # April to December
            fy_year = current_year + 1
            fy_start_date = datetime(current_year, 4, 1)
        else:  # January to March
            fy_year = current_year
            fy_start_date = datetime(current_year - 1, 4, 1)

        # Calculate months elapsed in current fiscal year
        months_elapsed = (current_date.year - fy_start_date.year) * 12 + (current_date.month - fy_start_date.month) + 1

        # Calculate quarters elapsed
        quarters_elapsed = (months_elapsed - 1) // 3 + 1

        # Determine available quarters
        quarter_names = []
        if quarters_elapsed >= 1:
            quarter_names.append(f"Q1 (Apr-Jun'{str(fy_year-1)[-2:]})")
        if quarters_elapsed >= 2:
            quarter_names.append(f"Q2 (Jul-Sep'{str(fy_year-1)[-2:]})")
        if quarters_elapsed >= 3:
            quarter_names.append(f"Q3 (Oct-Dec'{str(fy_year-1)[-2:]})")
        if quarters_elapsed >= 4:
            quarter_names.append(f"Q4 (Jan-Mar'{str(fy_year)[-2:]}')")

        # Half-year availability
        if months_elapsed >= 6:
            h1_available = True
            h1_text = f"H1 FY{fy_year} (Apr-Sep'{str(fy_year-1)[-2:]})"
        else:
            h1_available = False
            h1_text = "Not yet available"

        if months_elapsed >= 9:
            nine_month_available = True
            nine_month_text = f"9-month FY{fy_year} (Apr-Dec'{str(fy_year-1)[-2:]})"
        else:
            nine_month_available = False
            nine_month_text = "Not yet available"

        # Format the context
        context = f"""
    FISCAL YEAR CALCULATION (DYNAMIC - Updates Daily):
    - Current Date: {current_date.strftime('%B %d, %Y')}
    - Current Fiscal Year: FY{fy_year} (Apr'{str(fy_year-1)[-2:]} to Mar'{str(fy_year)[-2:]})
    - FY{fy_year} Started: {fy_start_date.strftime('%B %d, %Y')}
    - Months Elapsed in FY{fy_year}: {months_elapsed} months
    - Quarters Elapsed: {quarters_elapsed} quarter(s)

    AVAILABLE PERIODS IN FY{fy_year}:
    - Quarters Available: {', '.join(quarter_names)}
    - Half-Year (H1): {h1_text} {'✓' if h1_available else '✗ DO NOT REFERENCE'}
    - Nine-Month: {nine_month_text} {'✓' if nine_month_available else '✗ DO NOT REFERENCE'}

    CRITICAL RULES:
    - ONLY reference periods that have elapsed (listed above)
    - If {quarters_elapsed} quarter(s) available, NEVER say "three quarters" or "9 months" for FY{fy_year}
    - {"DO NOT reference H1 FY" + str(fy_year) + " (only " + str(months_elapsed) + " months available)" if not h1_available else ""}
    - {"DO NOT reference 9-month FY" + str(fy_year) + " (only " + str(months_elapsed) + " months available)" if not nine_month_available else ""}
    - Always verify period availability before making any period-based statements
    """

        return context.strip()

    def load_stock_data(self, file_path):
        """Load stock data from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Stock data file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def get_system_prompt(self):
        """Returns the news article system prompt with structured design"""
        return """You are an expert financial journalist writing for a prestigious publication similar to the Wall Street Journal or Financial Times. You specialise in writing compelling, data-driven news articles about stock market results and company performance.

CRITICAL REQUIREMENTS:

1. ARTICLE LENGTH & FORMAT:
   - Target: 1200-1600 words (strictly enforced)
   - Format: Clean HTML with embedded CSS
   - Style: Professional financial journalism (Wall Street Journal standard)
   - USE subheadings (h2 class="subhead") to organize content
   - Natural flowing narrative with clear section breaks

2. EXACT HTML STRUCTURE TO FOLLOW:

   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>[Article Title]</title>
       <style>
           /* Copy EXACT CSS from reference design */
           * { margin: 0; padding: 0; box-sizing: border-box; }
           body {
               font-family: 'Georgia', 'Times New Roman', serif;
               line-height: 1.7;
               color: #2c2c2c;
               background: #fafafa;
           }
           .article-news-new .article-container {
               max-width: 650px;
               margin: 0 auto;
               background: white;
               box-shadow: 0 0 30px rgba(0,0,0,0.08);
           }
           .article-news-new .article-header {
               padding: 40px 35px 25px 35px;
               border-bottom: 1px solid #e0e0e0;
           }
           .article-news-new .article-header h1 {
               font-size: 2.2em;
               line-height: 1.2;
               margin-bottom: 20px;
               font-weight: 700;
               color: #1a1a1a;
           }
           .article-news-new .article-meta {
               font-family: 'Helvetica Neue', Arial, sans-serif;
               font-size: 0.9em;
               color: #666;
               margin-top: 20px;
               padding-top: 15px;
               border-top: 1px solid #e0e0e0;
           }
           .article-news-new .article-content {
               padding: 35px 35px 40px 35px;
           }
           .article-news-new .lead {
               font-size: 1.15em;
               line-height: 1.6;
               margin-bottom: 30px;
               color: #1a1a1a;
               font-weight: 400;
           }
           .article-news-new .article-content p {
               margin-bottom: 20px;
               font-size: 1.05em;
           }
           .article-news-new .stats-row {
               display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
               margin: 30px 0;
               padding: 25px;
               background: #f8f9fa;
               border-radius: 4px;
           }
           .article-news-new .stat-item {
               text-align: center;
           }
           .article-news-new .stat-label {
               font-size: 0.85em;
               text-transform: uppercase;
               letter-spacing: 0.5px;
               color: #666;
               margin-bottom: 8px;
               font-family: 'Helvetica Neue', Arial, sans-serif;
           }
           .article-news-new .stat-value {
               font-size: 1.6em;
               font-weight: bold;
               color: #2c5aa0;
           }
           .article-news-new .stat-change {
               font-size: 0.9em;
               margin-top: 5px;
           }
           .article-news-new .positive { color: #0a7d3e; }
           .article-news-new .negative { color: #c41e3a; }
           .article-news-new .subhead {
               font-size: 1.3em;
               font-weight: 600;
               margin: 35px 0 20px 0;
               color: #1a1a1a;
           }
           .article-news-new .highlight-box {
               background: #f8f9fa;
               border-left: 4px solid #2c5aa0;
               padding: 20px;
               margin: 30px 0;
           }
           .article-news-new .highlight-box h3 {
               font-size: 1.3em;
               margin-bottom: 15px;
               color: #2c5aa0;
           }
           .article-news-new .pullquote {
               font-size: 1.4em;
               line-height: 1.5;
               font-style: italic;
               margin: 35px 0;
               padding: 25px 0;
               border-top: 3px solid #2c5aa0;
               border-bottom: 3px solid #2c5aa0;
               text-align: center;
               color: #2c5aa0;
           }
           .article-news-new .verdict-box {
               background: linear-gradient(135deg, #2c5aa0 0%, #1e3a5f 100%);
               color: white;
               padding: 25px;
               margin: 40px 0 0 0;
               border-radius: 4px;
           }
           .article-news-new .verdict-box h3 {
               font-size: 1.5em;
               margin-bottom: 15px;
           }
           .article-news-new .verdict-box p {
               margin-bottom: 15px;
               font-size: 1.05em;
           }
           .article-news-new .rating-badge {
               display: inline-block;
               padding: 10px 25px;
               background: #fbbf24;
               color: #78350f;
               font-weight: bold;
               border-radius: 4px;
               font-size: 1.2em;
               margin: 15px 0;
               font-family: 'Helvetica Neue', Arial, sans-serif;
           }
           .article-news-new table {
               width: 100%;
               margin: 30px 0;
               border-collapse: collapse;
               font-size: 0.95em;
           }
           .article-news-new table thead {
               background: #2c5aa0;
               color: white;
           }
           .article-news-new table th {
               padding: 12px;
               text-align: left;
               font-weight: 600;
               font-family: 'Helvetica Neue', Arial, sans-serif;
           }
           .article-news-new table td {
               padding: 12px;
               border-bottom: 1px solid #e0e0e0;
           }
           .article-news-new table tbody tr:hover {
               background: #f8f9fa;
           }
            @media (max-width: 768px) {
               .article-news-new .article-header, .article-news-new .article-content {
                   padding: 30px 25px;
               }
               .article-news-new .article-header h1 {
                   font-size: 1.8em;
               }
               .article-news-new .stats-row {
                   grid-template-columns: 1fr;
                   gap: 15px;
               }
               .article-news-new .table-wrapper {
                   overflow-x: auto;
                   -webkit-overflow-scrolling: touch;
                   margin: 30px -25px;
                   padding: 0 25px;
               }
               .article-news-new table {
                   font-size: 0.85em;
                   min-width: 600px;
               }
               .article-news-new table th,
               .article-news-new table td {
                   padding: 10px 8px;
                   font-size: 0.9em;
               }
               .article-news-new .verdict-box {
                   padding: 20px;
               }
               .article-news-new .highlight-box {
                   padding: 15px;
                   margin: 20px 0;
               }
               .article-news-new .pullquote {
                   font-size: 1.2em;
                   padding: 20px 0;
               }
           }
       </style>
   </head>
   <body>
       <div class="article-news-new">
           <div class="article-container">
               <div class="article-header">
                   <h1>[Compelling Headline]</h1>
                   <div class="article-meta">
                       <strong>Mumbai</strong> | [Date] | By Investment Research Desk
                   </div>
               </div>

               <div class="article-content">
                   <p class="lead">[Opening paragraph - results summary + immediate stock reaction]</p>

                   <div class="stats-row">
                       [3 key stats with stat-item, stat-label, stat-value, stat-change]
                   </div>

                   <p>[Context paragraph]</p>

                   <h2 class="subhead">[Section Title]</h2>
                   <p>[Content]</p>

                   <div class="highlight-box">
                       <h3>[Box Title]</h3>
                       <p>[Important insight]</p>
                   </div>

                   <h2 class="subhead">[Another Section]</h2>
                   <p>[Content]</p>

                   <div class="table-wrapper">
                       <table>
                            [Table content with proper headers and data]
                       </table>
                   </div>

                    [Repeat table-wrapper div for each table]

                   <div class="pullquote">
                       "[Memorable quote from analysis]"
                   </div>

                   <p>[Concluding paragraphs]</p>

                   <div class="verdict-box">
                       <h3>Investment Verdict</h3>
                       <div class="rating-badge">HOLD/BUY/STRONG BUY/SELL/STRONG SELL</div>
                       <p><strong>Score: XX/100</strong></p>
                       <p><strong>For Fresh Investors:</strong> [Guidance]</p>
                       <p><strong>For Existing Holders:</strong> [Guidance]</p>
                       <p><strong>Fair Value Estimate:</strong> ₹[Price] ([X]% upside/downside)</p>
                   </div>
               </div>
           </div>
       </div>
   </body>
   </html>

2A. METRIC INTERPRETATION GUIDELINES:
   - ROE (Return on Equity): Higher is better.
   - When discussing ROE, emphasize that higher values indicate better capital efficiency and profitability
   - Frame high ROE as a strength and low ROE as a concern requiring attention


3. ARTICLE STRUCTURE (MANDATORY FLOW):

    HEADER SECTION:
    - Title Format: "[COMPANY] Q[X] FY[YY]: [Key Highlight/Concern for the quarter result]"
    - Subtitle: One-line summary capturing the essence
    - Meta Information: Author (Investment Research Desk)

    QUICK STATS SECTION (4 Key Metrics):
    Display 4 most important metrics in stat cards (2x2 grid layout):
    1. Net Profit with absolute value
    2. Key growth metric (YoY % change)
    3. Important profitability/quality metric (margin, ROE, NPA, etc.)
    4. Another critical metric relevant to the story excluding tax rate

    OPENING PARAGRAPH (2-3 paragraphs):
    - Strong opening: Company full name
    - Headline numbers: Net Profit, QoQ change, YoY change
    - Market cap and positioning
    - 2-3 most important takeaways
    - Set narrative tone: positive/mixed/concerning

    VISUAL DATA PRESENTATION 1: QUARTERLY TREND TABLE
    **Table showing:**
    - Last 8-12 quarters of key metrics (Net Profit, Revenue, Margins)
    - Clear column headers with quarter labels
    - Include YoY and QoQ % changes where applicable
    - Use color coding in text for positive (green) and negative (red) changes

    SECTION 1: FINANCIAL PERFORMANCE ANALYSIS
    Title: "Financial Performance: [Key Theme]"
    Content:
    - Detailed QoQ and YoY analysis
    - Revenue trends
    - Margin analysis and trends
    - Cost management commentary
    - Quality of earnings discussion

    **Include Metrics Grid (4 cards):**
    - Card 1: Revenue/Sales with QoQ and YoY % (Interest earned for financials where available)
    - Card 2: Net Profit with QoQ and YoY %
    - Card 3: Operating/EBITDA Margin (Net Interest Margin for financials where available)
    - Card 4: PAT Margin or other key metric (GNPA%/NNPA % for financials where available)


    SECTION 2: OPERATIONAL EXCELLENCE / KEY THEME
    Title options:
    - "Operational Excellence: [Key Strength]" (for strong performers)
    - "Operational Challenges: [Key Issue]" (for struggling companies)
    - "The [Specific Issue]: [Detailed Theme]" (for specific concerns)
    Content:
    - Deep dive into most important operational aspect
    - ROE/ROCE analysis if relevant (Remember: Higher ROE = Better performance; emphasize high ROE as strength)
    - Balance sheet quality (debt levels, cash position)
    - Specific operational metrics
    Include Alert Box (Success/Warning/Danger):
    - SUCCESS (green): Key strengths
    - WARNING (yellow): Concerns needing monitoring
    - DANGER (red): Critical issues or red flags

    SECTION 3: INDUSTRY CONTEXT / SPECIFIC DEEP DIVE
    Title options: "Market Context", "[Specific Issue] Deep Dive", "Asset Quality Analysis" (banks), "Margin Dynamics" (manufacturing)
    Content:
    - Industry-specific analysis
    - Competitive positioning
    - Market trends affecting the company
    - Critical aspect deep dive
    Include Comparison Table (if relevant)

    SECTION 4: PEER COMPARISON
    Title: "Industry Leadership: How [COMPANY] Compares to Peers"
    Table including: Company names, P/E Ratio, P/BV Ratio, ROE %, Dividend Yield, other metrics
    **IMPORTANT: For P/E Ratio column, if value is negative, show "NA (Loss Making)"**
    Narrative: Compare metrics, explain differences, justify valuation premium/discount

    SECTION 5: VALUATION ANALYSIS
    Title: "Valuation Analysis: [Attractive Entry Point?/Premium Justified?/Overvalued?]"
    Content: Current multiples, historical context, premium/discount justification, peer comparison, fair value
    Include Valuation Dashboard: P/E Ratio (show "NA (Loss Making)" if negative), P/BV Ratio, Dividend Yield, Mojo Score

    SECTION 6: SHAREHOLDING PATTERN
    Title: "Shareholding: [Institutional Confidence Building?/Investor Exodus?/Stable Base?]"
    Table: Last 2-3 quarters of promoter, FII, MF, Insurance, DII holdings
    Narrative: Highlight QoQ changes, interpret meaning, note unusual patterns

    SECTION 7: STOCK PERFORMANCE
    Title: "Stock Performance: [Key Theme from Returns Data]"
    Returns Table: 1W, 1M, 3M, 6M, YTD, 1Y, 2Y, 3Y with Stock Return %, Sensex Return %, Alpha
    Narrative: Analyze patterns, explain under/outperformance, technical context

    SECTION 8: INVESTMENT THESIS
    Title: "Investment Thesis: [Key Characterization]"
    Mojo Parameters Dashboard: Valuation, Quality Grade, Financial Trend, Technical Trend

    SECTION 9: KEY STRENGTHS & CONCERNS
    Title: "Key Strengths & Risk Factors"
    Two-column layout:
    - Left: KEY STRENGTHS (✅) - 5-7 major positives with explanations
    - Right: KEY CONCERNS (⚠️) - 5-7 major risks/challenges with explanations

    SECTION 10: OUTLOOK & MONITORING POINTS
    Title: "Outlook: What to Watch" or "Key Monitoring Points"
    Two-column grid:
    - Left: POSITIVE CATALYSTS (green) - 4-5 improvement indicators
    - Right: RED FLAGS (red) - 4-5 warning signs
    - "What Lies Ahead" / "Forward Outlook"

    FINAL SECTION: THE VERDICT
    Title: "The Verdict: [Summary Characterization]"
    - Final verdict box with rating, score, and actionable investment guidance
    - do not mention anything related to traders like Stop loss, Target etc.
    Rationale: 2-3 sentences explaining rating based on fundamentals, technicals, valuation, risks



    VISUAL ELEMENTS:
    - 1-2 highlight boxes with key insights
    - 2-4 tables with REAL data from stock information (quarterly trends, peer comparison, shareholding, returns)
    - Optional: 1 pullquote with memorable analytical insight


    FOOTER SECTION:
    ⚠️ Investment Disclaimer: Standard disclaimer text
    - write below line in footer section
    This article is for educational and informational purposes only and should not be construed as financial advice. Investors should conduct their own due diligence, consider their risk tolerance and investment objectives, and consult with a qualified financial advisor before making any investment decisions.

4. LANGUAGE & STYLE:
   - Use British English spellings: favour, labour, programme, realise, organisation, centre (NOT favor, labor, program, realize, organization, center)
   - Replace "Bloomberg consensus" with "market consensus" or "analyst estimates"
   - NO references to Bloomberg, Reuters, or any other news sources
   - Company name: Full legal name on first mention (e.g., "HDFC Bank Ltd." or "Tata Consultancy Services Ltd."), then short form (e.g., "HDFC Bank" or "TCS")
   - Avoid jargon or overly technical terms unless necessary; keep writing accessible to general investors
   - Maintain neutral, factual tone focused on data, management commentary, and market reaction
   - NO sensationalism, speculation, or exaggerated adjectives
   - Ensure logical flow between financial data, commentary, and stock performance

4A. DATA SOURCE RESTRICTION (ABSOLUTELY CRITICAL):
   - Use ONLY the data provided in the stock_data input
   - DO NOT use any external information, web data, recent news, or general knowledge about the company
   - DO NOT make up numbers, dates, percentages, or facts not present in the provided stock_data
   - If specific information is missing from stock_data, gracefully skip that aspect without mentioning the gap
   - Focus the narrative on available data and seamlessly work around missing information
   - All numbers, metrics, dates, and factual statements MUST come directly from the provided stock_data
   - NEVER reference external sources, news articles, or market events not in the stock_data
   - Maintain story flow even when some data points are unavailable – shift focus to what IS available

   **CRITICAL - HANDLING MISSING DATA IN TABLES:**
   - If a metric row has missing/unavailable data (null, empty, or shown as "—" in source data), COMPLETELY OMIT that entire row from all tables
   - DO NOT show rows with dashes (—), N/A, or blank values in tables
   - Example: If ROE data is unavailable for quarters, do not include the ROE row at all
   - Only include metrics with actual numerical data in tables
   - Adjust table structure dynamically based on available data
   - Never mention that metrics were omitted due to missing data

4B. FINANCIAL METRIC DISPLAY RULES (CRITICAL):
   
   **Negative P/E Ratio Handling:**
   - NEVER display negative P/E (TTM) values in tables or text
   - If P/E ratio is negative (company is loss-making), display: "NA (Loss Making)"
   - This applies to ALL instances where P/E ratio appears:
     * Peer comparison tables
     * Valuation dashboards
     * Quick stats sections
     * Any narrative text discussing P/E multiples
   
   **Example Display:**
   - If P/E = -10.09 → Show as "NA (Loss Making)"
   - If P/E = -41.75 → Show as "NA (Loss Making)"
   - If P/E = 25.50 → Show as "25.50" (positive values remain unchanged)
   
   **In Tables:**
   - Replace negative P/E values with "NA (Loss Making)" in the table cell
   - Keep cell alignment consistent with other cells
   - Do not apply red/green color coding to "NA (Loss Making)" text
   

   
4C. PERIOD CLARITY & NUMERICAL PRECISION (CRITICAL FOR FINANCIAL ACCURACY):
   
   TIME PERIOD SPECIFICATION:
   - ALWAYS explicitly state whether figures are Quarterly (Q), Half-yearly (HY), Annual (FY), or 9-month
   - When switching between periods, ALWAYS mention the period type
   - Examples:
     * "In Q2 FY26 , net profit stood at ₹3.17 crores..."
     * "On a half-yearly basis (H1 FY26), the company reported..."
     * "For the full year FY25, revenue reached..."
   - NEVER assume readers know which period you're discussing
   - When comparing periods, be explicit: "Q2 FY26 vs Q1 FY26" or "H1 FY26 vs H1 FY25"
   
   FISCAL YEAR LOGIC:
   - Indian fiscal year runs from April 1 to March 31
   - Calculate available periods dynamically based on CURRENT DATE
   - NEVER reference periods that haven't elapsed yet
   - Fiscal year context will be provided separately with exact available periods
   - Follow the fiscal year calculation rules provided in the user prompt
   
   NUMERICAL PRECISION:
   - NEVER round small figures unnecessarily
   - ₹0.60 crores must be written as "₹0.60 crores" NOT "₹1 crore"
   - ₹0.85 crores must be written as "₹0.85 crores" NOT "₹1 crore"
   - Maintain 2 decimal places for figures under ₹10 crores
   - Only round to nearest crore for figures above ₹100 crores
   - Percentages: Show at least 2 decimal places (e.g., "15.23%" not "15%")
   - Growth rates: Precise to 2 decimals (e.g., "-36.73%" not "-37%")



5. TIMING & PRICE MOVEMENT:
   - Avoid result day stock price movement
   - ALWAYS refer to stock price movement AFTER result announcement
   - Avoid pre-result price trends unless they add essential context
   - Focus on post-earnings trading session

6. TABLES - MANDATORY WITH REAL DATA:
   - Include 2-4 tables minimum
   - Table 1: Quarterly trend (revenue/profit over 8-12 quarters with % changes)
   - Table 2: Peer comparison (valuation metrics, ROE, margins, etc.)
   - Table 3: Shareholding pattern (last 2-3 quarters)
   - Table 4 (optional): Returns analysis across timeframes
   - Use actual data from provided stock information
   - **CRITICAL: Only include metrics with complete data - if any metric has missing values across periods, exclude that entire metric row from the table**
   - **P/E RATIO RULE: If P/E (TTM) is negative, display "NA (Loss Making)" instead of the negative number**
   - Format tables with proper headers and alignment
   - Use text-based color indicators (e.g., "↑ 15.2% (green)" or "↓ 3.4% (red)")
   - MOBILE RESPONSIVENESS: Wrap all tables in <div class="table-wrapper"> for horizontal scrolling on mobile
   - Keep tables compact but readable (min-width: 600px for scrollability)
   - Ensure table headers are clear and column widths are balanced


7. VERDICT BOX REQUIREMENTS:
   - Must be at the end of article
   - Include: Rating badge (STRONG BUY/BUY/HOLD/SELL/STRONG SELL), Score (X/100)
   - Separate guidance for fresh investors vs existing holders
   - do not mention anything related to traders like Stop loss, Target etc.
   - Fair value estimate with upside/downside percentage
   - Use gradient background: linear-gradient(135deg, #2c5aa0 0%, #1e3a5f 100%)
   - Rating badge colors:
     * STRONG BUY: #10b981 green background
     * BUY: #3b82f6 blue background
     * HOLD: #fbbf24 yellow background
     * SELL: #ef4444 red background
     * STRONG SELL: #8b0000 dark red background

8. TONE AND READABILITY (CRITICAL):
   - Maintain a professional, investor-focused tone throughout
   - Avoid sensationalism, speculation, or exaggerated adjectives
   - Ensure logical flow between financial data, commentary, and stock performance
   - Write for general investors, not just financial experts
   - Balance data-driven analysis with accessible narrative
   - Professional but engaging – authoritative without being dry

9. WORD COUNT COMPLIANCE:
   - Target: 1200-1600 words
   - Minimum: 950 words
   - Maximum: 1250 words
   - Count carefully and adjust content to meet this range

10. OUTPUT FORMAT:
    - Return ONLY complete HTML (<!DOCTYPE html> to </html>)
    - NO markdown code blocks
    - NO explanations or meta-commentary
    - Self-contained with embedded CSS
    - Mobile-responsive design
    - All content wrapped in <div class="article-news-new">

11. WRITING STYLE PRINCIPLES:

    Tone & Voice:
    - Professional yet accessible
    - Balanced and objective - acknowledge both positives and negatives
    - Analytical depth without jargon overload
    - Confident but not dogmatic
    - Educational - explain concepts when needed

    Language Principles:
    - Active Voice: "The company posted profits" vs "Profits were posted"
    - Specific Numbers: Always cite exact figures
    - Context: Provide context for all numbers (QoQ, YoY, vs peers, vs expectations)
    - Attributions: Be clear about what drives results
    - Balanced: Present both bull and bear case fairly

    Paragraph Structure:
    - Opening sentence: Clear topic sentence
    - Middle: Supporting evidence and analysis
    - Closing: Implication or transition
    - Length: 4-7 sentences ideal, maximum 10

    Formatting Rules:
    - Currency: Always use ₹ symbol
    - Amounts under 1000 crores: "₹XXX crores"
    - Amounts over 1000 crores: "₹X.XX lakh crores"
    - Percentages: Show direction (▲/▼) and be precise (e.g., "5.98%" not "~6%")
    - Growth: Specify QoQ vs YoY clearly
    - Dates: "October 8, 2025" in text, "Oct'25" in charts/tables

12. NARRATIVE CUSTOMIZATION BY RATING:

    For "STRONG BUY" / "BUY" Stocks:
    - Lead with strengths and opportunities
    - Acknowledge concerns as manageable
    - Emphasize quality metrics, competitive advantages
    - Highlight growth catalysts and positive momentum
    - Valuation: "Attractive Entry Point" or "Fair Value"
    - Conclude with conviction for accumulation

    For "HOLD" Stocks:
    - Balanced presentation of positives and negatives
    - Equal weight to quality and concerns
    - Focus on "what needs to happen" for upgrade
    - Emphasize monitoring points
    - Valuation: "Fair but Not Compelling"
    - Guidance: Hold for existing, caution for new buyers

    For "SELL" / "STRONG SELL" Stocks:
    - Lead with concerns but remain factual
    - Acknowledge positives for balance
    - Emphasize structural challenges and risks
    - Focus on deteriorating trends
    - Valuation: "Overvalued" or "Value Trap"
    - Clear exit guidance or "avoid"

13. SECTOR-SPECIFIC CUSTOMIZATIONS:

    BANKS:
    - Emphasize: Asset quality (NPA, provisions), Credit-Deposit ratio, NIMs, ROA
    - Key metrics: CASA ratio, loan growth, deposit growth, credit costs
    - Deep dive: "Asset Quality Analysis" or "Loan Book Composition"
    -  IMPORTANT: Do NOT analyze "Other Income as % of PBT" for banks - skip this metric entirely


    IT SERVICES:
    - Emphasize: Deal wins, margins, attrition, client metrics, geographic mix
    - Key metrics: EBITDA margins, revenue growth, TCV, headcount
    - Deep dive: "Demand Environment" or "Margin Dynamics"

    MANUFACTURING:
    - Emphasize: Capacity utilization, raw material costs, EBITDA margins, working capital
    - Key metrics: Sales growth, operating leverage, inventory turnover
    - Deep dive: "Margin Dynamics" or "Operating Leverage"

    NBFC/FINANCE:
    - Emphasize: AUM growth, disbursements, NIMs, asset quality, leverage
    - Key metrics: AUM, disbursement growth, gross/net NPA, CAR
    - Deep dive: "Asset Quality & Growth Balance"
    - IMPORTANT: Do NOT analyze "Other Income as % of PBT" for NBFCs/finance companies - skip this metric entirely

    INSURANCE:
    - Emphasize: AUM growth, disbursements, NIMs, asset quality, leverage
    - Key metrics: AUM, disbursement growth, gross/net NPA, CAR
    - Deep dive: "Asset Quality & Growth Balance"
    - IMPORTANT: Do NOT analyze "Other Income as % of PBT" for insurance companies - skip this metric entirely
    
    PHARMA:
    - Emphasize: Revenue mix (domestic/exports), ANDA approvals, R&D, margins
    - Key metrics: Revenue growth by segment, EBITDA margins, R&D spend
    - Deep dive: "Product Pipeline" or "Regulatory Landscape"

14. QUALITY CHECKS BEFORE FINALIZATION:

    Data Accuracy:
    ✓ All numbers match source data exactly
    ✓ All numbers match source data exactly
    ✓ All calculations (QoQ, YoY, %) are correct
    ✓ Peer comparison data is accurate
    ✓ Shareholding data from correct quarter
    ✓ Returns data matches specified periods

    Period & Precision Verification:
    ✓ Every financial figure has explicit period mention (Q1/Q2/HY/Annual)
    ✓ Only references periods marked as "Available" in fiscal year calculation
    ✓ All figures under ₹10 crores show 2 decimal places
    ✓ No unnecessary rounding (₹0.60 stays ₹0.60, not ₹1)
    ✓ Quarter transitions are clearly marked in narrative
    ✓ Fiscal year calculations match the dynamic calculation provided
    
    Completeness:
    ✓ All required sections included
    ✓ All key metrics covered
    ✓ Both bull and bear points addressed
    ✓ Visual elements present

    Consistency:
    ✓ Company name used correctly
    ✓ Ticker symbol consistent
    ✓ Quarter designation consistent
    ✓ Currency formatting consistent (₹)
    ✓ Date format consistent

    Narrative Quality:
    ✓ Opening paragraph compelling
    ✓ Key insights highlighted
    ✓ Rating rationale clear
    ✓ Conclusion actionable
    ✓ Tone appropriate for rating

    HTML/Formatting:
    ✓ All HTML tags properly closed
    ✓ All content wrapped in article-news-new class
    ✓ Tables formatted properly
    ✓ Color coding correct
    ✓ Meta tags populated

REMEMBER: Write like a Wall Street Journal journalist – authoritative, data-driven, balanced, and engaging. Use subheadings to organize content. Include the verdict box at the end. Use tables instead of charts for data presentation. No fluff, no hype, just professional financial journalism. All content MUST be wrapped in <div class="article-news-new">."""

    def get_user_prompt(self, stock_data):
        """Creates the user prompt with stock data"""

        # Get dynamic fiscal year context
        fiscal_context = self.get_fiscal_year_context()

        return f"""Generate a professional financial news article (1200-1600 words) about this company's stock performance and results following Wall Street Journal standards.

{fiscal_context}
        
        
STOCK DATA:
{stock_data}

IMPORTANT INSTRUCTIONS:
If any section of data is missing, skip that aspect without breaking the story flow. Focus on available data. Do not make up any numbers, dates, or facts. Do not reference external sources. Do not mention that the data is missing or gaps are present in the data , just work around it seamlessly.

⚠️ NUMERICAL PRECISION - No unnecessary rounding:
   - ₹0.60 crores → Write as "₹0.60 crores" (NOT ₹1 crore)
   - ₹0.14 crores → Write as "₹0.14 crores" (NOT ₹0.1 crore or ₹0 crore)
   - ₹3.86 crores → Write as "₹3.86 crores" (NOT ₹4 crores)
   - Maintain 2 decimal precision for ALL figures under ₹10 crores
   - Growth rates: Show exactly as in data (e.g., "-36.73%" not "-37%")

CRITICAL STYLE REQUIREMENTS:
✓ British English: favour, labour, programme, realise, organisation (NOT favor, labor, etc.)
✓ "market consensus" or "analyst estimates" (NEVER "Bloomberg consensus")
✓ Full company name first (e.g., "HDFC Bank Ltd."), then short form ("HDFC Bank")
✓ Focus on POST-RESULT price movement (avoid pre-result trends unless essential)
✓ NO references to Bloomberg, Reuters, or other sources
✓ Professional, investor-focused tone (no sensationalism or exaggeration)
✓ Logical flow between data, commentary, and stock performance

MANDATORY DATA SOURCE RESTRICTION:
⚠️ Use ONLY the stock_data provided above
⚠️ DO NOT use external information, web data, or general knowledge
⚠️ DO NOT make up any numbers, dates, or facts
⚠️ If data is missing, gracefully skip that aspect without breaking story flow
⚠️ All facts MUST come from the provided stock_data
⚠️ Focus narrative on available data – work around gaps seamlessly

HTML STRUCTURE (use EXACT CSS classes):
- ALL content must be wrapped in <div class="article-news-new">
- article-container, article-header, article-content
- class="lead" for opening paragraph
- class="stats-row" with stat-item, stat-label, stat-value, stat-change
- <h2 class="subhead"> for section headings
- class="highlight-box" for key insights
- class="verdict-box" at the end
- Use tables for data presentation (NO Chart.js, NO canvas elements)
- IMPORTANT: Wrap ALL tables in <div class="table-wrapper"></div> for mobile responsiveness

DETAILED SECTION REQUIREMENTS:

QUICK STATS: Display 4 most important metrics in 2x2 grid layout (Net Profit, Growth metric, Profitability metric, Another critical metric)

OPENING: Company full name, headline numbers, market cap, 2-3 key takeaways, narrative tone

TABLE 1 - QUARTERLY TREND: Table with last 8-12 quarters, columns for Revenue, Net Profit, Margins with QoQ/YoY changes
(Wrap in <div class="table-wrapper"> for mobile scrolling)

SECTION BREAKDOWN:
1. Financial Performance Analysis: QoQ/YoY analysis, revenue/margin trends, cost management, quality of earnings + Metrics Grid
2. Operational Excellence/Challenges: Deep dive, ROE/ROCE, balance sheet quality + Alert Box (Success/Warning/Danger)
3. Industry Context/Deep Dive: Industry analysis, competitive positioning, market trends + Comparison Table
4. Peer Comparison: Table with P/E, P/BV, ROE, Dividend Yield + narrative
5. Valuation Analysis: Current multiples, historical context, fair value + Valuation Dashboard
6. Shareholding Pattern: Last 2-3 quarters table + QoQ change interpretation
7. Stock Performance: Returns table (1W to 3Y) with Stock/Sensex/Alpha + performance analysis
8. Investment Thesis: Dashboard with Valuation, Quality Grade, Financial Trend, Technical Trend
9. Key Strengths & Concerns: Two-column layout with 5-7 points each
10. Outlook & Monitoring: POSITIVE CATALYSTS vs RED FLAGS grid

THE VERDICT: Summary characterization + rationale (2-3 sentences)

FOOTER: Investment disclaimer

### FOOTER SECTION
**Disclaimer text (standard):**
⚠️ Investment Disclaimer
This article is for educational and informational purposes only and should not be construed as financial advice. Investors should conduct their own due diligence, consider their risk tolerance and investment objectives, and consult with a qualified financial advisor before making any investment decisions.

CRITICAL: ALL TABLES must be wrapped in <div class="table-wrapper"></div> for mobile responsiveness

WRITING STYLE REMINDERS:
- Active voice, specific numbers, context for all metrics
- Paragraph structure: topic sentence → evidence → implication (4-7 sentences)
- Currency: ₹XXX crores or ₹X.XX lakh crores
- Percentages with direction symbols (▲/▼)
- Dates: "October 8, 2025" in text, "Oct'25" in tables

NARRATIVE BY RATING:
- BUY/STRONG BUY: Lead with strengths, manageable concerns, growth catalysts
- HOLD: Balanced, equal weight, focus on upgrade requirements
- SELL/STRONG SELL: Lead with concerns (factual), structural challenges, deteriorating trends

SECTOR-SPECIFIC FOCUS:
- Banks: NPA, CASA, NIMs, asset quality
- IT: Deal wins, margins, attrition, client metrics
- Manufacturing: Capacity utilization, raw material costs, operating leverage
- NBFC: AUM growth, disbursements, asset quality
- Pharma: Revenue mix, ANDA approvals, R&D

Generate the complete HTML article now. Return ONLY the HTML – no explanations, no markdown blocks, just pure HTML from <!DOCTYPE html> to </html>. Remember to wrap all content in <div class="article-news-new">."""

    def generate_article_from_data(self, stock_data_string, max_tokens=20000):
        """
        Generate news article directly from stock data string (no file needed)

        Args:
            stock_data_string (str): Stock data as string
            max_tokens (int): Maximum tokens for response

        Returns:
            tuple: (html_content, tracking_info)
        """
        start_time = time.time()

        try:
            html_content = ""
            input_tokens = 0
            output_tokens = 0
            stop_reason = ""

            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                system=self.get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": self.get_user_prompt(stock_data_string)
                    }
                ]
            ) as stream:
                for text in stream.text_stream:
                    html_content += text

                final_message = stream.get_final_message()
                input_tokens = final_message.usage.input_tokens
                output_tokens = final_message.usage.output_tokens
                stop_reason = final_message.stop_reason

            elapsed_time = time.time() - start_time
            total_tokens = input_tokens + output_tokens

            # Cost calculation
            input_cost = (input_tokens / 1_000_000) * 3.00
            output_cost = (output_tokens / 1_000_000) * 15.00
            total_cost = input_cost + output_cost

            # Clean up any markdown code blocks
            html_content = self._clean_html(html_content)

            tracking_info = {
                "api": "claude_sonnet_4.5",
                "model": self.model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6),
                "total_cost": round(total_cost, 6),
                "duration_seconds": round(elapsed_time, 2),
                "stop_reason": stop_reason,
                "generated_at": datetime.now().isoformat()
            }

            return html_content, tracking_info

        except Exception as e:
            raise Exception(f"Error generating article: {str(e)}")

    def _clean_html(self, content):
        """Remove markdown code blocks if present"""
        content = re.sub(r'^```html\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```\s*$', '', content, flags=re.MULTILINE)
        return content.strip()

    def extract_title_and_article(self, html_content):
        """
        Extract title, summary, and article content from generated HTML

        Args:
            html_content (str): Complete HTML content

        Returns:
            dict: Dictionary with 'title', 'summary', and 'article' keys
        """
        result = {
            'title': '',
            'summary': '',
            'article': ''
        }

        # Extract title from <title> tag or <h1> in article-header
        title_match = re.search(r'<title>([^<]+)</title>', html_content)
        if title_match:
            result['title'] = title_match.group(1).strip()
        else:
            # Fallback to h1 in article-header
            h1_match = re.search(r'<div class="article-header">.*?<h1>([^<]+)</h1>', html_content, re.DOTALL)
            if h1_match:
                result['title'] = h1_match.group(1).strip()

        # Extract summary from <p class="lead">
        summary_match = re.search(r'<p class="lead">([^<]+(?:<[^>]+>[^<]*</[^>]+>[^<]*)*)</p>', html_content, re.DOTALL)
        if summary_match:
            # Get the raw content with potential HTML tags
            summary_raw = summary_match.group(1)
            # Remove any HTML tags to get clean text
            summary_clean = re.sub(r'<[^>]+>', '', summary_raw)
            # Clean up whitespace
            result['summary'] = re.sub(r'\s+', ' ', summary_clean).strip()

        # Extract article content (from article-content div)
        content_start = re.search(r'<div class="article-content">', html_content)

        if content_start:
            start_pos = content_start.start()

            # Find the matching closing </div> for article-content
            div_count = 0
            pos = start_pos
            in_article_content = False
            end_pos = -1

            while pos < len(html_content):
                # Check for opening div
                if html_content[pos:pos+4] == '<div':
                    div_count += 1
                    if not in_article_content:
                        in_article_content = True

                # Check for closing div
                elif html_content[pos:pos+6] == '</div>':
                    div_count -= 1
                    if div_count == 0 and in_article_content:
                        end_pos = pos + 6
                        break

                pos += 1

            if end_pos > start_pos:
                # Extract the article-content section
                article_section = html_content[start_pos:end_pos]

                # Remove the first paragraph (<p class="lead">) from article to avoid duplication
                # This paragraph is already extracted as summary
                article_section = re.sub(r'<p class="lead">.*?</p>\s*', '', article_section, count=1, flags=re.DOTALL)

                # Wrap it in the required structure
                result['article'] = f"""    <div class="article-news-new">
        <div class="article-container">

{article_section}
        </div>
    </div>"""

        return result


# ============================================================================
# Process Result Trigger Function
# ============================================================================
def process_result_trigger(m_r_news_triggers, generator):
    """
    Process a single result trigger and generate news article

    Args:
        m_r_news_triggers (dict): News trigger document from MongoDB
        generator (StockNewsGeneratorV2): Claude news generator instance
    """
    start_time = time.time()

    # Initialize m_dict with data from trigger
    m_dict = {}

    try:
        # Extract basic trigger information
        m_dict["newsid"] = m_r_news_triggers["_id"]
        m_dict["stockid"] = m_r_news_triggers["stockid"]
        m_dict["category"] = m_r_news_triggers.get("category")
        m_dict["date"] = m_r_news_triggers["date"]
        m_dict["data"] = m_r_news_triggers["data"]
        m_dict["trigger_name"] = m_r_news_triggers["trigger_name"]

        # Company name
        m_comp_name = m_r_news_triggers.get("comp_name", "").replace(" Ltd", "").replace(" Ltd.", "")
        m_dict["comp_name"] = m_comp_name

        # Score and grade information
        m_dict["score"] = m_r_news_triggers.get("score")
        m_dict["scoreText"] = m_r_news_triggers.get("scoreText")
        m_dict["prevScoreText"] = m_r_news_triggers.get("prevScoreText")
        m_dict["scoreTxtChngDate"] = m_r_news_triggers.get("scoreTxtChngDate")

        # Result specific information
        m_dict["upcoming_result"] = m_r_news_triggers.get("upcoming_result")
        m_dict["result"] = m_r_news_triggers.get("result")
        m_dict["result_quarter"] = m_r_news_triggers.get("result_quarter")

        # Other metadata
        m_dict["country_id"] = m_r_news_triggers.get("country_id")
        m_dict["trigger_date"] = m_r_news_triggers.get("trigger_date")
        m_dict["mcap_grade"] = m_r_news_triggers.get("mcap_grade")
        m_dict["turn_arround"] = m_r_news_triggers.get("turn_arround")
        m_dict["turn_arround_entry_date"] = m_r_news_triggers.get("turn_arround_entry_date")
        m_dict["momentumnow"] = m_r_news_triggers.get("momentumnow")
        m_dict["momentumnow_entry_date"] = m_r_news_triggers.get("momentumnow_entry_date")
        m_dict["consistant_performer"] = m_r_news_triggers.get("consistant_performer")
        m_dict["consistant_performer_entry_date"] = m_r_news_triggers.get("consistant_performer_entry_date")
        m_dict["mojostocks"] = m_r_news_triggers.get("mojostocks")
        m_dict["mojostocks_entry_date"] = m_r_news_triggers.get("mojostocks_entry_date")
        m_dict["day_change"] = str(m_r_news_triggers.get("stock_1d_return", "")).replace("%", "") + "%" if m_r_news_triggers.get("stock_1d_return") else None

        # Get additional data from stock_screener
        m_filter = {"sid": m_dict["stockid"]}
        m_c_stock_screener = m_stock_screener.find(m_filter)

        m_fin_grade = None
        for m_r_stock_screener in m_c_stock_screener:
            m_dict["ind_id"] = m_r_stock_screener.get("old_ind_id")
            if "sector_id" in m_r_stock_screener:
                m_dict["sub_sect_id"] = m_r_stock_screener["sector_id"]
            else:
                m_dict["sub_sect_id"] = m_dict.get("ind_id")
            m_fin_grade = m_r_stock_screener.get("fin_grade")

        # Override with trigger data if available
        if "old_ind_id" in m_r_news_triggers:
            m_dict["ind_id"] = m_r_news_triggers["old_ind_id"]
        if "sub_sect_id" in m_r_news_triggers:
            m_dict["sub_sect_id"] = m_r_news_triggers["sub_sect_id"]

        # Exchange information
        if "bse_nse" in m_r_news_triggers:
            if m_r_news_triggers["bse_nse"] in [None]:
                m_dict["exch"] = None
            elif "bse" in m_r_news_triggers["bse_nse"]:
                m_dict["exch"] = 0
            else:
                m_dict["exch"] = 1

        # Financial grade
        if "fin_grade" in m_r_news_triggers:
            m_dict["fin_grade"] = m_r_news_triggers["fin_grade"]
        else:
            m_dict["fin_grade"] = m_fin_grade

        # Status
        m_dict["status"] = 0

        # Published date
        if "date_time_trigger" in m_r_news_triggers:
            m_dict["published"] = datetime.strptime(m_r_news_triggers["date_time_trigger"], "%Y-%m-%d %H:%M:%S")
        else:
            m_dict["published"] = datetime.now()

        # Theme based on financial grade
        m_d_fin_grade = {
            "outstanding": "green",
            "very positive": "green",
            "positive": "green",
            "flat": "orange",
            "negative": "red",
            "very negative": "red"
        }

        if m_dict["fin_grade"] and m_dict["fin_grade"].lower() in m_d_fin_grade:
            m_dict["theme"] = m_d_fin_grade[m_dict["fin_grade"].lower()]
        else:
            m_dict["theme"] = "grey"

        # Bucket and priority for result triggers
        m_dict["bucket"] = 1  # Results are typically Bucket 1
        m_dict["priority"] = 1

        print(f"\n{'='*70}")
        print(f"📊 PROCESSING RESULT TRIGGER")
        print(f"{'='*70}")
        print(f"   News ID:       {m_dict['newsid']}")
        print(f"   Stock ID:      {m_dict['stockid']}")
        print(f"   Company:       {m_comp_name}")
        print(f"   Result Date:   {m_dict.get('result', 'N/A')}")
        print(f"   Quarter:       {m_dict.get('result_quarter', 'N/A')}")
        print(f"   Score Text:    {m_dict.get('scoreText', 'N/A')}")

        # Generate article using Claude API
        print(f"\n🚀 Generating article with Claude Sonnet 4.5...")
        html_content, tracking_info = generator.generate_article_from_data(
            stock_data_string=m_dict["data"],
            max_tokens=20000
        )

        print(f"\n✅ Article generated successfully!")
        print(f"   Duration:      {tracking_info['duration_seconds']} seconds")
        print(f"   Total Cost:    ${tracking_info['total_cost']}")
        print(f"   Total Tokens:  {tracking_info['total_tokens']:,}")

        # Extract title, summary, and article components
        print(f"\n📋 Extracting components...")
        components = generator.extract_title_and_article(html_content)

        # Populate all 9 fields with SAME content (paid, unpaid, crawler)
        # IMPORTANT: Use components['article'] NOT html_content (only article section, not full HTML)
        m_dict["generated_article"] = components['article']
        m_dict["generated_article_unpaid"] = components['article']
        m_dict["generated_article_crawler"] = components['article']

        m_dict["generated_headline"] = components['title']
        m_dict["generated_headline_unpaid"] = components['title']
        m_dict["generated_headline_crawler"] = components['title']

        m_dict["generated_summary"] = components['summary']
        m_dict["generated_summary_unpaid"] = components['summary']
        m_dict["generated_summary_crawler"] = components['summary']

        # Add tracking information
        m_dict["tracking"] = tracking_info

        # Set inserted timestamp
        m_dict["inserted"] = datetime.now()

        # Validate generated content
        if (len(m_dict["generated_article"]) > 100 and
            len(m_dict["generated_summary"]) > 10 and
            len(m_dict["generated_headline"]) > 5):

            # Update news_stories collection
            m_filter = {"newsid": m_dict["newsid"]}
            m_news_stories.update_one(m_filter, {"$set": m_dict}, upsert=True)

            # Mark trigger as processed (status = 1)
            m_filter = {"_id": m_dict["newsid"]}
            m_news_triggers.update_one(m_filter, {"$set": {"status": 1}})

            print(f"\n✅ News saved to database")
            print(f"   Headline:  {components['title'][:80]}...")
            print(f"   Summary:   {components['summary'][:80]}...")
            print(f"   Article:   {len(html_content):,} characters")

        else:
            # Mark as failed if content is too short
            m_filter = {"_id": m_dict["newsid"]}
            m_news_triggers.update_one(m_filter, {"$set": {"status": 2, "error_message": "Generated content too short"}})
            print(f"\n❌ Generated content too short - marked as failed")

        end_time = time.time()
        task_duration = end_time - start_time
        print(f"\n⏱️  Total processing time: {task_duration:.2f} seconds")

    except Exception as e:
        error_msg = f"Error processing trigger: {str(e)}"
        print(f"\n❌ {error_msg}")

        # Mark trigger as failed (status = 2)
        try:
            m_filter = {"_id": m_r_news_triggers["_id"]}
            m_news_triggers.update_one(m_filter, {"$set": {"status": 2, "error_message": error_msg}})
        except:
            pass


# ============================================================================
# Main Execution Function
# ============================================================================
def get_news_data():
    """
    Main function to fetch result triggers and generate news articles
    """
    print("\n" + "="*70)
    print("🎯 STARTING NEWS GENERATION FOR RESULT TRIGGERS")
    print("="*70)

    # Initialize Claude generator
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    try:
        generator = StockNewsGeneratorV2(api_key=ANTHROPIC_API_KEY)
        print("✅ Claude Sonnet 4.5 generator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize generator: {str(e)}")
        return

    # Query news_triggers for result triggers with status = 0
    m_filter = {
        "trigger_name": ["result"],
        "status": 0,
        "date": {"$gte": "2025-10-12"},
        "country_id": 34,  # India
        "$or": [
            {"trigger_name": {"$ne": "ipo_listing"}, "scoreText": {"$nin": ["Not Rated"]}}
        ]
    }

    try:
        m_c_news_triggers = m_news_triggers.find(m_filter)
        trigger_count = m_news_triggers.count_documents(m_filter)

        print(f"\n📝 Found {trigger_count} result triggers with status=0")
        print(f"   Processing all {trigger_count} triggers...")

        processed = 0
        successful = 0
        failed = 0

        for m_r_news_triggers in m_c_news_triggers:
            processed += 1
            print(f"\n{'#'*70}")
            print(f"# Processing {processed}/{trigger_count}: Stock ID {m_r_news_triggers['stockid']}")
            print(f"{'#'*70}")

            try:
                process_result_trigger(m_r_news_triggers, generator)
                successful += 1
            except Exception as e:
                failed += 1
                print(f"❌ Failed to process trigger: {str(e)}")

        print(f"\n" + "="*70)
        print(f"🎉 PROCESSING COMPLETE")
        print(f"="*70)
        print(f"   Total Processed:  {processed}")
        print(f"   Successful:       {successful}")
        print(f"   Failed:           {failed}")

    except Exception as e:
        print(f"\n❌ Error querying triggers: {str(e)}")


# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == "__main__":
    try:
        get_news_data()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
    finally:
        print("\n" + "="*70)
        print("👋 Script execution ended")
        print("="*70)