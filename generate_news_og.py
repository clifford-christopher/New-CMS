from openai import OpenAI
from pymongo import MongoClient
from datetime import datetime
import psutil
import sys
import random
import os
from openai import AsyncOpenAI
import openai
import asyncio
import time
from datetime import datetime
import re
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Optional: To see the debug messages from your extract function, add this line:
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_script_running(script_name):
	for process in psutil.process_iter(attrs=['name']):
		if script_name in process.info['name']:
			return True
	return False

script_name = "generate_news.py"

if is_script_running(script_name):
	print(f"{script_name} is already running.")
	sys.exit()
else:
	print(f"{script_name} is not running.")
	
	
#with open('mongourl.txt', 'r') as file:
with open('mongourl_mmfrontend_prod.txt', 'r') as file:
    m_mongourl = file.read().replace('\n', '')

#MongoDB connection setup
# m_mongourl = "mongodb://35.154.169.5:27017/"
m_client = MongoClient(m_mongourl)

#select the database
m_db_mmfrontend = m_client["mmfrontend"]

m_news_triggers = m_db_mmfrontend["news_triggers"]

m_news_stories = m_db_mmfrontend["news_stories"]

m_stock_screener = m_db_mmfrontend["stock_screener"]



# Initialize the asynchronous OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def safe_request_with_retry(async_openai_client, *args, **kwargs):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            start_time = time.perf_counter()
            response = await async_openai_client.chat.completions.create(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time

            duration_rounded = round(duration, 4)

            # Instead of using .get(), we access the attribute directly.
            # If usage is None, we default to an empty object.
            usage = response.usage or {}
            prompt_tokens = usage.prompt_tokens if hasattr(usage, "prompt_tokens") else 0
            completion_tokens = usage.completion_tokens if hasattr(usage, "completion_tokens") else 0
            total_tokens = prompt_tokens + completion_tokens

            # Calculate cost for GPT-4o mini:
            # Input cost: $0.150 / 1M tokens, Output cost: $0.600 / 1M tokens
            cost = (prompt_tokens * 0.150 + completion_tokens * 0.600) / 1e6

            # Round off duration to 2 decimals and cost to 6 decimals.
            #duration_rounded = round(duration, 2)
            cost_rounded = round(cost, 6)

            print(f"OpenAI Request: duration: {duration:.2f} sec, total_cost: ${cost_rounded}")

            response.tracking = {
                "duration": duration_rounded,
                "total_cost": cost_rounded
            }
            return response
        except openai.APIConnectionError as e:
            retries += 1
            wait_time = 2 ** retries
            print(f"Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries}) - {e}")
            await asyncio.sleep(wait_time)
        except openai.RateLimitError as e:
            wait_time = 60
            print(f"Rate limit reached. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries}) - {e}")
            await asyncio.sleep(wait_time)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
    raise Exception("Max retries reached for OpenAI API call")

# --- ADD THIS NEW DICTIONARY FOR SPECIFIC PROMPTS ---

# This dictionary maps each "Stock in Action" trigger to a specific, tailored prompt.
STOCK_IN_ACTION_PROMPTS = {

    # --- Add these two new entries at the top ---
    "golden_cross": "Craft a SEO friendly news article of 150-200 words explaining that the stock has experienced a Golden Cross. Describe what this technical event signifies and its potential implication using only the provided data.",
    "dealth_cross": "Craft a SEO friendly news article of 150-200 words explaining that the stock has experienced a Death Cross. Describe what this technical event signifies and its potential implication using only the provided data.",

    "day high": "Craft a SEO friendly news article of 150-200 words focusing on the stock hitting its day's high. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources. Use an informative tone and a fact-based style based only on the provided data.",
    "day low": "Craft a SEO friendly news article of 150-200 words focusing on the stock hitting its day's low. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources. Use a neutral, informative tone and a fact-based style based only on the provided data.",
    "52wk_high": "Craft a SEO friendly news article of 150-200 words about the stock reaching its 52-week high. Highlight this significant milestone, mentioning the new high price. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources.",
    "52wk_low": "Craft a SEO friendly news article of 150-200 words about the stock touching its 52-week low. Detail this event, mentioning the new low price. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources.",
    "all_time_high": "Craft a SEO friendly news article of 150-200 words announcing that the stock has reached an all-time high. This is a major event, so emphasize the event and the company's strong performance leading to this achievement, using only the provided data. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources.",
    "all_time_low": "Craft a SEO friendly news article of 150-200 words reporting that the stock has fallen to an all-time low. Focus on this significant event,  the market context, based only on the provided data. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources.",
    "gap_up": "Craft a SEO friendly news article of 150-200 words about the stock opening with a significant gap up. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources.",
    "gap_down": "Craft a SEO friendly news article of 150-200 words about the stock opening with a significant gap down. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. If any date field is missing or shown as 'NA', ignore it and make no comment on it. Please only use the information I've provided and do not include any external data or sources."
    # "bulk_block_deal": "Craft a SEO friendly news article of 150-200 words reporting on a significant bulk or block deal in the stock. Detail the nature of the transaction if data is available (e.g., volume, price) and discuss its potential implications for the stock's ownership structure, using only the provided data.",
    # "only_buyers": "Craft a SEO friendly news article of 150-200 words explaining that the stock is locked in the upper circuit with only buyers and no sellers. Describe what this indicates about market demand and highlight its price movement for the day, based only on the provided data.",
    # "only_sellers": "Craft a SEO friendly news article of 150-200 words explaining that the stock is locked in the lower circuit with only sellers and no buyers. Describe what this indicates about market sentiment and highlight its price movement for the day, based only on the provided data."
}

# --- ADD THIS NEW DICTIONARY FOR SPECIFIC HEADLINE PROMPTS ---

# This dictionary maps each "Stock in Action" trigger to a specific headline prompt.
STOCK_IN_ACTION_HEADLINE_PROMPTS = {

    "golden_cross": "Create a headline announcing the stock has formed a Golden Cross, signaling a potential bullish breakout.",
    "dealth_cross": "Create a headline reporting that the stock has formed a Death Cross, indicating a potential bearish trend.",

    "day high": "Create a headline that focuses on the stock hitting its day high. Mention its strong intraday performance and include the company name.",
    "day low": "Create a headline that reports the stock touching its day low. Mention the price pressure and include the company name.",
    "52wk_high": "Create a headline announcing the stock has reached a new 52-week high. Highlight this key milestone and include the company name.",
    "52wk_low": "Create a headline stating the stock has fallen to its 52-week low. Focus on this significant price level and include the company name.",
    "all_time_high": "Create a powerful headline declaring that the stock has hit its all-time high. Convey the significance of this event.",
    "all_time_low": "Create a headline reporting that the stock has dropped to an all-time low. Convey the significance of this event.",
    "gap_up": "Create a headline about the stock's 'gap up' opening. Mention a strong start and positive market sentiment.",
    "gap_down": "Create a headline about the stock's 'gap down' opening. Mention a weak start and market concerns.",
    "bulk_block_deal": "Create a headline that indicates a significant bulk or block deal has occurred in the stock, suggesting notable investor activity."
    # "only_buyers": "Create a headline stating the stock is locked in the upper circuit due to strong buyer interest. Use words like 'surges' or 'rallies'.",
    # "only_sellers": "Create a headline stating the stock is locked in the lower circuit. Use words like 'plunges' or 'tumbles'."
}

# --- BEGIN IRB SPECIFIC CONSTANTS ---
IRB_STOCK_ID = 430474 # Define the specific stock ID

IRB_BOILERPLATE_TEXT = """Note : Historical numbers are not comparable for this company due to transfer of 9 assets by IRB to Private InvIT in FY20.

Pledge shareholding: IRB has provided a non-disposal undertaking (committing not to sell a certain percentage of their holding in IRB) to GIC and the Ferrovial Group."""

# Prompts for stockid == 430474 and trigger_name == 'score grade change'
IRB_UNPAID_PROMPT_SCORE_CHANGE = """Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions , using the numerical data present in the data.. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. You can use terms like 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format. Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned.

Following the main article content, please include the following exact note at the end before the link: 

Note : Historical numbers are not comparable for this company due to transfer of 9 assets by IRB to Private InvIT in FY20.\n\n

Pledge shareholding: IRB has provided a non-disposal undertaking (committing not to sell a certain percentage of their holding in IRB) to GIC and the Ferrovial Group.
  
   
Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:

<a class="stock-link" href="https://www.marketsmojo.com/mojo/professionalpack?s=buy&utm=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - Start your journey with MojoOne today!</a> """

IRB_CRAWLER_PROMPT_SCORE_CHANGE = """Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions , using the numerical data present in the data. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. You can use terms like 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format.Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned. 

Following the main article content, please include the following exact note at the end before the link: 

Note : Historical numbers are not comparable for this company due to transfer of 9 assets by IRB to Private InvIT in FY20.\n\n

Pledge shareholding: IRB has provided a non-disposal undertaking (committing not to sell a certain percentage of their holding in IRB) to GIC and the Ferrovial Group.
  

Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:
    
<a class="stock-link" href="https://www.marketsmojo.com/mojofeed/register?utm_source=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - SignUp in less than 2 Minutes and get FREE Premium Access.</a> """

# Prompts for stockid == 430474 and trigger_name == 'result'
IRB_UNPAID_PROMPT_RESULT = """Analyze the provided financial results for mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. Use terms like 'evaluation changes,' 'adjustment in evaluation,' or 'revision in its score' to acknowledge any shifts in assessment. Do not mention any specific rating (e.g., 'Buy,' 'Sell,' 'Hold') or if the rating was upgraded or downgraded in any part of the output. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format.Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned. 
        
Following the main article content, please include the following exact note at the end before the link: 

Note : Historical numbers are not comparable for this company due to transfer of 9 assets by IRB to Private InvIT in FY20.\n\n
        
Pledge shareholding: IRB has provided a non-disposal undertaking (committing not to sell a certain percentage of their holding in IRB) to GIC and the Ferrovial Group.
        
        
Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:
        
<a class="stock-link" href="https://www.marketsmojo.com/mojo/professionalpack?s=buy&utm=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - Start your journey with MojoOne today!</a> """

IRB_CRAWLER_PROMPT_RESULT = """Analyze the provided financial results for mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. Use terms like 'evaluation changes,' 'adjustment in evaluation,' or 'revision in its score' to acknowledge any shifts in assessment. Do not mention any specific rating (e.g., 'Buy,' 'Sell,' 'Hold') or if the rating was upgraded or downgraded in any part of the output. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format.  Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned.
        
Following tee main article content, please include the following exact note at the end before the link: 

Note : Historical numbers are not comparable for this company due to transfer of 9 assets by IRB to Private InvIT in FY20.\n\n
        
Pledge shareholding: IRB has provided a non-disposal undertaking (committing not to sell a certain percentage of their holding in IRB) to GIC and the Ferrovial Group.
        
        
Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:
            
<a class="stock-link" href="https://www.marketsmojo.com/mojofeed/register?utm_source=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - SignUp in less than 2 Minutes and get FREE Premium Access.</a> """
# --- END IRB SPECIFIC CONSTANTS ---


async def generate_news(stockid,m_comp_name, m_industry, m_sector, m_score, m_scoreText, m_upcoming_result, m_result, m_result_quarter, m_l_trigger_name, m_data, m_prevScoreText, m_scoreTxtChngDate, m_trigger_date, m_mcap_grade, m_turn_arround, m_turn_arround_entry_date, m_momentumnow, m_momentumnow_entry_date, m_consistant_performer, m_consistant_performer_entry_date, m_mojostocks, m_mojostocks_entry_date, m_day_change):
    global async_client
    # --- ORIGINAL LOGIC FOR ALL OTHER TRIGGERS ---

    m_d_grades = {"Strong Buy":5, "Buy":4, "Hold":3, "Sell":2, "Strong Sell":1, "Not Rated":0}
    m_d_highlow = {"52wk_high":"price has touched 52 week high", "52wk_low":"price has touched 52 week low", "52wk_high close":"price is closer to touching 52 week high", "52wk_low close":"price is closer to touching 52 week low", "day high":"has gained", "day low":"has lost", "all_time_high":"price has touched All Time High", "all_time_low":"price has touched All Time Low"}
    m_d_mcap_grade = {1:"Largecap", 2:"Midcap", 3:"Smallcap", 4:"Microcap"}
    if m_scoreText == None:
        m_scoreText = "Not Rated"
    if m_scoreText in ["Strong Buy", "Buy"]:
        m_sentiment = "positive and informative"
    elif m_scoreText in ["Strong Sell", "Sell"]:
        m_sentiment = "neutral and informative"
    else:
        m_sentiment = "neutral and informative"
    m_heading = ""
    if "result" in m_l_trigger_name:
        m_heading = "\nFinancial result for quarter " + str(m_result_quarter) + " has been declared on " + m_result
        m_heading = m_heading + "\n\nStock call is '" + m_scoreText + "' by MarketsMOJO"
        m_max_words = 200
    elif "score grade change" in m_l_trigger_name:
        # --- NEW: Add a safety check before dictionary lookup ---
        if m_scoreText in m_d_grades and m_prevScoreText in m_d_grades:
            if (m_d_grades[m_scoreText] - m_d_grades[m_prevScoreText]) > 0:
                m_gradechange = "upgraded"
            else:
                m_gradechange = "downgraded"
            
            m_heading = "\nStock call on " + m_comp_name + " has been " + m_gradechange + " from '" + m_prevScoreText + "' to '" + m_scoreText + "' by MarketsMOJO on " + m_scoreTxtChngDate
        else:
            # Fallback if the score texts are invalid or missing
            m_heading = "\nStock call on " + m_comp_name + " has been updated to '" + m_scoreText + "' by MarketsMOJO on " + m_scoreTxtChngDate
        
        m_max_words = 150

    elif m_l_trigger_name[0] in ["52wk_high", "52wk_low", "52wk_high close", "52wk_low close", "day high", "day low", "all_time_high", "all_time_low", "going_up_daily", "going_down_daily", "only_buyers", "only_sellers", "turnaround_fall", "turnaround_gain", "bulk_block_deal", "gap_up", "gap_down", "fall_from_high", "rise_from_low"]:
        if m_l_trigger_name[0] in ["day high", "day low"]:
            m_heading = "\n" + m_comp_name + " " + m_d_highlow[m_l_trigger_name[0]] + " " + m_day_change + " on " + m_trigger_date
        elif m_l_trigger_name[0] not in ["going_up_daily", "going_down_daily", "only_buyers", "only_sellers", "gap_up", "gap_down", "fall_from_high", "rise_from_low", "bulk_block_deal", "turnaround_fall", "turnaround_gain"]:
            m_heading = "\n" + m_comp_name + " " + m_d_highlow[m_l_trigger_name[0]] + " on " + m_trigger_date
        if m_scoreText not in [None, "Not Rated", ""]:
            m_heading = m_heading + "\n\nStock call is '" + m_scoreText + "' by MarketsMOJO"
        if m_turn_arround == "Yes":
            m_heading = m_heading + "\nStock is part of Hidden Turnaround on MarketsMOJO since " + m_turn_arround_entry_date
        if m_momentumnow == "Yes":
            m_heading = m_heading + "\nStock is part of Momentumnow Stocks on MarketsMOJO since " + m_momentumnow_entry_date
        if m_consistant_performer == "Yes":
            m_heading = m_heading + "\nStock is part of Reliable Performers on MarketsMOJO since " + m_consistant_performer_entry_date
        if m_mojostocks == "Yes":
            m_heading = m_heading + "\nStock is part of MOJO Stocks on MarketsMOJO since " + m_mojostocks_entry_date
        else:
            m_max_words = 150
    elif m_l_trigger_name[0] in ["multibagger"]:
        m_heading = "\nThis news is about " + m_comp_name + " being a multibagger stock, mention the same in headline "

    if "result_summary" in m_l_trigger_name:
        m_data = "\nFinancial Result summary:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words on current quarter financial result summary, Please only use the information I've provided and do not include any external data or sources: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    
    # --- ADD THIS NEW BLOCK ---
    elif "high_return_in_period" in m_l_trigger_name:
        m_data = "\nHigh Return Stock Analysis:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words analyzing this stock's high return performance. Use an informative, fact-based style. Please only use the information provided and do not include external data: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    # --- END OF NEW BLOCK ---

    
    # elif "market_summary" in m_l_trigger_name or "smallcap_market_summary" in m_l_trigger_name or "midcap_market_summary" in m_l_trigger_name or "largecap_market_summary" in m_l_trigger_name or "sector_summary" in m_l_trigger_name or  "52_week_high_summary" in m_l_trigger_name:
    #     m_data = "\nMarket summary:\\n" + m_data
    #     news_prompt = "Craft a SEO friendly news article with 150 to 200 words on whats driving the market today, Please only use the information I've provided and do not include any external data or sources: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")

    # --- THIS IS THE NEW, REFINED BLOCK FOR PAID PROMPTS ---
    elif "market_summary" in m_l_trigger_name:
        m_data = "\nMarket Summary Analysis:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words summarizing the overall market performance for the day based on the provided data. Focus on the key indices, advancing/declining stocks, and top gainers/losers. Please only use the information provided: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    
    elif "smallcap_market_summary" in m_l_trigger_name or "midcap_market_summary" in m_l_trigger_name or "largecap_market_summary" in m_l_trigger_name:
        # This prompt can handle all market-cap specific summaries
        m_data = "\nMarket Segment Summary:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words summarizing the performance of this specific market segment (e.g., small-cap, mid-cap). Focus on the key trends and top-performing stocks mentioned in the provided data: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")

    elif "sector_summary" in m_l_trigger_name:
        m_data = "\nSector Performance Summary:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words summarizing the performance of the specified market sector. Highlight the key drivers and notable stock movements within that sector from the provided data: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")

    elif "52_week_high_summary" in m_l_trigger_name:
        m_data = "\n52-Week High Summary:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words about the stocks that have recently hit their 52-week high. Focus on this key performance milestone for the stocks listed in the provided data: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    # --- END OF REFINED BLOCK ---

    elif "downgrade_summary" in m_l_trigger_name or "upgrade_summary" in m_l_trigger_name or "updated_Downgrade_summary" in m_l_trigger_name:
        m_data = "\nMOJO Stock Rating Changes summary:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words on MOJO stock rating changes, Please only use the information I've provided and do not include any external data or sources: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "tech_dot_summary" in m_l_trigger_name or "tech_upgrade_summary" in m_l_trigger_name or "tech_downgrade_summary" in m_l_trigger_name:
        m_data = "\nTechnical Indicators summary:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words on technical indicators changes to following stocks, Please only use the information I've provided and do not include any external data or sources: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "new_stock_added" in m_l_trigger_name:
        m_data = "\nNew Stock Added to MarketsMOJO:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words on following stocks, please only use the information I've provided and do not include any external data or sources: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
	##################################
    elif "index_summary" in m_l_trigger_name:
        m_data = "\nIndex Summary:\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words summarizing the current index performance. Please only use the information I've provided and do not include any external data or sources: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
	##################################
    elif "multibagger" in m_l_trigger_name:
        #m_data = "\n\A Multibagger stock giving more than 100% return in last 1 year period\n"
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with " + m_sentiment + " tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "only_buyers" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with " + m_sentiment + " tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. This stock is experiencing strong buying. Highlight any consecutive gains or price increases. Explain the stock's performance relative to the Sensex. Analyze potential contributing factors to the buying pressure based on the provided data. Include relevant price summary information, such as open gap up and intraday high. Do not speculate or offer investment advice.: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "only_sellers" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with " + m_sentiment + " tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. This stock is experiencing significant selling pressure. Emphasize the fact that the stock has only sellers today and highlight the consecutive days of losses. Explain the stock's performance relative to the Sensex. Analyze potential contributing factors to the selling pressure based on the provided data. Include relevant price summary information. Do not speculate or offer investment advice.: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "ipo_listing" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with informative and neutral tone. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Conclude with Emphasizing more on the important events from sections 'Compare Quality with peers' and 'Compare Valuation with peers'  :" + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "valuation_dot" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with informative and neutral tone. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Conclude with Emphasizing more on the important events from peer comparison section:" + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "quality_dot" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with informative and neutral tone. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Conclude with Emphasizing more on the important events from peer comparison section:" + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "fintrend_dot" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with informative and neutral tone. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Discuss the mentioned Financial Trend changes for the company and talk about what is working/not working for the company. Conclude with Emphasizing more on the important events from 'Return of company with comparision of sensex' section:" + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "technical_dot" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO friendly news article with 150 to 200 words with informative and neutral tone. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Discuss the mentioned Technical Trend changes for the company and the details of the company. Talk in detail about Technical Sumamry mentioned in detail and Conclude with Emphasizing more on the important events from 'Return of company with comparision of sensex' section:" + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "stocks_hitting_upper_circuit" in m_l_trigger_name :
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = " Do not generate the response in markdown format. " + \
        "Craft a SEO-friendly news article with 150 to 200 words in an informative and neutral tone. Do not discuss future potential, mention investor interest or experts, or give any recommendations. Use only the information I've provided, and do not include external data or sources. Incorporate all available data points from the context while creating news article, including last traded price, change (Absolute change), price band (noted as percentage), intraday high and low, total traded volume, turnover, the 'Price summary' details, respective 1D returns, and company information. Important: 'priceBand' denotes a percentage, not an absolute currency value. Emphasize more on the highPrice and not ltp. The main story is that the stock hit its upper circuit limit mentioning its highPrice. Please omit any data implying a negative price change or a new 52-week low if it conflicts with the upper circuit narrative. Follow a proper good news article structure. Wrap up with a neutral final observation, restating the overall performance without making predictions or offering recommendations. Present the final output in plain text, maintaining a fact-based journalistic style.: "  + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "stocks_hitting_lower_circuit" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = " Do not generate the response in markdown format. " + \
        "Craft a SEO-friendly news article with 150 to 200 words in an informative and neutral tone. Do not discuss future potential, mention investor interest or experts, or give any recommendations. Use only the information I've provided, and do not include external data or sources. Incorporate all available data points from the context while creating news article, including last traded price, change (Absolute change), price band (noted as percentage), intraday high and low, total traded volume, turnover, the 'Price summary' details, respective 1D returns, and company information. Important: 'priceBand' denotes a percentage, not an absolute currency value. Emphasize more on the lowPrice and not ltp. The main story is that the stock hit its lower circuit limit mentioning its lowPrice. Please omit any data implying a positive price change or a new 52-week high if it conflicts with the lower circuit narrative. Follow a proper good news article structure. Wrap up with a neutral final observation, restating the overall performance without making predictions or offering recommendations. Present the final output in plain text, maintaining a fact-based journalistic style.: "  + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "most_active_equities_by_volume" in m_l_trigger_name or "most_active_equities_by_value" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = "Craft a SEO-friendly news article with 150 to 200 words in an informative and neutral tone. Do not discuss future potential, mention investor interest or experts, or give any recommendations. Use only the information I've provided, and do not include external data or sources. Incorporate each and every important available data points from the context while creating news article. Your article MUST reference these data points in meaningful way if they appear in the context. Follow a proper good news article structure. Wrap up with a neutral final observation, restating the overall performance without making predictions or offering recommendations. Present the final output in plain text, maintaining a fact-based journalistic style.: " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "most_active_stocks_calls" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = " Do not generate the response in markdown format. " + \
        "Craft a SEO friendly news article about 'One of the Most active stock calls' with 150 to 200 words with informative and neutral tone. Present a well-structured narrative that uses ALL provided data points carefully and accurately. Incorporate key details including the underlying stock, expiry dates, option types, strike prices, number of contracts traded, turnover, open interest, and underlying value. Additionally, integrate the price summary and performance metrics (such as the performance comparison, trend reversal, opening gap, intraday high, and moving averages) to create a coherent story. Do not include external data, future potential, investor interest, expert opinions, or recommendations.Do NOT discuss future potential, investor sentiment, expert views, or give any advice/recommendation. Use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Keep the language professional, objective, and coherent so that it reads like a succinct financial news piece. Follow a proper good news article structure. Wrap up with a neutral final observation, mentioning the core of the story without making predictions or offering recommendations.  :"  + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "most_active_stocks_puts" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = " Do not generate the response in markdown format. " + \
        "Craft a SEO friendly news article about 'One of the Most active stock Puts' with 150 to 200 words with informative and neutral tone. Present a well-structured narrative that uses ALL provided data points carefully and accurately. Incorporate key details if available in the provided data such as the underlying stock , expiry date , option type (Put), strike prices, number of contracts traded, turnover , open interest, and underlying value. In addition, integrate the price summary information Performance Today, Trend Reversal, Open Gap Up, Day's High, Weighted Average Price, Moving Averages, Falling Investor Participation, Liquidity and include the one-day return figures and company details to create a coherent story. Do not include external data, future potential, investor interest, expert opinions, or recommendations. Do NOT discuss future potential, investor sentiment, expert views, or give any advice/recommendation. Use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Keep the language professional, objective, and coherent so that it reads like a succinct financial news piece. Follow a proper good news article structure. Wrap up with a neutral final observation, mentioning the core of the story without making predictions or offering recommendations.  :"  + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    elif "oi_spurts_by_underlying" in m_l_trigger_name:
        m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
        news_prompt = " Do not generate the response in markdown format. " + \
        "Craft a SEO friendly news article with 150 to 200 words with informative and neutral tone. This news focuses on a notable spurt in open interest (OI) for the given stock. Highlight the latest OI, previous OI, the change in OI, and the volume details. Include relevant price summary information, but do not speculate on future price movements . Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style, Please only use the information I've provided and do not include any external data or sources. Make a proper use of all the data points mentioned in the provided data. Keep the language professional, objective, and coherent so that it reads like a succinct financial news piece. Follow a proper good news article structure. Wrap up with a neutral final observation, mentioning the core of the story without making predictions or offering recommendations.  :"  + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    else:
        # THIS IS THE CORRECTED FALLBACK BLOCK

        # --- MODIFIED LINE WITH .get() FOR SAFETY ---
        full_data_context = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade.get(m_mcap_grade, ' ') + "\n" + m_heading + "\\n" + m_data

        
        # **FIX:** Clean the data string *before* using it in the f-string
        cleaned_data_context = full_data_context.replace('\\n', '\n').replace('\\t', '\t').replace('"', "'")

        # Get the current trigger name
        # trigger_key = m_l_trigger_name[0] if m_l_trigger_name else None

        # --- START OF FIX ---
        # This logic handles cases where the trigger name is a list (like ['day high'])
        # or a string (like 'high_return_in_period').
        if isinstance(m_l_trigger_name, list):
            trigger_key = m_l_trigger_name[0] if m_l_trigger_name else None
        else:
            trigger_key = m_l_trigger_name
        # --- END OF FIX ---

        

        # --- LOGIC: Check for a specific prompt in our dictionary ---
        if trigger_key in STOCK_IN_ACTION_PROMPTS:
            print(f"INFO: Found a specific prompt for trigger: '{trigger_key}'")
            # Use the specific prompt from the dictionary
            specific_prompt = STOCK_IN_ACTION_PROMPTS[trigger_key]
            news_prompt = (f"{specific_prompt} Please only use the information I've provided "
                            f"and do not include any external data or sources: "
                            f"{cleaned_data_context}") # Use the cleaned variable here
        else:
            # --- FALLBACK: If no specific prompt is found, use the original generic prompt ---
            print(f"INFO: No specific prompt for '{trigger_key}'. Using generic prompt.")
            news_prompt = ("Craft a SEO friendly news article with 150 to 200 words with " + m_sentiment + " tone, "
                            "don't talk about future potential, don't mention investor interest or experts, no recommendation, "
                            "use fact based style, avoid harsh or overly negative terms. Do not use the phrase 'operational challenges'. "
                            "If any date field is missing or shown as 'NA', ignore it and make no comment on it. "
                            "Please only use the information I've provided and do not include any external data or sources: "
                            f"{cleaned_data_context}") # Use the cleaned variable here


    print("PROMPT")
    print(news_prompt)
    print("")

    '''
	news_prompt = """
	Craft a news article using following content: 
	Company Name: Syngene International Ltd
	Industry : Pharma
	Sector :Concept
	Syngene International Ltd stock price has volatile intraday
	Return Summary:
	Stock Return:
	1 YEAR RETURN: 20.49% (Decreased by 20.49%)
	Sensex Return:
	OUTPERFORMED BY 9.27: 11.22% (Sensex gained 11.22%)
	Sector Return:
	UNDERPERFORMED BY -6.42: 26.91% (Sector gained 26.91%)

	Dividend Yield 0.16%: latest dividend: 0.7 per share ex-dividend date: Jun-30-2023
	Medium Risk Medium Return: Syngene Intl. has given Medium returns per unit of risk v/s SENSEX during 1 Year period
	Low Beta Stock: Syngene Intl. has a beta(adjusted beta) of 0.51 with Sensex
	1 week Performance: -3.66%
	1 month Performance: 1.15%
	YTD Performance: 23.27%

	Technical Grade turned  Mildly Bullish from Bullish on 03 Oct 2023 at Rs 811.20

	It's a Good quality company basis long term financial performance.
	Ranks 11th out of 157 companies in Pharma sector
	Management Risk: Good (Positive)
	Growth: Below Average (Negative)
	Capital Structure: Excellent (Positive)

	Stock Call: Hold with a Score of 64
	Company has a low Debt to Equity ratio (avg) at 0 timesPoor long term growth as Operating profit has grown by an annual rate 11.95% of over the last 5 years
	Positive results in Sep 23
	-OPERATING CF(Y) Highest at Rs 823.50 Cr
	-NET SALES(HY) At Rs 1,718.20 cr has Grown at 21.63 %
	-PAT(HY) At Rs 215.62 cr has Grown at 22.58 %
	Stock is technically in a Mildly Bullish range
	-The stocks MACD and KST technical factors are also Bullish
	With ROE of 12.8, it has a Very Expensive valuation with a 8 Price to Book Value
	-The stock is trading at a fair value compared to its average historical valuations
	-Over the past year, while the stock has generated a return of 20.49%, its profits have risen by 17.8% ; the PEG ratio of the company is 3.3
	High Institutional Holdings at 35.27%
	-These investors have better capability and resources to analyse fundamentals of companies than most retail investors.
	-Their stake has increased by 0.88% over the previous quarter.
	"""
	'''
    '''
    Craft a news article under 1000 words using following content: 
	Moschip Technologies Ltd from IT - Software industry regarding price volatility
	 
	Moschip Technologies Ltd stock price has volatile intraday price movement
	Stock Return: 1 YEAR RETURN 33.08%  
	OUTPERFORMED BY 21.86%, Sensex return 11.22%
	OUTPERFORMED BY 27.19, Sector Return 5.89%
	 
	Dividend Yield 0%: latest dividend: 0.2 per share ex-dividend date: Aug-31-2017
	High Risk High Return: Moschip Tech. has given Higher returns per unit of risk v/s SENSEX during 1 Year period
	High Beta Stock: Moschip Tech. has a beta(adjusted beta) of 1.35 with Sensex
	 
	1 week Performance -1.33%
	1 month Performance 2.17%
	YTD Performance 31.13%
	"""
	'''
    '''
    Craft a news article using the provided content about Alkyl Amines Chemicals Ltd quarterly financial result and recent price movement and ensure that you seamlessly incorporate the following SEO keywords: Alkyl Amines Chemicals Ltd, quarterly result, financial trend, 52 week low, price movement, underperformance

	Alkyl Amines is 1% away from 52 week low.
	1 YEAR RETURN -24%
	UNDERPERFORMED BY -33.82%, SENSEX 9.54%
	UNDERPERFORMED BY -28.79%, SECTOR 4.51%
	Dividend Yield 0.46%  - latest dividend: 10 per share ex-dividend date: Jul-04-2023
	Medium Risk Low Return  - Alkyl Amines has given Lower returns per unit of risk v/s SENSEX during 1 Year period
	High Beta Stock  - Alkyl Amines has a beta(adjusted beta) of 1.20 with Sensex 
	1 week return -0.57%
	1 month return -1.27%
	3 months return -14.64%
	6 months return -12.33%
	1 year return -24.28%

	  
	Alkyl Amines has seen Negative financial performance of the quarter Sep 2023. The score has fallen to -17 from -5 in the last 3 months.
	 
	Here's what is working for Alkyl Amines based on Sep 2023 financials.
	Dividend per Share (DPS) - Annually: Highest at Rs 10.00 in the last five years.Company is distributing higher dividend from profits generated.
	 
	Here's what is not working for Alkyl Amines based on Sep 2023 financials.
	Profit Before Tax less Other Income (PBT) - Quarterly: At Rs 34.08 cr has Fallen at -46.0 % over average PBT of the previous four quarters of Rs 63.06 Cr.Near term PBT trend is very negative.
	Profit After Tax (PAT) - Quarterly: At Rs 27.24 cr has Fallen at -44.6 % over average PAT of the previous four quarters of Rs 49.13 Cr.Near term PAT trend is very negative.
	Net Sales - Quarterly: At Rs 352.15 cr has Fallen at -13.0 % over average Net Sales of the previous four quarters of Rs 404.65 Cr.Near term sales trend is very negative.
	Net Sales - Quarterly: Lowest at Rs 352.15 cr in the last five quarters.Near term sales trend is negative.
	Operating Profit (PBDIT) - Quarterly: Lowest at Rs 48.28 cr. in the last five quarters.Near term Operating Profit trend is negative.
	Operating Profit Margin - Quarterly: Lowest at 13.71% in the last five quarters.Company's efficiency has deteriorated.
	Profit Before Tax less Other Income (PBT) - Quarterly: Lowest at Rs 34.08 cr. in the last five quarters.Near term PBT trend is negative.
	Earnings per Share (EPS) - Quarterly: Lowest at Rs 5.33 in the last five quarters.Declining profitability; company has created lower earnings for shareholders.
	"""
	'''
    '''

    Craft a news article using the provided content about Jindal Poly Films Ltd quarterly financial result and ensure that you seamlessly incorporate the following SEO keywords: Jindal Poly Films Ltd, quarterly result, financial trend

	Jindal Poly Film has seen Negative financial performance of the quarter Sep 2023. The score has improved to -17 from -28 in the last 3 months.
	 
	Here's what is working for Jindal Poly Film based on Sep 2023 financials.
	Dividend Payout Ratio (DPR) - Annually: Highest at 5.90 % and Growneach year in the last five years.Company is distributing higher proportion of profits generated as dividend.
	 
	Here's what is not working for Jindal Poly Film based on Sep 2023 financials.
	Profit After Tax (PAT) - Quarterly: At Rs 12.18 cr has Fallen at -85.2 % over average PAT of the previous four quarters of Rs 82.12 Cr.Near term PAT trend is very negative.
	Operating Cash Flow - Annually: Lowest at Rs -565.53 Cr and Falleneach year in the last three years.The company's  cash revenues from business operations are falling.
	Net Sales - Half Yearly: At Rs 1,865.25 cr has Grown at -37.96 % Year on Year (YoY).Near term sales trend is negative.
	Non Operating Income - Quarterly: is 381.90 % of Profit Before Tax (PBT) .The company's income from non business activities is high; which is not a sustainable business model.
	"""
	'''
    '''
    Craft a news article using the provided content about Kalyan Jewellers India Ltd quarterly financial result and ensure that you seamlessly incorporate the following SEO keywords: Kalyan Jewellers India Ltd, quarterly result, financial trend

	Kalyan Jewellers has seen Positive financial performance of the quarter Sep 2023. The financial trend score has improved to 14 from 10 in the last 3 months.
	 
	Here's what is working for Kalyan Jewellers based on Sep 2023 financials.
	Profit After Tax (PAT) - Half Yearly: At Rs 279.14 cr has Grown at 30.24 % Year on Year (YoY).Near term PAT trend is positive.
	Debt-Equity Ratio - Half Yearly: Lowest at 0.65 times and Falleneach half year in the last five half yearly periods.The company has been reducing its borrowing as compared to equity capital.
	Operating Cash Flow - Annually: Highest at Rs 714.60 Cr in the last three years.The company has generated higher cash revenues from business operations.
	Net Sales - Quarterly: Highest at Rs 4,414.54 cr in the last five quarters.Near term sales trend is  positive.
	 
	Here's what is not working for Kalyan Jewellers based on Sep 2023 financials.
	Debtors Turnover Ratio- Half Yearly: Lowest at 41.86 times in the last five half yearly periods.Company's pace of settling its Debtors has slowed.
	"""
	'''
    '''
    Craft a news article using the provided content about recent performance of Honda India Power Products stock and ensure that you seamlessly incorporate the following SEO keywords:
	Honda India Power Products, Electric Equipment Industry, Stock Analysis, Stock Performance, Investment Risks
	1 year return -7.14%
	Underperformed by -13.46%, Sensex 6.32%
	Underperformed by -63.71%, sector 56.57%
	Dividend yield 0.67%, - latest dividend: 16.5 per share ex-dividend date: Aug-03-2023
	High risk low return, - Honda India has given Lower returns per unit of risk v/s SENSEX during 1 Year period
	Medium beta stock, - Honda India has a beta(adjusted beta) of 1.03 with Sensex
	1 week return -3.76%
	1 month return -15.22%
	3 months return -6.05%
	6 months return 7.80%
	1 year return -7.14%
	"""
	'''

    # -----------------------------------------------------
	########## ARTICLE SECTION ##########
    # -----------------------------------------------------

    # Define the list of triggers for the specialized prompt
    stock_in_action_triggers = [
        '52wk_high', '52wk_high close', '52wk_low', '52wk_low close',
        'all_time_high', 'all_time_low', 'bulk_block_deal', 'day high',
        'day low', 'fall_from_high', 'gap_down', 'gap_up',
        'going_down_daily', 'going_up_daily', 'only_buyers', 'only_sellers',
        'rise_from_low', 'turnaround_fall', 'turnaround_gain', 'fall_from_peak', 'nifty_50_stock', 'dealth_cross','golden_cross','ipo_listing','quality_dot','valuation_dot','fintrend_dot','technical_dot', 'stocks_hitting_lower_circuit', 'stocks_hitting_upper_circuit', "most_active_equities_by_volume", "most_active_equities_by_value", 'most_active_stocks_calls','most_active_stocks_puts','oi_spurts_by_underlying'
    ]

    # --- ADD THIS NEW EXCLUSION LIST ---
    HEADLINE_REUSE_EXCLUSIONS = ["valuation_dot", "quality_dot", "technical_dot", "fintrend_dot"]


    #PAID MAIN PROMPT
    news_prompt = " Do not generate the response in markdown format. " + news_prompt


    messages = [
            {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
            {"role": "user", "content": f"{news_prompt}"}
        ]
    news_response = await safe_request_with_retry(async_client,
		#model = "gpt-3.5-turbo",
		#engine="text-davinci-003",  # You can use another engine if needed
		model="gpt-4o-mini", #gpt-3.5-turbo-instruct-0914",
		messages=messages,
		max_tokens=2000,  # You can adjust this based on the desired length of the generated content
		temperature= 0.1, #random.uniform(0.1, 0.3),  # You can adjust this for more creative or more focused outputs
	)
    tracking_article = news_response.tracking
    generated_article = news_response.choices[0].message.content.strip()
    # generated_article = generated_article.replace("Reliance Industries - 18th Jan 2024", "")
    print("ARTICLE")
    print(generated_article)
    #print(news_response)
	
	#UNPAID MAIN PROMPT	
    m_unpaid_user_prompt_base = "The focus should be on the underlying trends or events. DO NOT mention any call or give any investment advice. Do not mention any specific rating (e.g., 'Buy','Sell','Hold')  or if the rating was upgraded or downgraded in any part of the output.  Make it sound like a teaser with enough details to make it interesting but without revealing the full context to identify the stock. Use an informative and fact-based style and write it like a teaser. Do not generate response in markdown format."
	
    m_unpaid_user_prompt = m_unpaid_user_prompt_base  # Default prompt

	#FOR CRAWLER

	#CRAWLER MAIN PROMPT
    m_google_crawler_prompt_base = "Given the following stock analysis data, generate a news article which include the stock name in it that reports without revealing the specific strategy list , number/percentage details , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. You can use terms like 'call changes,' 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating (e.g., 'Buy','Sell','Hold')  or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Do not generate the response in markdown format. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput. Use informative tone with fact based style."

    m_google_crawler_prompt = m_google_crawler_prompt_base # Default crawler prompt

    if any(trigger in m_l_trigger_name for trigger in stock_in_action_triggers):#### Stock In Action ####
        if 'only_buyers' in m_l_trigger_name:
            m_unpaid_user_prompt = "This stock is experiencing strong buying. Highlight any consecutive gains or price increases. Explain the stock's performance relative to the Sensex. Analyze potential contributing factors to the buying pressure based on the provided data. Include relevant price summary information, such as open gap up and intraday high. Do not speculate or offer investment advice. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on unusually high buyer activity. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format."
            m_google_crawler_prompt = "This stock is experiencing strong buying. Highlight any consecutive gains or price increases. Explain the stock's performance relative to the Sensex. Analyze potential contributing factors to the buying pressure based on the provided data. Include relevant price summary information, such as open gap up and intraday high. Do not speculate or offer investment advice. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on unusually high buyer activity. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format."
        elif 'only_sellers' in m_l_trigger_name:
            m_unpaid_user_prompt = "This stock is experiencing significant selling pressure. Emphasize the fact that the stock has only sellers today and highlight the consecutive days of losses. Explain the stock's performance relative to the Sensex.  Analyze potential contributing factors to the selling pressure based on the provided data. Include relevant price summary information. Do not speculate or offer investment advice. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on unusually high seller activity. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format."
            m_google_crawler_prompt = "This stock is experiencing significant selling pressure. Emphasize the fact that the stock has only sellers today and highlight the consecutive days of losses. Explain the stock's performance relative to the Sensex.  Analyze potential contributing factors to the selling pressure based on the provided data. Include relevant price summary information. Do not speculate or offer investment advice.The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on unusually high seller activity. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format."
        elif 'valuation_dot' in m_l_trigger_name:
            m_unpaid_user_prompt = "Important: If the context mentions a change from one specific grade to another (like 'fair to expensive'), do NOT mention the old or new grade or the direction of the change.Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or grade in a generic way (e.g., 'evaluation adjustment', 'revision in its score'). Do not reveal any specific vauation trend grades (e.g., 'Very Expensive','Expensive','Fair','Attractive','Very Attractive') or the direction (e.g. 'upgraded', 'downgraded', 'fair to expensive'). Do NOT state or repeat old/new valuation labels from the data. Refer only to a 'valuation adjustment' or 'evaluation revision' in generic terms. Also do NOT mention peer valuation categories (like 'very expensive' or 'risky') instead discuss how the peer compared without revealing those labels valuation grdaes for company and its peers also.Focus on key financial metrics, market position, and performance indicators. Do not include mention of analyst calls or recommendations. Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally.Do not generate the response in markdown format."
            m_google_crawler_prompt = "Important: If the context mentions a change from one specific grade to another (like 'fair to expensive'), do NOT mention the old or new grade or the direction of the change. Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or grade in a generic way (e.g., 'evaluation adjustment,' 'revision in its score'). Do not reveal any specific vauation trend grades (e.g. 'Very Expensive','Expensive','Fair','Attractive','Very Attractive') or the direction (e.g. 'upgraded', 'downgraded', 'fair to expensive'). Do NOT state or repeat old/new valuation labels from the data. Refer only to a 'valuation adjustment' or 'evaluation revision' in generic terms. Also do NOT mention peer valuation categories (like 'very expensive' or 'risky') instead discuss how the peer compared without revealing those labels valuation grdaes for company and its peers also. Focus on key financial metrics, market position, and performance indicators. Do not include mention of analyst calls or recommendations. Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally. Do not generate the response in markdown format."
        elif 'quality_dot' in m_l_trigger_name:
            m_unpaid_user_prompt = "Important: If the context mentions a change from one specific grade to another (like 'Below Average to Good'), do NOT mention the old or new grade or the direction of the change. Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or grade in a generic way (e.g., 'evaluation adjustment', 'revision in its score').Do not reveal any specific quality trend grades (e.g., 'Below Average','Average','Good','Excellent') or the direction (e.g. 'upgraded', 'downgraded', 'Good to Excellent'). Do NOT state or repeat old/new quality labels from the data. Refer only to a 'Quality adjustment' or 'evaluation revision' in generic terms. Also do NOT mention peer quality categories (like 'Below Average','Average','Good','Excellent') instead discuss how the peer compared without revealing those labels quality grdaes for company and its peers also. Focus on key financial metrics, market position, and performance indicators.Do not include mention of analyst calls or recommendations. Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally.Do not generate the response in markdown format."
            m_google_crawler_prompt = "Important: If the context mentions a change from one specific grade to another (like 'Below Average to Good'), do NOT mention the old or new grade or the direction of the change.Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or grade in a generic way (e.g., 'evaluation adjustment,' 'revision in its score').Do not reveal any specific quality trend grades (e.g., 'Below Average','Average','Good','Excellent') or the direction (e.g. 'upgraded' 'downgraded' 'Good to Excellent').Do NOT state or repeat old/new quality labels from the data. Refer only to a 'Quality adjustment' or 'evaluation revision' in generic terms.Also do NOT mention peer quality categories (like 'Below Average','Average','Good','Excellent') instead discuss how the peer compared without revealing those labels quality grdaes for company and its peers also.Focus on key financial metrics, market position, and performance indicators. Do not include mention of analyst calls or recommendations.Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally.Do not generate the response in markdown format."
        elif 'fintrend_dot' in m_l_trigger_name:
            m_unpaid_user_prompt = "Important: If the context mentions a change from one specific grade to another (like 'Very Negative to Flat'), do NOT mention the old or new grade or the direction of the change. Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or grade in a generic way (e.g., 'evaluation adjustment', 'revision in its score').Do not reveal any specific CFT Financial trend grades (e.g., 'Very Negative', 'Negative', 'Flat', 'Positive', 'Very Positive', 'Outstanding') or the direction (e.g. 'upgraded', 'downgraded', 'Improved'). Do NOT state or repeat old/new CFT Financial labels from the data. Refer only to a 'Financial trend adjustment' or 'evaluation revision' in generic terms. Focus on key financial metrics, market position, and performance indicators.Do not include mention of analyst calls or recommendations. Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally.Do not generate the response in markdown format."
            m_google_crawler_prompt = "Important: If the context mentions a change from one specific grade to another (like 'Very Negative to Flat'), do NOT mention the old or new grade or the direction of the change. Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or grade in a generic way (e.g., 'evaluation adjustment', 'revision in its score').Do not reveal any specific CFT Financial trend grades (e.g., 'Very Negative', 'Negative', 'Flat', 'Positive', 'Very Positive', 'Outstanding') or the direction (e.g. 'upgraded', 'downgraded', 'Improved'). Do NOT state or repeat old/new CFT Financial labels from the data. Refer only to a 'Financial trend adjustment' or 'evaluation revision' in generic terms. Focus on key financial metrics, market position, and performance indicators.Do not include mention of analyst calls or recommendations. Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally.Do not generate the response in markdown format."
        elif 'technical_dot' in m_l_trigger_name:
            m_unpaid_user_prompt = "Important: If the context mentions a change from one specific grade to another (like 'Bearish to Sideways'), do NOT mention the old or new grade or the direction of the change. Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or trend in a generic way (e.g., 'evaluation adjustment', 'revision in its score').Do not reveal any specific Technical Trend (e.g., Bearish, Mildly Bearish, Sideways, Mildly Bullish, Bullish ) or the direction (e.g. 'upgraded', 'downgraded', 'Improved'). Do NOT state or repeat old/new Technical Trend labels from the data. Refer only to a 'Technical Trend adjustment' or 'evaluation revision' in generic terms. Focus on key financial metrics, market position, and performance indicators.Do not include mention of analyst calls or recommendations. Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally.Do not generate the response in markdown format."
            m_google_crawler_prompt = "Important: If the context mentions a change from one specific grade to another (like 'Bearish to Sideways'), do NOT mention the old or new grade or the direction of the change. Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative, including the stock name in the article that reports on any changes to the stock's score or trend in a generic way (e.g., 'evaluation adjustment', 'revision in its score').Do not reveal any specific Technical Trend (e.g., Bearish, Mildly Bearish, Sideways, Mildly Bullish, Bullish ) or the direction (e.g. 'upgraded', 'downgraded', 'Improved'). Do NOT state or repeat old/new Technical Trend labels from the data. Refer only to a 'Technical Trend adjustment' or 'evaluation revision' in generic terms. Focus on key financial metrics, market position, and performance indicators.Do not include mention of analyst calls or recommendations. Do not use words like 'increased' 'decreased' or 'improved' when describing metrics just state the data neutrally.Do not generate the response in markdown format."
        else:
            m_unpaid_user_prompt = "A stock has demonstrated notable activity today. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format."
            m_google_crawler_prompt = "A stock has demonstrated notable activity today. The focus should be on the underlying trends or events, without making price predictions , using the numerical data present in the data. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format."
    elif 'score grade change' in m_l_trigger_name:#### Call Changes ####
        if stockid == IRB_STOCK_ID: # Check for IRB stock
            m_unpaid_user_prompt = IRB_UNPAID_PROMPT_SCORE_CHANGE
            m_google_crawler_prompt = IRB_CRAWLER_PROMPT_SCORE_CHANGE
        else:
            m_unpaid_user_prompt = """Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. You can use terms like 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format. Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned. Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:
            
            <a class="stock-link" href="https://www.marketsmojo.com/mojo/professionalpack?s=buy&utm=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - Start your journey with MojoOne today!</a> """
            m_google_crawler_prompt = """Discuss a recent evaluation adjustment on the mentioned stock. The focus should be on the underlying trends or events, without making price predictions , using the numerical data present in the data.. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. You can use terms like 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating (e.g., 'Buy','Sell','Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format.Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned. Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:
            
            <a class="stock-link" href="https://www.marketsmojo.com/mojofeed/register?utm_source=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - SignUp in less than 2 Minutes and get FREE Premium Access.</a> """
    elif 'result' in m_l_trigger_name:#### result ####
        if stockid == IRB_STOCK_ID: # Check for IRB stock
            m_unpaid_user_prompt = IRB_UNPAID_PROMPT_RESULT
            m_google_crawler_prompt = IRB_CRAWLER_PROMPT_RESULT
        else:
            m_unpaid_user_prompt = """Analyze the provided financial results for mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Avoid using harsh or overly negative tone. Do not use the phrase 'operational challenges'. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. Use terms like 'evaluation changes,' 'adjustment in evaluation,' or 'revision in its score' to acknowledge any shifts in assessment. Do not mention any specific rating (e.g., 'Buy,' 'Sell,' 'Hold') or if the rating was upgraded or downgraded in any part of the output. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format. Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned. Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:
            
            <a class="stock-link" href="https://www.marketsmojo.com/mojo/professionalpack?s=buy&utm=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - Start your journey with MojoOne today!</a> """
            m_google_crawler_prompt = """Analyze the provided financial results for mentioned stock. The focus should be on the underlying trends or events, without making price predictions. Avoid using harsh or overly negative tone. Do not use the phrase 'operational challenges'. Keep it brief and informative which include the stock name in it that reports on any changes to the stock's score or grade, without revealing any specific financial trend grades , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. Use terms like 'evaluation changes,' 'adjustment in evaluation,' or 'revision in its score' to acknowledge any shifts in assessment. Do not mention any specific rating (e.g., 'Buy,' 'Sell,' 'Hold') or if the rating was upgraded or downgraded in any part of the output. Crucially, do not include any mention of analyst ratings/recommendations or calls. Do not generate response in markdown format.  Avoid using terms like 'increased,' 'decreased,' 'improved,' 'deteriorated,' 'flat performance,' etc. when describing financial metrics. Instead, describe what the data shows for each period using neutral language. The article should strictly not talk about financial performance and score changes if mentioned. Conclude the article with the following text, where the entire sentence is hyperlinked with the provided URL:
            
            <a class="stock-link" href="https://www.marketsmojo.com/mojofeed/register?utm_source=MM_NewsPage_LastLine">Discover the Latest Mojo Score and Financial Trend Performance - SignUp in less than 2 Minutes and get FREE Premium Access.</a> """

# --- THIS IS THE NEW, HIGH-QUALITY PROMPT BLOCK ---
    elif 'high_return_in_period' in m_l_trigger_name:
        # This advanced prompt gives the AI a specific role and clear, positive instructions 
        # on what to include, which is more effective than only telling it what to exclude.
        
        base_prompt_instruction = """
You are a financial news writer creating an article for a public audience. Your task is to report on the top-performing stocks from the provided data.
Your article MUST focus ONLY on the following details for each stock:
- Company Name
- Sector or Industry
- Market Capitalization size (e.g., small-cap, mid-cap)
- The specific percentage return achieved

It is a strict editorial policy that you MUST OMIT all other metrics. Under NO circumstances should your article mention:
- Any numerical 'score'
- Any descriptive 'grades' or subjective ratings (e.g., 'Buy,' 'Sell,' 'Hold', "Strong Buy", "Strong Sell" )
- Any analyst recommendations or calls.

Write a professional news article using ONLY the allowed information points.
"""

        # List of specific investment grades to look for.
        grades_to_check = ['Strong Sell', 'Strong Buy', 'Buy', 'Sell', 'Hold']
        
        # Create a robust regex pattern for the grades. \b ensures we match whole words only.
        grades_pattern = r'\b(' + '|'.join(grades_to_check) + r')\b'

        # STEP 2: Filter the data line by line.
        
        # Split the original data into individual lines.
        original_lines = m_data.split('\n')
        sanitized_lines = [] # This list will hold the lines we want to keep.

        for line in original_lines:
            # We check each line for two conditions:
            # 1. Does it contain the word "score"? (case-insensitive)
            has_score = re.search(r'\bscore\b', line, re.IGNORECASE)
            # 2. Does it contain one of the investment grades? (case-insensitive)
            has_grade = re.search(grades_pattern, line, re.IGNORECASE)

            # KEEP the line ONLY if it does NOT contain BOTH score and grade.
            if not (has_score and has_grade):
                sanitized_lines.append(line)

        # Join the "clean" lines back into a single block of text.
        sanitized_data = '\n'.join(sanitized_lines)

        print("final sanitized data:\n", sanitized_data)

        # We use the same strong instruction for both unpaid and crawler, just changing the final formatting request.
        m_unpaid_user_prompt = base_prompt_instruction + " Do not generate the response in markdown format. Here is the data:\n" + sanitized_data
        m_google_crawler_prompt = base_prompt_instruction + " Do not generate the response in markdown format. Here is the data:\n" + sanitized_data
    # --- END OF NEW BLOCK ---

    # --- THIS IS THE FINAL, ROBUST SOLUTION BLOCK FOR ALL SUMMARIES ---
    elif any(trigger in m_l_trigger_name for trigger in ["market_summary", "smallcap_market_summary", "midcap_market_summary", "largecap_market_summary", "sector_summary", "52_week_high_summary"]):
        
        # STEP 1: For unpaid/crawler, create a sanitized version of the data.
        sanitized_data = m_data
        
        # Define the start and end markers for the block we want to remove.
        start_marker = "The following Stocks score has been upgraded recently."
        end_marker = "the following Stocks technical call changed recently."
        
        # Find the positions of these markers in the data.
        start_index = sanitized_data.find(start_marker)
        end_index = sanitized_data.find(end_marker)
        
        # If we found the "score upgrade" block...
        if start_index != -1:
            # Determine the end of the block to remove.
            # If a known "next block" exists, remove everything up to it.
            if end_index != -1:
                block_to_remove = sanitized_data[start_index:end_index]
            else:
                # Otherwise, remove from the start marker to the end of the data.
                block_to_remove = sanitized_data[start_index:]
            
            # Replace the identified block with an empty string.
            sanitized_data = sanitized_data.replace(block_to_remove, '')
        
        # Clean up any excess whitespace that might be left.
        sanitized_data = '\n'.join([line.strip() for line in sanitized_data.split('\n') if line.strip()])


        # STEP 2: Create specific, high-quality prompts using the now-sanitized data.
        base_summary_prompt = """You are a financial news writer. Your task is to write a news article summarizing the key trends and performance from the provided market data. Your article must focus on the main topic (e.g., overall market, a specific sector, or stocks hitting a milestone) and include all available numerical data like percentages and returns. Do not generate the response in markdown format.
" \
        "Your article MUST NOT mention or include any of the following:
- Any numerical 'score'
- Any descriptive 'grades' or subjective ratings (e.g., 'Buy,' 'Sell,' 'Hold', "Strong Buy", "Strong Sell" )
- Any analyst recommendations or calls.
        """
        
        m_unpaid_user_prompt = f"{base_summary_prompt} Here is the data:\n{sanitized_data}"
        m_google_crawler_prompt = f"{base_summary_prompt} Here is the data:\n{sanitized_data}"
    # --- END OF FINAL BLOCK ---


    elif "new_stock_added" in m_l_trigger_name:#### Mojo Premium ####
        m_unpaid_user_prompt = "The focus should be on the underlying trends or events. DO NOT mention the name of any specific stock, company, stock price, specific sector, call or give any investment advice. Remember to not disclose the stock name and stock price anywhere in the output. It should reports on any changes to the stock's score or grade, or addition to the list by revealing the specific strategy list like (Hidden Turnaround , Mojo Stocks , Reliable Performers etc) , number/percentage details , direction of the change or the specific new or old score/grade. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput. Use informative tone with fact based style. Do not generate the response in markdown format."
        m_google_crawler_prompt = "The focus should be on the underlying trends or events. It should include the stock name in the article and reports on any changes to the stock's score or grade, without revealing the specific strategy list , number/percentage details , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput. Use informative tone with fact based style. Do not generate the response in markdown format."

	
    # Use the dynamically set unpaid prompt
    messages_unpaid = [
        {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
        {"role": "user", "content": f"{m_unpaid_user_prompt} + {news_prompt}"}
    ]
    news_response_unpaid = await safe_request_with_retry(async_client,
        model="gpt-4o-mini",
        messages=messages_unpaid,
        max_tokens=2000,
        temperature=0.1,
    )
    tracking_article_unpaid = news_response_unpaid.tracking
    generated_article_unpaid = news_response_unpaid.choices[0].message.content.strip()
    # generated_article_unpaid = generated_article_unpaid.replace("Reliance Industries - 18th Jan 2024", "")
    print("ARTICLE (UNPAID)")
    print(generated_article_unpaid)
    # print(news_response_unpaid)

    # Use the dynamically set crawler prompt
    messages_crawler = [
        {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
        {"role": "user", "content": f"{m_google_crawler_prompt} + {news_prompt}"}
    ]
    news_response_crawler = await safe_request_with_retry(async_client,
        model="gpt-4o-mini",
        messages=messages_crawler,
        max_tokens=2000,
        temperature=0.1,
    )
    tracking_article_crawler = news_response_crawler.tracking
    generated_article_crawler = news_response_crawler.choices[0].message.content.strip()
    # generated_article_crawler = generated_article_crawler.replace("Reliance Industries - 18th Jan 2024", "")
    print("ARTICLE (CRAWLER)")
    print(generated_article_crawler)
    #print(news_response_crawler)

    # --- BEGIN IRB BOILERPLATE POST-PROCESSING (REVISED) ---
    if stockid == IRB_STOCK_ID:
        # For PAID articles, always append the boilerplate if it's IRB stock.
        if generated_article: # Check if paid article content exists
            # Optional: Check if it's already there to prevent double appending,
            # though for paid, AI wasn't asked to include it, so it shouldn't be.
            if IRB_BOILERPLATE_TEXT not in generated_article:
                 generated_article += "\n\n" + IRB_BOILERPLATE_TEXT.strip()
            print(f"DEBUG: Appended/Ensured IRB boilerplate for PAID article, stockid {stockid}")

        # For UNPAID and CRAWLER articles, only append if the AI wasn't already asked to.
        # Determine if the AI was instructed to add boilerplate for unpaid/crawler
        ai_handled_boilerplate_for_unpaid_crawler = False
        is_plain_result_trigger = (m_l_trigger_name == ['result']) # Re-evaluate for clarity here

        if m_l_trigger_name == ['score grade change'] or is_plain_result_trigger:
            ai_handled_boilerplate_for_unpaid_crawler = True
        
        if not ai_handled_boilerplate_for_unpaid_crawler:
            # AI was NOT asked, so Python appends it to unpaid and crawler
            if generated_article_unpaid: 
                # Check if somehow AI included it even if not explicitly asked for this trigger
                if IRB_BOILERPLATE_TEXT not in generated_article_unpaid:
                    generated_article_unpaid += "\n\n" + IRB_BOILERPLATE_TEXT.strip()
                print(f"DEBUG: Programmatically appended IRB boilerplate for UNPAID article (trigger: {m_l_trigger_name}), stockid {stockid}")
            
            if generated_article_crawler: 
                if IRB_BOILERPLATE_TEXT not in generated_article_crawler:
                    generated_article_crawler += "\n\n" + IRB_BOILERPLATE_TEXT.strip()
                print(f"DEBUG: Programmatically appended IRB boilerplate for CRAWLER article (trigger: {m_l_trigger_name}), stockid {stockid}")
        else: # AI was asked to include boilerplate for unpaid/crawler
            if generated_article_unpaid and IRB_BOILERPLATE_TEXT not in generated_article_unpaid:
                print(f"WARNING: AI was expected to include IRB boilerplate for UNPAID (trigger: {m_l_trigger_name}), but it was not found verbatim. Check AI output consistency.")
            elif generated_article_unpaid:
                print(f"DEBUG: AI included IRB boilerplate for UNPAID article (trigger: {m_l_trigger_name}), stockid {stockid}")

            if generated_article_crawler and IRB_BOILERPLATE_TEXT not in generated_article_crawler:
                print(f"WARNING: AI was expected to include IRB boilerplate for CRAWLER (trigger: {m_l_trigger_name}), but it was not found verbatim. Check AI output consistency.")
            elif generated_article_crawler:
                 print(f"DEBUG: AI included IRB boilerplate for CRAWLER article (trigger: {m_l_trigger_name}), stockid {stockid}")

    # --- END IRB BOILERPLATE POST-PROCESSING (REVISED) ---


    # -----------------------------------------------------
	########## HEADLINE SECTION ##########
    # -----------------------------------------------------

	#Create a compelling headline for this news article:
	#Generate a headline that captures the essence of this news article:
	#Craft a news headline summarizing this article:
	#Please provide a catchy news headline for this article:
	#Generate a concise and attention-grabbing headline based on the content of this news article:
    # -----------------------------------------------------
	########## new_stock_added = Mojo Premium ##########
    # -----------------------------------------------------	

    # -----------------------------------------------------
	########## Paid Headline ##########
    # -----------------------------------------------------	

    # --- Define target triggers and calculate headline temperature --- START ---
    triggers_for_temp_0_6 = ['most_active_equities_by_value', 'most_active_equities_by_volume', 'most_active_stocks_calls', 'most_active_stocks_puts']
    headline_temperature = 0.1 # Default temperature

    # Check if any of the specific triggers are present in the list m_l_trigger_name
    if any(trigger in m_l_trigger_name for trigger in triggers_for_temp_0_6):
        headline_temperature = 0.6
        print(f"INFO: Setting headline temperature to {headline_temperature} for triggers: {m_l_trigger_name}")
    else:
        print(f"INFO: Using default headline temperature {headline_temperature} for triggers: {m_l_trigger_name}")

    if "new_stock_added" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. If Quarter and FY details present in the article, then only use them in the headline. Do not generate the response in markdown format.\n" + generated_article

    # --- ADD THIS NEW, DATA-DRIVEN HEADLINE BLOCK ---
    elif "market_summary" in m_l_trigger_name:
        headline_prompt = "Create a compelling and clickable news headline in max 10 to 14 words using the provided market summary data. The headline MUST include the main index's performance and another key data point like the advance/decline ratio or the name of a top-performing stock. Focus on making it highly informative and attention-grabbing. Do not start with 'Headline:'.\n" + generated_article
    # --- END OF NEW BLOCK ---

    elif "multibagger" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 14 words using followings news article, mention the word 'multibagger' in the headline, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. If Quarter and FY details present in the article, then only use them in the headline. Do not generate the response in markdown format.\n" + generated_article
    elif "only_buyers" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Focus on price increases and any significant milestones reached (e.g., upper circuit). Use keywords related to gains and price movement. Include the stock name. Please do not start the headline with 'Headline:'. If Quarter and FY details present in the article, then only use them in the headline. Do not generate the response in markdown format.\n" + generated_article
    elif "only_sellers" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Focus on selling and any significant price declines. Use keywords related to selling , sellers and loss. Include the stock name. Please do not start the headline with 'Headline:'. If Quarter and FY details present in the article, then only use them in the headline. Do not generate the response in markdown format.\n" + generated_article
    elif "ipo_listing" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Emphasize more on the important events from price summary and Return of company section. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n" + generated_article
    elif "valuation_dot" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Emphasize on the Valuation grade change. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n" + generated_article
    elif "quality_dot" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Emphasize on the Quality grade change. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n" + generated_article
    elif "fintrend_dot" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Explicitly mention the Financial Trend scale change from old to new (e.g., 'Flat to Negative', 'Positive to Flat') along with the company name. Emphasize on the financial trend changes without any predictions. Follow given Financial Trend Scale: Very Negative < Negative < Flat < Positive < Very Positive < Outstanding . For Example : CIE Automotive's Financial Trend Drops from Flat to Negative Amid Declining Sales. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n" + generated_article
    elif "technical_dot" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Explicitly mention the Technical Trend scale change from old to new (e.g., 'Bearish to Sideways', 'Mildly Bearish to Bullish') along with the company name. Emphasize on the Techical Trend changes without any predictions. Follow given Technical Indicator Scale: Bearish < Mildly Bearish < Sideways < Mildly Bullish < Bullish  For Example : CIE Automotive's Techical Trend Drops from Sideways to Bearish Amid Declining Sales. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n" + generated_article
    elif "stocks_hitting_lower_circuit" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the lowPrice and not ltp. The main story is that the stock hit its lower circuit limit mentioning its lowPrice. Do not generate the response in markdown format.\n" + generated_article
    elif "stocks_hitting_upper_circuit" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the highPrice and not ltp. The main story is that the stock hit its upper circuit limit mentioning its highPrice. Do not generate the response in markdown format.\n" + generated_article
    # elif "gap_up" in m_l_trigger_name:
    #     headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the Gap Up. The main story is that the stock opened with a gain mentioning its gain percentage. Do not generate the response in markdown format.\n" + generated_article
    # elif "all_time_high" in m_l_trigger_name:
    #     headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the All time High. The main story is that the stock hit All time High today with mentioning the All time High Price. Do not generate the response in markdown format.\n" + generated_article
    # elif "all_time_low" in m_l_trigger_name:
    #     headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the All time Low. The main story is that the stock hit All time Low today with mentioning the All time Low Price. Do not generate the response in markdown format.\n" + generated_article
    # elif "most_active_stocks_calls" in m_l_trigger_name:
    #     headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the core of the article. The headline must use the variation of phrases: 'has emerged as one of the most active stock calls today'. Do not generate the response in markdown format.\n" + generated_article
    # elif "most_active_stocks_puts" in m_l_trigger_name:
    #     headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the core of the article. The headline must use the variation of phrases: 'has emerged as one of the most active stock puts today'. Do not generate the response in markdown format.\n" + generated_article

    # --- ADDED/MODIFIED BLOCK for most active equities ---
    elif "most_active_equities_by_value" in m_l_trigger_name:
        headline_prompt = "Create a specific and distinctive headline in max 6 to 14 words that focuses on this stock being one of the most active equities by value today. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Include the exact company name and highlight a key numerical data point from the article (such as trade value, price change percentage, or day's movement). The headline must convey this is about 'most active equities by value' but vary the phrasing. Do not use generic templates. Make the headline specific to the data provided. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4.\n" + generated_article

    elif "most_active_equities_by_volume" in m_l_trigger_name:
        headline_prompt = "Create a specific and distinctive headline in max 6 to 14 words that focuses on this stock being one of the most active equities by Volume today. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Include the exact company name and highlight a key numerical data point from the article (such as trade volume, price change percentage, or day's movement). The headline must convey this is about 'most active equities by volume' but vary the phrasing. Do not use generic templates. Make the headline specific to the data provided. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4.\n" + generated_article
    # --- END ADDED/MODIFIED BLOCK ---
    elif "most_active_stocks_calls" in m_l_trigger_name:
        headline_prompt = "Create a unique and specific headline in max 6 to 14 words for this financial news about stock options. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Use the exact company name and highlight the most notable data point from the news article (such as specific strike price, number of contracts traded, percentage changes, moving averages, turnover , open interest, underlying value, price summary or investor participation). The headline must indicate this is about 'most active calls' but vary the phrasing. Do not use generic templates. Do not start with 'Headline:'. Ensure the headline is unique to this specific data set. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Focus on what makes THIS specific option activity noteworthy.\n" + generated_article
    elif "most_active_stocks_puts" in m_l_trigger_name:
        headline_prompt = "Create a unique and specific headline in max 6 to 14 words for this financial news about stock options. Don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Use the exact company name and highlight the most notable data point from the news article (such as specific strike price, number of contracts traded, percentage changes, moving averages, turnover , open interest, underlying value, price summary or investor participation). The headline must indicate this is about 'most active puts' but vary the phrasing. Do not use generic templates. Do not start with 'Headline:'. Ensure the headline is unique to this specific data set. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Focus on what makes THIS specific option activity noteworthy.\n" + generated_article

    elif "oi_spurts_by_underlying" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article highlighting the spurt in open interest for this stock , use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n" + generated_article
    elif "result" in m_l_trigger_name:
        headline_prompt = "Create a headline in max 6 to 14 words using followings news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Instead just mention the month & year of the result in MMM'YY format if the month & year of result is mentioned in the context. Do not generate the response in markdown format.\n" + generated_article

    # THIS IS THE NEW, IMPROVED BLOCK
    else:
        # --- NEW LOGIC FOR SPECIFIC HEADLINES ---
        # trigger_key = m_l_trigger_name[0] if m_l_trigger_name else None

        # --- START OF FIX ---
        # This logic handles cases where the trigger name is a list (like ['day high'])
        # or a string (like 'high_return_in_period').
        if isinstance(m_l_trigger_name, list):
            trigger_key = m_l_trigger_name[0] if m_l_trigger_name else None
        else:
            trigger_key = m_l_trigger_name
        # --- END OF FIX ---


        # Check if a specific headline prompt exists in our new dictionary
        if trigger_key and trigger_key in STOCK_IN_ACTION_HEADLINE_PROMPTS:
            print(f"INFO: Found a specific headline prompt for trigger: '{trigger_key}'")
            base_prompt = STOCK_IN_ACTION_HEADLINE_PROMPTS[trigger_key]
        else:
            # Fallback to the generic prompt if no specific one is found
            print(f"INFO: No specific headline prompt for '{trigger_key}'. Using generic prompt.")
            base_prompt = "Create a headline using the following news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style."

        # Append the common instructions (word count, formatting) to the chosen prompt
        headline_prompt = (f"{base_prompt} The headline should be a maximum of 6 to 14 words. "
                            f"Please do not start the headline with 'Headline:'. "
                            f"Avoid mentioning the quarter - Q1, Q2, Q3, Q4. "
                            f"Do not generate the response in markdown format.\n" + generated_article)


    messages = [
        {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
        {"role": "user", "content": f"{headline_prompt}"}
    ]

    headline_response = await safe_request_with_retry(async_client,
		#model = "gpt-3.5-turbo",
		#engine="text-davinci-003",  # You can use another engine if needed
		model="gpt-4o-mini", #gpt-3.5-turbo-instruct-0914",
		#model="davinci-002",
		messages=messages,
		max_tokens=2000,  # You can adjust this based on the desired length of the generated content
		temperature= headline_temperature, #random.uniform(0.2, 0.4) #(random.randint(0, 7**5)/ 7**5),  # You can adjust this for more creative or more focused outputs
	)
    tracking_headline = headline_response.tracking
    generated_headline = headline_response.choices[0].message.content.strip()
    print("HEADLINE")
    print(generated_headline)
    #print(headline_response)

    # -----------------------------------------------------
	########## Unpaid Headline ##########
    # -----------------------------------------------------	

    # --- START OF MODIFIED SECTION FOR UNPAID HEADLINE ---
    
    # Check if the current trigger is a 'stock in action' trigger
    # trigger_key = m_l_trigger_name[0] if m_l_trigger_name else None

    # --- START OF FIX ---
    # This logic handles cases where the trigger name is a list (like ['day high'])
    # or a string (like 'high_return_in_period').
    if isinstance(m_l_trigger_name, list):
        trigger_key = m_l_trigger_name[0] if m_l_trigger_name else None
    else:
        trigger_key = m_l_trigger_name
    # --- END OF FIX ---


    # Define the list of summary triggers that should also reuse the headline
    summary_triggers = ["market_summary", "smallcap_market_summary", "midcap_market_summary", "largecap_market_summary", "sector_summary", "52_week_high_summary"]


    if (trigger_key in stock_in_action_triggers or trigger_key == 'multibagger' or trigger_key == 'high_return_in_period' or  trigger_key == 'dealth_cross' or trigger_key == 'golden_cross' or trigger_key in summary_triggers) and trigger_key not in HEADLINE_REUSE_EXCLUSIONS:

        # If it is, simply reuse the paid headline and skip the API call
        print(f"INFO: Reusing paid headline for unpaid 'stock in action' trigger: '{trigger_key}'")
        generated_headline_unpaid = generated_headline
        # Create a dummy tracking entry since no API call was made
        tracking_headline_unpaid = {"duration": 0, "total_cost": 0}
    else:
        # If it's NOT a 'stock in action' trigger, generate the unpaid headline as usual
        print(f"INFO: Generating unique unpaid headline for trigger: '{trigger_key}'")

        #FOR UNPAID HEADLINE
        if "new_stock_added" in m_l_trigger_name:
            headline_prompt_unpaid="Create an informative headline in max 14 words using the following news article. Focus on the underlying trends or events mentioned regarding specific stock mentioned in the article. DO NOT mention the name of any specific stock, company , stock price, specific sector, call or give any investment advice. Make it sound like a teaser with enough details to make it interesting without revealing the full context to identify the stock. Use a fact-based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n: " + generated_article_unpaid
        elif any(trigger in m_l_trigger_name for trigger in stock_in_action_triggers):#### Stock In Action ####
            if 'only_buyers' in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Focus on price increases and any significant milestones reached (e.g., upper circuit). Use keywords related to gains and price movement. Include the stock name. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            elif 'only_sellers' in m_l_trigger_name:      
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Focus on selling and any significant price declines. Use keywords related to selling , sellers and loss. Include the stock name. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            elif "ipo_listing" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize more on the important events from price summary and Return of company section.  Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            elif "valuation_dot" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Valuation grade change. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            elif "quality_dot" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Quality grade change. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            elif "fintrend_dot" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Financial Trend changes. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            elif "technical_dot" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Technical Trend changes. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            elif "gap_up" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the Gap Up. The main story is that the stock opened with a gain mentioning its gain percentage.\n:" + generated_article_unpaid
            elif "all_time_high" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the All time High. The main story is that the stock hit All time High today with mentioning the All time High Price.\n: " + generated_article_unpaid
            elif "all_time_low" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the All time Low. The main story is that the stock hit All time Low today with mentioning the All time Low Price.\n: " + generated_article_unpaid
            # elif "most_active_stocks_calls" in m_l_trigger_name:
            #     headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Emphasize more on the core of the article. The headline must use the variation of phrases: 'has emerged as one of the most active stock calls today' Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4.\n: " + generated_article_unpaid
            # elif "most_active_stocks_puts" in m_l_trigger_name:
            #     headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Emphasize more on the core of the article. The headline must use the variation of phrases: 'has emerged as one of the most active stock puts today'. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4.\n: " + generated_article_unpaid
    ########################################################
            elif "most_active_stocks_calls" in m_l_trigger_name:
                headline_prompt_unpaid = "Create a unique and specific headline in max 6 to 14 words for this financial news about stock options. Use the exact company name and highlight the most notable data point from the context (such as specific strike price, number of contracts, percentage changes, moving averages, or investor participation). The headline must indicate this is about 'most active calls' but vary the phrasing. Do not use generic templates. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Focus on what makes THIS specific option activity noteworthy.\n" + generated_article_unpaid
            elif "most_active_stocks_puts" in m_l_trigger_name:
                headline_prompt_unpaid = "Create a unique and specific headline in max 6 to 14 words for this financial news about stock options. Use the exact company name and highlight the most notable data point from the context (such as specific strike price, number of contracts, percentage changes, moving averages, or investor participation). The headline must indicate this is about 'most active puts' but vary the phrasing. Do not use generic templates. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Focus on what makes THIS specific option activity noteworthy.\n" + generated_article_unpaid

    ########################################################
            elif "oi_spurts_by_underlying" in m_l_trigger_name:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article highlighting the spurt in open interest for this stock. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
            else:
                headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
        elif 'score grade change' in m_l_trigger_name:#### Call Changes ####
            headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_unpaid
        elif 'result' in m_l_trigger_name:#### Result Alerts ####
            headline_prompt_unpaid = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key events described in the news article about recently announced financial results of the stock. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Instead just mention the month & year of the result in MMMM'YY format if the month & year of result is mentioned in the context.\n: " + generated_article_unpaid
        else:
            headline_prompt_unpaid="Create an informative headline in max 6 to 14 words using the following news article. Focus on the underlying trends or events mentioned regarding specific stock mentioned in the article. DO NOT mention the name of any specific stock, company, stock price, specific sector, call or give any investment advice. Make it sound like a teaser with enough details to make it interesting without revealing the full context to identify the stock. Use a fact-based style. Please do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format.\n: " + generated_article_unpaid

        messages = [
                {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
                {"role": "user", "content": headline_prompt_unpaid}
            ]

        headline_response_unpaid = await safe_request_with_retry(async_client,
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=2000,
            temperature= headline_temperature,
        )
        tracking_headline_unpaid = headline_response_unpaid.tracking
        generated_headline_unpaid = headline_response_unpaid.choices[0].message.content.strip()
        print("HEADLINE (UNPAID)")
        print(generated_headline_unpaid)
        #print(headline_response_unpaid)

    if (trigger_key in stock_in_action_triggers or trigger_key == 'multibagger' or trigger_key == 'high_return_in_period' or  trigger_key == 'dealth_cross' or trigger_key == 'golden_cross' or trigger_key in summary_triggers) and trigger_key not in HEADLINE_REUSE_EXCLUSIONS:
        # If it is, simply reuse the paid headline and skip the API call
        print(f"INFO: Reusing paid headline for crawler 'stock in action' trigger: '{trigger_key}'")
        generated_headline_crawler = generated_headline
        # Create a dummy tracking entry
        tracking_headline_crawler = {"duration": 0, "total_cost": 0}
    else:
        # If it's NOT a 'stock in action' trigger, generate the crawler headline as usual
        print(f"INFO: Generating unique crawler headline for trigger: '{trigger_key}'")

        if "new_stock_added" in m_l_trigger_name:
            headline_prompt_crawler="Create an informative headline in max 14 words using the following stock analysis data, that reports on any changes to the stock's score or grade, without revealing the specific direction of the change or the specific new or old score/grade. You can use terms like 'call changes,' 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Do not generate the response in markdown format. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput.  Include the stock name in the headline. Report on any changes to the stock's score or grade, without mentioning the specific direction of the change or the specific new or old score/grade. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the headline. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not generate the response in markdown format. Do not start the headline with 'Headline:'.\n" + generated_article_crawler
        elif any(trigger in m_l_trigger_name for trigger in stock_in_action_triggers):#### Stock In Action ####
            if 'only_buyers' in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Focus on price increases and any significant milestones reached (e.g., upper circuit). Use keywords related to gains and price movement. Include the stock name. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif 'only_sellers' in m_l_trigger_name:      
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Focus on selling and any significant price declines. Use keywords related to selling , sellers and loss. Include the stock name. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif "ipo_listing" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize more on the important events from price summary and Return of company section.  Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif "valuation_dot" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Valuation grade change. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif "quality_dot" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Quality grade change. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif "fintrend_dot" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Financial Trend changes. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif "technical_dot" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Emphasize on the Technical Trend changes. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif "gap_up" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the Gap Up. The main story is that the stock opened with a gain mentioning its gain percentage. \n: " + generated_article_crawler
            elif "all_time_high" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the All time High. The main story is that the stock hit All time High today with mentioning the All time High Price. \n:  " + generated_article_crawler
            elif "all_time_low" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Emphasize more on the All time Low. The main story is that the stock hit All time Low today with mentioning the All time Low Price. \n: " + generated_article_crawler
            # elif "most_active_stocks_calls" in m_l_trigger_name:
            #     headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Emphasize more on the core of the article. The headline must use the variation of phrases: 'has emerged as one of the most active stock calls today' Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            # elif "most_active_stocks_puts" in m_l_trigger_name:
            #     headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Emphasize more on the core of the article. The headline must use the variation of phrases: 'has emerged as one of the most active stock puts today'. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
    #############################################################  
            elif "most_active_stocks_calls" in m_l_trigger_name:
                headline_prompt_crawler = "Generate a distinctive headline in max 6 to 14 words specifically tailored to this stock's call option activity. Include the exact company name and reference the most significant numerical data point from the article (strike price, number of contracts traded, turnover , open interest, underlying value and price summary etc.). The headline must indicate these are 'active calls options' but using varied language. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Ensure the headline is unique to this specific data set. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            elif "most_active_stocks_puts" in m_l_trigger_name:
                headline_prompt_crawler = "Generate a distinctive headline in max 6 to 14 words specifically tailored to this stock's put option activity. Include the exact company name and reference the most significant numerical data point from the article (strike price, number of contracts traded, turnover , open interest, underlying value and price summary etc.). The headline must indicate these are 'active put options' but using varied language. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Ensure the headline is unique to this specific data set. Do not start with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler

    #############################################################            
            elif "oi_spurts_by_underlying" in m_l_trigger_name:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article highlighting the spurt in open interest for this stock. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
            else:
                headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key financial trends or events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
        elif 'score grade change' in m_l_trigger_name:#### Call Changes ####
            headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key events described in the news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. \n: " + generated_article_crawler
        elif 'result' in m_l_trigger_name:#### Result Alerts ####
            headline_prompt_crawler = "Create an informative headline in max 6 to 14 words using the following news article. It should highlight key events described in the news article about recently announced financial results of the stock. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. The headline should be informative and objective. Focus on the potential implications. Do not generate the response in markdown format. Do not start the headline with 'Headline:'. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Instead just mention the month & year of the result in MMMM'YY format if the month & year of result is mentioned in the context. \n: " + generated_article_crawler
        else:
            headline_prompt_crawler="Create an infromative headline in max 6 to 14 words using the following stock analysis data. that reports on any changes to the stock's score or grade, without revealing the specific direction of the change or the specific new or old score/grade. Include the name of the stock in the article. You can use terms like 'call changes,' 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput.  Include the stock name in the headline. Report on any changes to the stock's score or grade, without mentioning the specific direction of the change or the specific new or old score/grade. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the headline. Avoid mentioning the quarter - Q1, Q2, Q3, Q4. Do not start the headline with 'Headline:'.\n" + generated_article_crawler


        messages = [
                {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
                {"role": "user", "content": headline_prompt_crawler}
            ]

        headline_response_crawler = await safe_request_with_retry(async_client,
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=2000,
            temperature= headline_temperature,
        )
        tracking_headline_crawler = headline_response_crawler.tracking
        generated_headline_crawler = headline_response_crawler.choices[0].message.content.strip()
        print("HEADLINE (CRAWLER)")
        print(generated_headline_crawler)
        #print(headline_response_crawler)


    # -----------------------------------------------------
	########## SUMMARY SECTION ##########
    # -----------------------------------------------------

    # -----------------------------------------------------
	########## Paid Summary ##########
    # -----------------------------------------------------	

	#Generate a brief summary of the following news article:
	#Summarize the main points of the news article below:
	#Craft a short summary of this news article:
	#Generate a concise summary of the news article provided:
    if "result_summary" in m_l_trigger_name or "market_summary" in m_l_trigger_name or "smallcap_market_summary" in m_l_trigger_name or "midcap_market_summary" in m_l_trigger_name or "largecap_market_summary" in m_l_trigger_name or "sector_summary" in m_l_trigger_name or "high_return_in_period" in m_l_trigger_name:
        summary_prompt = "Generate a brief summary in 50 to 100 words using following news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the Summary with 'Summary:'. Do not generate the response in markdown format.\n" + generated_article
    else:
        summary_prompt = "Generate a brief summary in 40 to 50 words using following news article, use informative tone, don't talk about future potential, don't mention investor interest or experts, no recommendation, use fact based style. Please do not start the Summary with 'Summary:'. Do not generate the response in markdown format.\n" + generated_article

	
    messages = [
            {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
            {"role": "user", "content": f"{summary_prompt}"}
        ]

    summary_response = await safe_request_with_retry(async_client,
		#model = "gpt-3.5-turbo",
		#engine="text-davinci-003",  # You can use another engine if needed
		model="gpt-4o-mini", #gpt-3.5-turbo-instruct-0914",
		messages=messages,
		max_tokens=2000,  # You can adjust this based on the desired length of the generated content
		temperature= 0.1, # random.uniform(0.1, 0.3),  # You can adjust this for more creative or more focused outputs
	)
    tracking_summary = summary_response.tracking
    generated_summary = summary_response.choices[0].message.content.strip()
    print("SUMMARY")
    print(generated_summary)
    #print(summary_response)


    # -----------------------------------------------------
	########## Unpaid Summary ##########
    # -----------------------------------------------------	

    if "result_summary" in m_l_trigger_name or "market_summary" in m_l_trigger_name or "smallcap_market_summary" in m_l_trigger_name or "midcap_market_summary" in m_l_trigger_name or "largecap_market_summary" in m_l_trigger_name or "sector_summary" in m_l_trigger_name or "high_return_in_period" in m_l_trigger_name:
        unpaid_summary_prompt = "Generate an informative brief summary in 50 to 100 words using the following news article, focusing on the underlying trends or events. Please do not start the Summary with 'Summary:'. Do not generate the response in markdown format. : \n" + generated_article_unpaid
    elif any(trigger in m_l_trigger_name for trigger in stock_in_action_triggers):#### Stock In Action ####
        unpaid_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_unpaid
    elif 'score grade change' in m_l_trigger_name:#### Call Changes ####
        unpaid_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article, about a recent score or grade change. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_unpaid
    elif "new_stock_added" in m_l_trigger_name:#### Mojo Premium ####
        unpaid_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article, about a recent evaluation in the stock. DO NOT mention the name of any specific stock, company, stock price, specific sector, call or give any investment advice. Remember to not disclose the stock name and stock price anywhere in the output. It should reports on any changes to the stock's score or grade, or addition to the list by revealing the specific strategy list like (Hidden Turnaround , Mojo Stocks , Reliable Performers etc), number/percentage details , direction of the change or the specific new or old score/grade. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput. Use informative tone with fact based style. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_unpaid
    elif 'result' in m_l_trigger_name:#### Result Alerts ####
        unpaid_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article, about recently announced financial results. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_unpaid
    else:
        unpaid_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article, focusing on the underlying trends or events. Please do not start the Summary with 'Summary:'. Do not generate the response in markdown format. : \n" + generated_article_unpaid

    messages = [
            {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
            {"role": "user", "content":  unpaid_summary_prompt}
        ]

    summary_response_unpaid = await safe_request_with_retry(async_client,
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=2000,
        temperature= 0.1,
    )
    tracking_summary_unpaid = summary_response_unpaid.tracking
    generated_summary_unpaid = summary_response_unpaid.choices[0].message.content.strip()
    print("SUMMARY (UNPAID)")
    print(generated_summary_unpaid)
    #print(summary_response_unpaid)

    if "result_summary" in m_l_trigger_name or "market_summary" in m_l_trigger_name or "smallcap_market_summary" in m_l_trigger_name or "midcap_market_summary" in m_l_trigger_name or "largecap_market_summary" in m_l_trigger_name or "sector_summary" in m_l_trigger_name or "high_return_in_period" in m_l_trigger_name:
        crawler_summary_prompt = "Generate an informative brief summary in 50 to 100 words using the following news article, focusing on the underlying trends or events. Please do not start the Summary with 'Summary:'. Do not generate the response in markdown format. : \n" + generated_article_crawler
    elif any(trigger in m_l_trigger_name for trigger in stock_in_action_triggers):#### Stock In Action ####
        crawler_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_crawler
    elif 'score grade change' in m_l_trigger_name:#### Call Changes ####
        crawler_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article, about a recent score or grade change. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_crawler
    elif "new_stock_added" in m_l_trigger_name:
        crawler_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article, about a recent evaluation in the stock. It should include the stock name in the sumamry and reports on any changes to the stock's score or grade, without revealing the specific strategy list , number/percentage details , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput. Use informative tone with fact based style. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_crawler
    elif 'result' in m_l_trigger_name:#### Result Alerts ####
        crawler_summary_prompt = "Generate an informative brief summary in 40 to 50 words using the following news article, about recently announced financial results. Do not mention the direction, specific value of the change or analyst calls, or any investment advice. Do not generate the response in markdown format. Please do not start the Summary with 'Summary:'.\n: " + generated_article_crawler
    else:
        crawler_summary_prompt = "Generate a brief summary in 40 to 50 words given the following stock analysis data, generate a news article which include the stock name in the sumamry and reports on any changes to the stock's score or grade, without revealing the specific number/percentage details , direction of the change or the specific new or old score/grade. Include the name of the stock in the article. You can use terms like 'call changes,' 'adjustment in evaluation,' or 'revision in its score' to indicate a change in the stock's score or grade. Do not mention any specific rating (e.g., 'Buy,' 'Sell,' 'Hold') or if the rating was upgraded or downgraded in any part of the output. Focus on key financial metrics, market position, and performance indicators. Avoid adding the company's entry price, target price and upside/downside potential anywhere in the ouput. Use informative tone with fact based style. Please do not start the summary with 'Summary:'. Do not generate the response in markdown format. \n" + generated_article_crawler


    messages = [
            {"role": "system", "content": "You are a financial assistant specialized in financial journalism."},
            {"role": "user", "content": crawler_summary_prompt}
        ]

    summary_response_crawler = await safe_request_with_retry(async_client,
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=2000,
        temperature= 0.1,
    )
    tracking_summary_crawler = summary_response_crawler.tracking
    generated_summary_crawler = summary_response_crawler.choices[0].message.content.strip()
    print("SUMMARY (CRAWLER)")
    print(generated_summary_crawler)
    #print(summary_response_crawler)

    '''
	# Create a request to the DALL-E model
	prompt = ("Generate an image that visually represents the stock performance of Honda India Power Products in the Electric Equipment industry, "
			  "Honda India Stock Sees Negative Returns in Past Year, Underperforms Sensex and Sector Honda India, one of the leading car manufacturers in the country, has seen a negative return of -7.14% in the past year. This is in stark contrast to the 6.32% return of the Sensex, India's benchmark stock index, which has outperformed Honda India by 13.46%. In addition, the company has also underperformed its own sector by a whopping 63.71%. The sector return stands at 56.57%, highlighting Honda India's struggles in the market. Moreover, the dividend yield for the company is at a low 0.67%, with the latest dividend of 16.5 per share being announced with an ex-dividend date of August 3, 2023. This raises concerns for investors who are looking for steady returns on their investments. The risk-return profile for Honda India is also not very favorable, with the company being classified as a high-risk, low-return stock. During the past year, Honda India has given lower returns per unit of risk compared to the Sensex. The company also has a medium beta of 1.03 with the Sensex, indicating that it is moderately sensitive to market fluctuations. This could be a concern for investors who are looking for stable and consistent returns. In the short term, Honda India has not fared well either, with a negative return of -3.76% in the past week and a sharp decline of -15.22% in the past month. However, there is some relief for investors in the longer term, as the company has seen a positive return of 7.80% in the past six months. Overall, Honda India's stock performance has been lackluster in the past year, with negative returns and underperformance compared to the market and sector. Investors should carefully consider the risk-return profile of the company before making any investment decisions.")

	response = openai.Image.create(
	  model="dall-e-3",
	  prompt=prompt,
	  n=1,
	  size="1024x1024",
	  quality="hd",
	  style="vivid" #natural" #vivid
	)

	print(response)
	'''
    generated_headline = generated_headline.strip()
    generated_headline = generated_headline.replace('\"', '')
    generated_summary = generated_summary.strip()
    generated_summary = generated_summary.replace('\"', '')

    generated_headline_unpaid = generated_headline_unpaid.strip()
    generated_headline_unpaid = generated_headline_unpaid.replace('\"', '')
    generated_summary_unpaid = generated_summary_unpaid.strip()
    generated_summary_unpaid = generated_summary_unpaid.replace('\"', '')

    generated_headline_crawler = generated_headline_crawler.strip()
    generated_headline_crawler = generated_headline_crawler.replace('\"', '')
    generated_summary_crawler = generated_summary_crawler.strip()
    generated_summary_crawler = generated_summary_crawler.replace('\"', '')
	
    tracking = {
        "article": tracking_article,
        "article_unpaid": tracking_article_unpaid,
        "article_crawler": tracking_article_crawler,
        "headline": tracking_headline,
        "headline_unpaid": tracking_headline_unpaid,
        "headline_crawler": tracking_headline_crawler,
        "summary": tracking_summary,
        "summary_unpaid": tracking_summary_unpaid,
        "summary_crawler": tracking_summary_crawler
    }

    complete_total_cost = (
        tracking_article.get("total_cost", 0) +
        tracking_article_unpaid.get("total_cost", 0) +
        tracking_article_crawler.get("total_cost", 0) +
        tracking_headline.get("total_cost", 0) +
        tracking_headline_unpaid.get("total_cost", 0) +
        tracking_headline_crawler.get("total_cost", 0) +
        tracking_summary.get("total_cost", 0) +
        tracking_summary_unpaid.get("total_cost", 0) +
        tracking_summary_crawler.get("total_cost", 0)
    )

    complete_total_cost = round(complete_total_cost, 6)
    tracking["total_cost"] = complete_total_cost


    return (generated_article, generated_summary, generated_headline, news_prompt,
            generated_article_unpaid, generated_summary_unpaid, generated_headline_unpaid,
            generated_article_crawler, generated_summary_crawler, generated_headline_crawler,
            tracking)


# --- ADD THIS SECTION ---
# Mapping from trigger_name (as used in code) to bucket and priority
TRIGGER_BUCKET_PRIORITY_MAPPING = {
    # Bucket 1
    "most_active_equities_by_volume": {"bucket": 1, "priority": 1},
    "most_active_equities_by_value": {"bucket": 1, "priority": 2},
    "oi_spurts_by_underlying": {"bucket": 1, "priority": 3},
    "most_active_stocks_calls": {"bucket": 1, "priority": 4},
    "most_active_stocks_puts": {"bucket": 1, "priority": 5},

    # Bucket 2
    "stocks_hitting_upper_circuit": {"bucket": 2, "priority": 1},
    "only_buyers": {"bucket": 2, "priority": 2},
    "gap_up": {"bucket": 2, "priority": 3},

    # Bucket 3
    "stocks_hitting_lower_circuit": {"bucket": 3, "priority": 1},
    "only_sellers": {"bucket": 3, "priority": 2},
    "gap_down": {"bucket": 3, "priority": 3},

    # Bucket 4
    "all_time_high": {"bucket": 4, "priority": 1},
    "52wk_high": {"bucket": 4, "priority": 2},
    "day high": {"bucket": 4, "priority": 3},

    # Bucket 5
    "all_time_low": {"bucket": 5, "priority": 1},
    "52wk_low": {"bucket": 5, "priority": 2},
    "day low": {"bucket": 5, "priority": 3},
}
# --- END OF ADDED SECTION ---


async def process_trigger(m_r_news_triggers):
    start_time = time.time()  # Start time for this task
    m_dict = {}

    # --- START: MODIFIED SECTION ---
    # The main logic is wrapped in a try...except block to catch KeyErrors
    # try:

    m_dict["newsid"] = m_r_news_triggers["_id"]
    m_dict["stockid"] = m_r_news_triggers["stockid"]
    m_dict["category"] = m_r_news_triggers["category"]
    m_dict["date"] = m_r_news_triggers["date"]
    m_dict["data"] = m_r_news_triggers["data"]

    # --- START: ADD THIS BLOCK TO CHECK FOR 'inf%' ---
    # Check if the raw data string contains ' inf%' to catch infinite growth percentages.
    if " inf%" in m_r_news_triggers.get("data", ""):
        error_msg = f"Skipping newsid {m_r_news_triggers['_id']} due to 'inf%' in data, indicating invalid growth calculation."
        print(error_msg)
        
        # Update the trigger status to 2 (failed/skipped) so it's not processed again.
        m_filter = {"_id": m_r_news_triggers["_id"]}
        m_news_triggers.update_one(m_filter, {"$set": {"status": 2, "error_message": error_msg}})
        
        # Stop processing this trigger and move to the next one.
        return
    # --- END: ADD THIS BLOCK ---

    # --- NEW CHANGE FOR COUNTRYID ---
    if "country_id" in m_r_news_triggers:
        m_dict["country_id"] = m_r_news_triggers["country_id"]
    else:
        m_dict["country_id"] = None 
    # --- END OF ADDED BLOCK ---
    if "score" in m_r_news_triggers:
        m_dict["score"] = m_r_news_triggers["score"]
    else:
        m_dict["score"] = None
    if "scoreText" in m_r_news_triggers:
        m_dict["scoreText"] = m_r_news_triggers["scoreText"]
    else:
        m_dict["scoreText"] = None
    m_dict["trigger_name"] = m_r_news_triggers["trigger_name"]


    # --- START: Add this new block to transfer your custom fields ---

    # Transfer 'changed_fields' if the trigger is 'score grade change'
    if 'score grade change' in m_r_news_triggers.get('trigger_name', []) and 'changed_fields' in m_r_news_triggers:
        m_dict['changed_fields'] = m_r_news_triggers['changed_fields']

    # Transfer 'totalTradedVolume' if the trigger is 'most_active_equities_by_volume'
    if 'most_active_equities_by_volume' in m_r_news_triggers.get('trigger_name', []) and 'totalTradedVolume' in m_r_news_triggers:
        m_dict['totalTradedVolume'] = m_r_news_triggers['totalTradedVolume']

    # Transfer 'totalTradedValue' if the trigger is 'most_active_equities_by_value'
    if 'most_active_equities_by_value' in m_r_news_triggers.get('trigger_name', []) and 'totalTradedValue' in m_r_news_triggers:
        m_dict['totalTradedValue'] = m_r_news_triggers['totalTradedValue']

    # --- END: End of the new block ---


    m_filter = {"sid":m_dict["stockid"]}
    m_c_stock_screener = m_stock_screener.find(m_filter)
    for m_r_stock_screener in m_c_stock_screener:
        m_dict["ind_id"] = m_r_stock_screener["old_ind_id"]
        if "sector_id" in m_r_stock_screener:
            m_dict["sub_sect_id"] = m_r_stock_screener["sector_id"]
        else:
            m_dict["sub_sect_id"] = m_dict["ind_id"]
        m_fin_grade = m_r_stock_screener["fin_grade"]

    if "old_ind_id" in m_r_news_triggers:
        m_dict["ind_id"] = m_r_news_triggers["old_ind_id"]
    if "sub_sect_id" in m_r_news_triggers:
        m_dict["sub_sect_id"] = m_r_news_triggers["sub_sect_id"]
    if "bse_nse" in m_r_news_triggers:
        if m_r_news_triggers["bse_nse"] in [None]:
            m_dict["exch"] = None
        elif "bse" in m_r_news_triggers["bse_nse"]:
            m_dict["exch"] = 0
        else:
            m_dict["exch"] = 1

    #if "scoreTxtChngDate" in m_r_news_triggers:
    if "scoreTxtChngDate" in m_r_news_triggers:
        m_dict["scoreTxtChngDate"] = m_r_news_triggers["scoreTxtChngDate"]
    else:
        m_dict["scoreTxtChngDate"] = None
    #else:
    #	m_dict["scoreTxtChngDate"] = ""
    #if "prevScoreText" in m_r_news_triggers:
    if "prevScoreText" in m_r_news_triggers:
        m_dict["prevScoreText"] = m_r_news_triggers["prevScoreText"]
    else:
        m_dict["prevScoreText"] = None

    if "scoreText" in m_r_news_triggers:
        m_dict["scoreText"] = m_r_news_triggers["scoreText"]
    else:
        m_dict["scoreText"] = None
    if "prev_fin_grade" in m_r_news_triggers:
        m_dict["prev_fin_grade"] = m_r_news_triggers["prev_fin_grade"]
    else:
        m_dict["prev_fin_grade"] = None

    if "fin_grade" in m_r_news_triggers:
        m_dict["fin_grade"] = m_r_news_triggers["fin_grade"]
    else:
        m_dict["fin_grade"] = None

    #else:
    #	m_dict["prevScoreText"] = ""
    #if "trigger_date" in m_r_news_triggers:
    print("TRIGGER:{0}".format(m_dict["trigger_name"]))
    # if m_dict["trigger_name"] == ["market_summary"] or m_dict["trigger_name"] == ["result_summary"] or m_dict["trigger_name"] == ["smallcap_market_summary"] or m_dict["trigger_name"] == ["midcap_market_summary"] or m_dict["trigger_name"] == ["largecap_market_summary"] or m_dict["trigger_name"] == ["sector_summary"] or m_dict["trigger_name"] == ["downgrade_summary"] or m_dict["trigger_name"] == ["upgrade_summary"] or m_dict["trigger_name"] == ["tech_dot_summary"] or m_dict["trigger_name"] == ["new_stock_added"] or m_dict["trigger_name"] == ["high_return_in_period"] or m_dict["trigger_name"] == ["52_week_high_summary"] or m_dict["trigger_name"] == ["updated_Downgrade_summary"] or m_dict["trigger_name"] == ["tech_upgrade_summary"] or m_dict["trigger_name"] == ["tech_downgrade_summary"] or m_dict["trigger_name"] == ["tech_upgrade_summary"]:
    # 	m_dict["trigger_date"] = m_r_news_triggers["date"]

    # if m_dict["trigger_name"] == ["market_summary"] or m_dict["trigger_name"] == ["result_summary"] or m_dict["trigger_name"] == ["smallcap_market_summary"] or m_dict["trigger_name"] == ["midcap_market_summary"] or m_dict["trigger_name"] == ["largecap_market_summary"] or m_dict["trigger_name"] == ["sector_summary"] or m_dict["trigger_name"] == ["downgrade_summary"] or m_dict["trigger_name"] == ["upgrade_summary"] or m_dict["trigger_name"] == ["tech_dot_summary"] or m_dict["trigger_name"] == ["new_stock_added"] or m_dict["trigger_name"] == ["high_return_in_period"] or m_dict["trigger_name"] == ["52_week_high_summary"] or m_dict["trigger_name"] == ["updated_Downgrade_summary"] or m_dict["trigger_name"] == ["tech_upgrade_summary"] or m_dict["trigger_name"] == ["tech_downgrade_summary"] or m_dict["trigger_name"] == ["tech_upgrade_summary"] or m_dict["trigger_name"] == ["index_summary"]:
    #     m_dict["trigger_date"] = m_r_news_triggers["date"]
    #     if m_r_news_triggers["index_id"] in [None]:
    #         m_dict["index_id"] = 0
    #     else:
    #         m_dict["index_id"] = m_r_news_triggers["index_id"]
    #     m_dict["bse_nse"] = m_r_news_triggers["bse_nse"]
    #     if "mcap_id" in m_r_news_triggers and m_r_news_triggers["mcap_id"] not in [None]:
    #         m_dict["mcap_id"] = m_r_news_triggers["mcap_id"]
    #     else:
    #         m_dict["mcap_id"] = 0
    #     m_comp_name = ""
    #     m_dict["mcap_grade"] = None
    #     m_dict["turn_arround"] = None
    #     m_dict["turn_arround_entry_date"] = None
    #     m_dict["momentumnow"] = None
    #     m_dict["momentumnow_entry_date"] = None
    #     m_dict["consistant_performer"] = None
    #     m_dict["consistant_performer_entry_date"] = None
    #     m_dict["mojostocks"] = None
    #     m_dict["mojostocks_entry_date"] = None
    #     m_dict["day_change"] = None
    #     m_dict["fin_grade"] = None
    #     m_dict["upcoming_result"] = None
    #     m_dict["result"] = None
    #     m_dict["result_quarter"] = None
    # else:
    #     m_dict["trigger_date"] = m_r_news_triggers["trigger_date"]
    #     m_dict["mcap_grade"] = m_r_news_triggers["mcap_grade"]
    #     m_dict["turn_arround"] = m_r_news_triggers["turn_arround"]
    #     m_dict["turn_arround_entry_date"] = m_r_news_triggers["turn_arround_entry_date"]
    #     m_dict["momentumnow"] = m_r_news_triggers["momentumnow"]
    #     m_dict["momentumnow_entry_date"] = m_r_news_triggers["momentumnow_entry_date"]
    #     m_dict["consistant_performer"] = m_r_news_triggers["consistant_performer"]
    #     m_dict["consistant_performer_entry_date"] = m_r_news_triggers["consistant_performer_entry_date"]
    #     m_dict["mojostocks"] = m_r_news_triggers["mojostocks"]
    #     m_dict["mojostocks_entry_date"] = m_r_news_triggers["mojostocks_entry_date"]
    #     m_dict["comp_name"] = m_r_news_triggers["comp_name"].replace(" Ltd", "").replace(" Ltd.", "")
    #     m_dict["day_change"] = str(m_r_news_triggers["stock_1d_return"]).replace("%", "") + "%"
    #     #if m_fin_grade != None:
    #     #	m_dict["fin_grade"] = m_fin_grade
    #     if "fin_grade" in m_r_news_triggers:
    #         m_dict["fin_grade"] = m_r_news_triggers["fin_grade"]
    #     else:
    #         m_dict["fin_grade"] = m_fin_grade
    #     m_comp_name = m_r_news_triggers["comp_name"].replace("Ltd", "").replace("Ltd.", "")
    #     m_dict["upcoming_result"] = m_r_news_triggers["upcoming_result"]
    #     m_dict["result"] = m_r_news_triggers["result"]
    #     m_dict["result_quarter"] = m_r_news_triggers["result_quarter"]
    #else:
    #	m_dict["trigger_date"] = ""

    if ("market_summary" in m_dict["trigger_name"] or 
        "result_summary" in m_dict["trigger_name"] or 
        "smallcap_market_summary" in m_dict["trigger_name"] or 
        "midcap_market_summary" in m_dict["trigger_name"] or 
        "largecap_market_summary" in m_dict["trigger_name"] or 
        "sector_summary" in m_dict["trigger_name"] or 
        "downgrade_summary" in m_dict["trigger_name"] or 
        "upgrade_summary" in m_dict["trigger_name"] or 
        "tech_dot_summary" in m_dict["trigger_name"] or 
        "new_stock_added" in m_dict["trigger_name"] or 
        "high_return_in_period" in m_dict["trigger_name"] or 
        "52_week_high_summary" in m_dict["trigger_name"] or 
        "updated_Downgrade_summary" in m_dict["trigger_name"] or 
        "tech_upgrade_summary" in m_dict["trigger_name"] or 
        "tech_downgrade_summary" in m_dict["trigger_name"] or 
        "index_summary" in m_dict["trigger_name"]):
        
        # This is the original, correct logic for summary triggers
        m_dict["trigger_date"] = m_r_news_triggers["date"]
        if m_r_news_triggers.get("index_id") is None:
            m_dict["index_id"] = 0
        else:
            m_dict["index_id"] = m_r_news_triggers["index_id"]
        m_dict["bse_nse"] = m_r_news_triggers["bse_nse"]
        if "mcap_id" in m_r_news_triggers and m_r_news_triggers["mcap_id"] is not None:
            m_dict["mcap_id"] = m_r_news_triggers["mcap_id"]
        else:
            m_dict["mcap_id"] = 0
        m_comp_name = ""
        m_dict["mcap_grade"] = None
        m_dict["turn_arround"] = None
        m_dict["turn_arround_entry_date"] = None
        m_dict["momentumnow"] = None
        m_dict["momentumnow_entry_date"] = None
        m_dict["consistant_performer"] = None
        m_dict["consistant_performer_entry_date"] = None
        m_dict["mojostocks"] = None
        m_dict["mojostocks_entry_date"] = None
        m_dict["day_change"] = None
        m_dict["fin_grade"] = None
        m_dict["upcoming_result"] = None
        m_dict["result"] = None
        m_dict["result_quarter"] = None
    else:
        # This is the original, correct logic for stock-specific triggers
        m_dict["trigger_date"] = m_r_news_triggers["trigger_date"]
        m_dict["mcap_grade"] = m_r_news_triggers["mcap_grade"]
        m_dict["turn_arround"] = m_r_news_triggers["turn_arround"]
        m_dict["turn_arround_entry_date"] = m_r_news_triggers["turn_arround_entry_date"]
        m_dict["momentumnow"] = m_r_news_triggers["momentumnow"]
        m_dict["momentumnow_entry_date"] = m_r_news_triggers["momentumnow_entry_date"]
        m_dict["consistant_performer"] = m_r_news_triggers["consistant_performer"]
        m_dict["consistant_performer_entry_date"] = m_r_news_triggers["consistant_performer_entry_date"]
        m_dict["mojostocks"] = m_r_news_triggers["mojostocks"]
        m_dict["mojostocks_entry_date"] = m_r_news_triggers["mojostocks_entry_date"]
        m_dict["comp_name"] = m_r_news_triggers["comp_name"].replace(" Ltd", "").replace(" Ltd.", "")
        m_dict["day_change"] = str(m_r_news_triggers["stock_1d_return"]).replace("%", "") + "%"
        if "fin_grade" in m_r_news_triggers:
            m_dict["fin_grade"] = m_r_news_triggers["fin_grade"]
        else:
            m_dict["fin_grade"] = m_fin_grade
        m_comp_name = m_r_news_triggers["comp_name"].replace("Ltd", "").replace("Ltd.", "")
        m_dict["upcoming_result"] = m_r_news_triggers["upcoming_result"]
        m_dict["result"] = m_r_news_triggers["result"]
        m_dict["result_quarter"] = m_r_news_triggers["result_quarter"]

    # --- END OF FIX ---


    m_dict["status"] = 0

    m_d_fin_grade = {"outstanding":"green", "very positive":"green", "positive":"green", "flat":"orange", "negative":"red", "very negative":"red"}
    m_d_stock_grade = {"Strong Buy":"green", "Buy":"green", "Hold":"orange", "Sell":"red", "Strong Sell":"red"}
    m_d_price_theme = {"52wk_high":"green", "52wk_high close":"green", "day high":"green", "all_time_high":"green", "52wk_low":"red", "52wk_low close":"red", "day low":"red", "all_time_low":"red", "going_up_daily":"green", "going_down_daily":"red"}

    if "result" in m_r_news_triggers["trigger_name"]:
        m_dict["published"] = datetime.strptime(m_r_news_triggers["date_time_trigger"], "%Y-%m-%d %H:%M:%S") #datetime.strptime(m_r_news_triggers["result"] + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
    elif "score grade change" in m_r_news_triggers["trigger_name"]:
        m_dict["published"] = datetime.strptime(m_r_news_triggers["date_time_trigger"], "%Y-%m-%d %H:%M:%S") #datetime.strptime(m_r_news_triggers["scoreTxtChngDate"] + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
    else: #if "52wk_high" in m_r_news_triggers["trigger_name"]:
        m_dict["published"] = datetime.strptime(m_r_news_triggers["date_time_trigger"], "%Y-%m-%d %H:%M:%S") #datetime.strptime(m_r_news_triggers["trigger_date"] + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
    #else:
    #	m_dict["published"] = datetime.now()

    if "result" in m_r_news_triggers["trigger_name"]:
        if "fin_grade" in m_dict and m_dict["fin_grade"] in m_d_fin_grade:
            m_dict["theme"] = m_d_fin_grade[m_dict["fin_grade"]]
        else:
            m_dict["theme"] = "grey"
    elif "score grade change" in m_r_news_triggers["trigger_name"]:
        m_dict["published"] = datetime.strptime(m_r_news_triggers["date_time_trigger"], "%Y-%m-%d %H:%M:%S") #datetime.strptime(m_r_news_triggers["scoreTxtChngDate"] + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")

        if m_dict["scoreText"] in m_d_stock_grade:
            m_dict["theme"] = m_d_stock_grade[m_dict["scoreText"]]
        else:
            m_dict["theme"] = "grey"
    else:
        if m_r_news_triggers["trigger_name"][0] in m_d_price_theme:
            m_dict["theme"] = m_d_price_theme[m_r_news_triggers["trigger_name"][0]]

    # --- ADD THIS LOGIC ---
    # Determine bucket and priority based on trigger_name
    # Determine bucket and priority based on trigger_name
    current_trigger = None
    if m_dict["trigger_name"] and isinstance(m_dict["trigger_name"], list) and len(m_dict["trigger_name"]) > 0:
        # Assuming the actual trigger is the first element in the list
        current_trigger = m_dict["trigger_name"][0]

    if current_trigger:
        # Look up in the mapping dictionary (defined globally)
        bucket_info = TRIGGER_BUCKET_PRIORITY_MAPPING.get(current_trigger)
        if bucket_info:
            # --- If a mapping exists, use it ---
            if "bucket" in bucket_info:
                m_dict["bucket"] = bucket_info["bucket"]
            if "priority" in bucket_info:
                m_dict["priority"] = bucket_info["priority"]
            print(f"Mapped trigger '{current_trigger}' to Bucket: {m_dict.get('bucket')}, Priority: {m_dict.get('priority')}")
        else:
            # --- If no mapping found, assign default values --- # MODIFIED BLOCK
            m_dict["bucket"] = 6
            m_dict["priority"] = 0
            print(f"No specific bucket/priority mapping found for trigger: '{current_trigger}'. Assigning defaults: Bucket={m_dict['bucket']}, Priority={m_dict['priority']}")
            # --- End of Modified Block ---
    else:
        # --- If trigger name itself is invalid/missing ---
        # Optional: Decide if you want defaults here too, or leave them unset.
        # Leaving them unset is probably safer unless explicitly required.
        # m_dict["bucket"] = 6  # Uncomment if defaults are needed even for missing triggers
        # m_dict["priority"] = 0 # Uncomment if defaults are needed even for missing triggers
        print("Trigger name is missing or not in expected format. Bucket/priority may not be assigned.")
    # --- END OF ADDED LOGIC ---

    # ----------------------------------------------------------------------
    # Generate news content along with tracking metrics from generate_news
    # ----------------------------------------------------------------------
    result = await generate_news(
        m_dict["stockid"], # <<< ADD THIS
        m_comp_name,
        m_r_news_triggers["industry"],
        m_r_news_triggers["sector"],
        m_dict["score"],
        m_dict["scoreText"],
        m_dict["upcoming_result"],
        m_dict["result"],
        m_dict["result_quarter"],
        m_dict["trigger_name"],
        m_r_news_triggers["data"],
        m_dict["prevScoreText"],
        m_dict["scoreTxtChngDate"],
        m_dict["trigger_date"],
        m_dict["mcap_grade"],
        m_dict["turn_arround"],
        m_dict["turn_arround_entry_date"],
        m_dict["momentumnow"],
        m_dict["momentumnow_entry_date"],
        m_dict["consistant_performer"],
        m_dict["consistant_performer_entry_date"],
        m_dict["mojostocks"],
        m_dict["mojostocks_entry_date"],
        m_dict["day_change"]
    )
    # Check how many values were returned.
    if len(result) == 11:
        (m_dict["generated_article"],
        m_dict["generated_summary"],
        m_dict["generated_headline"],
        m_dict["data"],
        m_dict["generated_article_unpaid"],
        m_dict["generated_summary_unpaid"],
        m_dict["generated_headline_unpaid"],
        m_dict["generated_article_crawler"],
        m_dict["generated_summary_crawler"],
        m_dict["generated_headline_crawler"],
        tracking_data) = result
    else:
        (m_dict["generated_article"],
        m_dict["generated_summary"],
        m_dict["generated_headline"],
        m_dict["data"],
        m_dict["generated_article_unpaid"],
        m_dict["generated_summary_unpaid"],
        m_dict["generated_headline_unpaid"],
        m_dict["generated_article_crawler"],
        m_dict["generated_summary_crawler"],
        m_dict["generated_headline_crawler"]) = result
        tracking_data = {}  # Fallback if tracking info isn't returned

    # Store tracking info in the document
    m_dict["tracking"] = tracking_data

    print("Final m_dict before DB update:") # Add this line for debugging
    print(m_dict)                        # Add this line for debugging

    # Update news_stories collection if generated content is valid
    if (len(m_dict["generated_article"]) > 10 and 
        len(m_dict["generated_summary"]) > 10 and 
        len(m_dict["generated_headline"]) > 10):
        m_dict["inserted"] = datetime.now()
        m_filter = {"newsid": m_dict["newsid"]}
        m_news_stories.update_one(m_filter, {"$set": m_dict}, upsert=True)
        m_filter = {"_id": m_dict["newsid"]}
        m_news_triggers.update_one(m_filter, {"$set": {"status": 1}})
        print("NEWS UPDATED")
    else:
        m_filter = {"_id": m_dict["newsid"]}
        m_news_triggers.update_one(m_filter, {"$set": {"status": 2}})

    # except KeyError as e:
    #     # This block catches the error, logs it, and updates the status to 2 (failed)
    #     print(f"Skipping newsid {m_r_news_triggers['_id']} due to KeyError: {e}. Invalid score text provided.")
    #     m_filter = {"_id": m_r_news_triggers["_id"]}
    #     m_news_triggers.update_one(m_filter, {"$set": {"status": 2, "error_message": f"KeyError: {str(e)}"}})
    
    # --- END: MODIFIED SECTION ---


    end_time = time.time()
    task_duration = end_time - start_time
    print(f"Task completed in {task_duration:.2f} seconds")	

async def get_news_data_async():
    m_trigger_name = ["52wk_high"] #score grade change"] #day low"] #day high"] #52wk_low close"] #52wk_high close"] #52wk_low"] #52wk_high"] #result"] #52wk_low close"]
    m_l_stockids = []
    m_d_fin_grade = {"outstanding":"green", "very positive":"green", "positive":"green", "flat":"orange", "negative":"red", "very negative":"red"}
    m_d_stock_grade = {"Strong Buy":"green", "Buy":"green", "Hold":"orange", "Sell":"red", "Strong Sell":"red"}
    m_d_price_theme = {"52wk_high":"green", "52wk_high close":"green", "day high":"green", "all_time_high":"green", "52wk_low":"red", "52wk_low close":"red", "day low":"red", "all_time_low":"red", "going_up_daily":"green", "going_down_daily":"red"}
    m_today = datetime.today().strftime("%Y-%m-%d")

    start_batch_time = time.time()
    tasks = []


    m_filter = {
            "date": {"$gte": "2025-02-05"},
            "country_id": 34,
            "status": 0,
            "trigger_name": {"$nin": ["bulk_block_deal"]},
            "$or": [
                {"trigger_name": {"$ne": "ipo_listing"}, "scoreText": {"$nin": ["Not Rated"]}},
                {"trigger_name": "ipo_listing"}
            ]
        }




	
	#m_filter = {"trigger_name":m_trigger_name}
	#m_l_stockids = m_news_stories.distinct("stockid", m_filter)
	
	#{"trigger_name":["result_summary"]}
	#{"trigger_name":["market_summary"]} #
	# m_filter = {"date":{"$gte":"2025-02-05"}, "scoreText":{"$nin":["Not Rated"]}, "status":0, "trigger_name":{"$nin":["bulk_block_deal"]}} #, "trigger_name":["market_summary"]} #, "trigger_name":["market_summary"]} #, "trigger_name":{"$ne":["tech_downgrade_summary"]}, "trigger_name":["market_summary"]} #, "stockid":{"$nin":m_l_stockids}} 
	#m_filter = {"date":{"$gte":"2025-01-19"}, "status": 1}
    print(m_filter)
    count = m_news_triggers.count_documents(m_filter)
    print(f"Found {count} documents matching the filter.")
    m_c_news_triggers = m_news_triggers.find(m_filter, batch_size=25).sort("_id", 1) #.limit(25)
    for m_r_news_triggers in m_c_news_triggers:

        task = asyncio.create_task(process_trigger(m_r_news_triggers))
        tasks.append(task)
        # Log the current number of tasks being processed
        print(f"Current active tasks: {len(tasks)}")
        if len(tasks) == 5:  # Once 5 tasks are added, wait for them to complete
            await asyncio.gather(*tasks)
            batch_end_time = time.time()  # End time for the batch
            batch_duration = batch_end_time - start_batch_time
            print(f"Completed 5 tasks in {batch_duration:.2f} seconds")
            tasks = []  # Clear the task list after running 5 tasks
            start_batch_time = time.time()  # Reset the batch start time

    if tasks:
        await asyncio.gather(*tasks)
        batch_end_time = time.time()  # End time for remaining tasks
        batch_duration = batch_end_time - start_batch_time
        print(f"Completed remaining tasks in {batch_duration:.2f} seconds")

# Run the async function
asyncio.run(get_news_data_async())
