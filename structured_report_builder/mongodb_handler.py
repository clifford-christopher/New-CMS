"""
MongoDB Handler for fetching historical data from mojo_dots_hist collection
"""
import pymongo
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

class MongoDBHandler:
    """Handler for fetching historical data from MongoDB"""

    def __init__(self):
        """
        Initialize MongoDB connection
        Reads connection string from mongourl_mmfrontend.txt
        """
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        try:
            # Read connection string from file
            with open('mongourl_mmfrontend.txt', 'r') as f:
                connection_string = f.read().strip()
            self.logger.info("MongoDB URL loaded from mongourl_mmfrontend.txt")

            self.client = pymongo.MongoClient(connection_string)
            self.db = self.client['mmfrontend']
            self.collection = self.db['mojo_dots_hist']

            self.logger.info("MongoDB connection initialized successfully")
        except FileNotFoundError:
            self.logger.error("mongourl_mmfrontend.txt not found. Please create this file with MongoDB connection string.")
            raise
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_valuation_grade_history(self, stock_id: int, limit: int = 5) -> List[Dict]:
        """
        Get valuation grade history for a stock
        Returns last N grade changes (not just last N records)

        Args:
            stock_id: Stock ID to fetch data for
            limit: Number of grade changes to return (default 5)

        Returns:
            List of valuation grade changes with dates
        """
        try:
            # Query MongoDB for this stock, sorted by date descending
            query = {'stockid': stock_id}

            # Get records sorted by date descending
            cursor = self.collection.find(query).sort('date', -1)

            # Process to find grade changes
            grade_changes = []
            prev_grade = None
            prev_date = None

            for doc in cursor:
                current_grade = doc.get('valuation_grade', '').lower()
                current_date = doc.get('date', '')

                # Skip if no grade
                if not current_grade:
                    continue

                # On first iteration, just save as previous
                if prev_grade is None:
                    prev_grade = current_grade
                    prev_date = current_date
                    continue

                # If grade changed, record the change
                if current_grade != prev_grade and prev_date:
                    grade_changes.append({
                        'from_grade': current_grade,  # older grade
                        'to_grade': prev_grade,       # newer grade
                        'date': prev_date,             # date of change
                        'formatted_date': self._format_date(prev_date)
                    })

                    # Stop if we have enough changes
                    if len(grade_changes) >= limit:
                        break

                # Update previous values
                prev_grade = current_grade
                prev_date = current_date

            return grade_changes

        except Exception as e:
            self.logger.error(f"Error fetching valuation history: {e}")
            return []

    def get_current_valuation_grade(self, stock_id: int) -> Optional[str]:
        """
        Get the current (most recent) valuation grade for a stock

        Args:
            stock_id: Stock ID to fetch data for

        Returns:
            Current valuation grade or None
        """
        try:
            # Get the most recent record
            query = {'stockid': stock_id}
            latest_doc = self.collection.find_one(
                query,
                sort=[('date', -1)]
            )

            if latest_doc:
                grade = latest_doc.get('valuation_grade', '')
                return self._format_valuation_grade(grade) if grade else None

            return None

        except Exception as e:
            self.logger.error(f"Error fetching current valuation grade: {e}")
            return None

    def get_technical_trend_history(self, stock_id: int, limit: int = 5) -> List[Dict]:
        """
        Get technical trend history for a stock
        Returns last N trend changes (not just last N records)

        Args:
            stock_id: Stock ID to fetch data for
            limit: Number of trend changes to return (default 5)

        Returns:
            List of technical trend changes with dates
        """
        try:
            # Query MongoDB for this stock, sorted by date descending
            query = {'stockid': stock_id}

            # Get records sorted by date descending
            cursor = self.collection.find(query).sort('date', -1)

            # Process to find trend changes
            trend_changes = []
            prev_trend = None
            prev_date = None

            for doc in cursor:
                current_trend = doc.get('tech_grade', '').lower()
                current_date = doc.get('date', '')

                # Skip if no trend
                if not current_trend:
                    continue

                # On first iteration, just save as previous
                if prev_trend is None:
                    prev_trend = current_trend
                    prev_date = current_date
                    continue

                # If trend changed, record the change
                if current_trend != prev_trend and prev_date:
                    trend_changes.append({
                        'date': prev_date,             # date of change
                        'formatted_date': self._format_date(prev_date),
                        'trend_change': self._format_technical_trend(prev_trend),  # new trend
                        'previous_trend': self._format_technical_trend(current_trend)  # old trend
                    })

                    # Stop if we have enough changes
                    if len(trend_changes) >= limit:
                        break

                # Update previous values
                prev_trend = current_trend
                prev_date = current_date

            return trend_changes

        except Exception as e:
            self.logger.error(f"Error fetching technical trend history: {e}")
            return []

    def get_quality_grade_history(self, stock_id: int, limit: int = 5) -> List[Dict]:
        """
        Get quality grade history for a stock
        Returns last N grade changes (not just last N records)

        Args:
            stock_id: Stock ID to fetch data for
            limit: Number of grade changes to return (default 5)

        Returns:
            List of quality grade changes with dates
        """
        try:
            # Query MongoDB for this stock, sorted by date descending
            query = {'stockid': stock_id}

            # Get records sorted by date descending
            cursor = self.collection.find(query).sort('date', -1)

            # Process to find grade changes
            grade_changes = []
            prev_grade = None
            prev_date = None

            for doc in cursor:
                current_grade = doc.get('quality_grade', '').lower()
                current_date = doc.get('date', '')

                # Skip if no grade
                if not current_grade:
                    continue

                # On first iteration, just save as previous
                if prev_grade is None:
                    prev_grade = current_grade
                    prev_date = current_date
                    continue

                # If grade changed, record the change
                if current_grade != prev_grade and prev_date:
                    grade_changes.append({
                        'date': prev_date,             # date of change
                        'formatted_date': self._format_date(prev_date),
                        'grade_change': self._format_quality_grade(prev_grade),  # new grade
                        'previous_grade': self._format_quality_grade(current_grade)  # old grade
                    })

                    # Stop if we have enough changes
                    if len(grade_changes) >= limit:
                        break

                # Update previous values
                prev_grade = current_grade
                prev_date = current_date

            return grade_changes

        except Exception as e:
            self.logger.error(f"Error fetching quality grade history: {e}")
            return []

    def get_current_quality_grade(self, stock_id: int) -> Optional[str]:
        """
        Get the current (most recent) quality grade for a stock

        Args:
            stock_id: Stock ID to fetch data for

        Returns:
            Current quality grade or None
        """
        try:
            # Get the most recent record
            query = {'stockid': stock_id}
            latest_doc = self.collection.find_one(
                query,
                sort=[('date', -1)]
            )

            if latest_doc:
                grade = latest_doc.get('quality_grade', '')
                return self._format_quality_grade(grade) if grade else None

            return None

        except Exception as e:
            self.logger.error(f"Error fetching current quality grade: {e}")
            return None

    def get_score_history(self, stock_id: int, limit: int = 5) -> List[Dict]:
        """
        Get proprietary score history for a stock
        Returns last N rating CHANGES based on final_score_grade field

        Args:
            stock_id: Stock ID to fetch data for
            limit: Number of rating changes to return (default 5)

        Returns:
            List of score changes with dates, scores, ratings, and transitions
        """
        try:
            # Query MongoDB for this stock, sorted by date descending
            query = {'stockid': stock_id}

            # Get records sorted by date descending - get more to find actual changes
            cursor = self.collection.find(query).sort('date', -1)

            records = list(cursor)
            if not records:
                return []

            # First, add the current score
            score_history = []
            current_doc = records[0]
            current_score = current_doc.get('grade_final_score_4_override')
            current_rating = current_doc.get('final_score_grade', '')

            if current_score is not None:
                score_history.append({
                    'date': current_doc.get('date', ''),
                    'formatted_date': 'Current',
                    'score': current_score,
                    'rating': current_rating.capitalize() if current_rating else self._get_rating_from_score(current_score),
                    'change_from': '-'
                })

            # Now find actual RATING changes (not just score changes)
            prev_score = current_score
            prev_rating = current_rating
            prev_date = current_doc.get('date', '')

            for i in range(1, len(records)):
                doc = records[i]
                score = doc.get('grade_final_score_4_override')
                rating = doc.get('final_score_grade', '')
                date = doc.get('date', '')

                # Skip if no score or rating
                if score is None or not rating:
                    continue

                # If RATING changed (not just score), record the change
                if rating.lower() != prev_rating.lower() and prev_rating:
                    # This is where the rating changed TO prev_rating FROM rating
                    score_history.append({
                        'date': prev_date,
                        'formatted_date': self._format_date(prev_date),
                        'score': prev_score,
                        'rating': prev_rating.capitalize() if prev_rating else self._get_rating_from_score(prev_score),
                        'change_from': f"{rating.capitalize()}→{prev_rating.capitalize()}"
                    })

                    # Stop if we have enough changes
                    if len(score_history) >= limit:
                        break

                # Update previous values
                prev_score = score
                prev_rating = rating
                prev_date = date

            return score_history[:limit]

        except Exception as e:
            self.logger.error(f"Error fetching score history: {e}")
            return []

    def _get_rating_from_score(self, score):
        """
        Get rating category from score value

        Args:
            score: Score value (0-100)

        Returns:
            Rating string (e.g., 'Buy', 'Hold', 'Sell')
        """
        if score is None:
            return 'N/A'

        score = int(score)
        if score >= 80:
            return 'Strong Buy'
        elif score >= 70:
            return 'Buy'
        elif score >= 50:
            return 'Hold'
        elif score >= 30:
            return 'Sell'
        else:
            return 'Strong Sell'

    def get_financial_trend_history(self, stock_id: int, limit: int = 5) -> List[Dict]:
        """
        Get financial trend history for a stock with quarter information
        Returns last N trend changes (not just last N records)

        Args:
            stock_id: Stock ID to fetch data for
            limit: Number of trend changes to return (default 5)

        Returns:
            List of financial trend changes with dates and quarters
        """
        try:
            # Query MongoDB for this stock, sorted by date descending
            query = {'stockid': stock_id}

            # Get records sorted by date descending
            cursor = self.collection.find(query).sort('date', -1)

            # Process to find trend changes
            trend_changes = []
            prev_trend = None
            prev_date = None
            prev_quarter = None

            for doc in cursor:
                current_trend = doc.get('fin_grade', '').lower()
                current_date = doc.get('date', '')
                current_quarter = doc.get('quarter', '')

                # Skip if no trend
                if not current_trend:
                    continue

                # On first iteration, just save as previous
                if prev_trend is None:
                    prev_trend = current_trend
                    prev_date = current_date
                    prev_quarter = current_quarter
                    continue

                # If trend changed, record the change
                if current_trend != prev_trend and prev_date:
                    trend_changes.append({
                        'date': prev_date,
                        'formatted_date': self._format_date(prev_date),
                        'quarter': self._format_quarter(prev_quarter),
                        'trend': self._format_financial_trend(prev_trend),  # new trend
                        'previous_trend': self._format_financial_trend(current_trend)  # old trend
                    })

                    # Stop if we have enough changes
                    if len(trend_changes) >= limit:
                        break

                # Update previous values
                prev_trend = current_trend
                prev_date = current_date
                prev_quarter = current_quarter

            return trend_changes

        except Exception as e:
            self.logger.error(f"Error fetching financial trend history: {e}")
            return []

    def _format_quarter(self, quarter):
        """
        Format quarter from YYYYMM to readable format

        Args:
            quarter: Quarter in YYYYMM format (e.g., 202509)

        Returns:
            Formatted quarter string (e.g., "Q3 FY25")
        """
        try:
            if not quarter:
                return ""

            quarter_str = str(quarter)
            if len(quarter_str) != 6:
                return quarter_str

            year = quarter_str[:4]
            month = int(quarter_str[4:])

            # Convert month to quarter
            if month in [1, 2, 3]:
                q = "Q4"
                fy_year = year
            elif month in [4, 5, 6]:
                q = "Q1"
                fy_year = str(int(year) + 1)
            elif month in [7, 8, 9]:
                q = "Q2"
                fy_year = str(int(year) + 1)
            elif month in [10, 11, 12]:
                q = "Q3"
                fy_year = str(int(year) + 1)
            else:
                return quarter_str

            # Return as Q3 FY25 format
            return f"{q} FY{fy_year[-2:]}"

        except:
            return str(quarter) if quarter else ""

    def get_current_technical_trend(self, stock_id: int) -> Optional[str]:
        """
        Get the current (most recent) technical trend for a stock

        Args:
            stock_id: Stock ID to fetch data for

        Returns:
            Current technical trend or None
        """
        try:
            # Get the most recent record
            query = {'stockid': stock_id}
            latest_doc = self.collection.find_one(
                query,
                sort=[('date', -1)]
            )

            if latest_doc:
                trend = latest_doc.get('tech_grade', '')
                return self._format_technical_trend(trend) if trend else None

            return None

        except Exception as e:
            self.logger.error(f"Error fetching current technical trend: {e}")
            return None

    def _format_date(self, date_str: str) -> str:
        """
        Format date string to desired output format

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Formatted date string (e.g., "08-Oct-25")
        """
        try:
            # Parse the date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Format as DD-Mon-YY
            return date_obj.strftime('%d-%b-%y')
        except:
            # If parsing fails, return as is
            return date_str

    def _format_valuation_grade(self, grade: str) -> str:
        """
        Format valuation grade to proper case
        Official grades: Very Risky, Risky, Very Expensive, Expensive, Fair, Attractive, Very Attractive

        Args:
            grade: Raw grade from database (e.g., 'attractive', 'fair')

        Returns:
            Formatted grade string (e.g., 'Attractive', 'Fair')
        """
        grade_map = {
            # MongoDB format -> Display format
            'veryrisky': 'Very Risky',
            'very risky': 'Very Risky',
            'risky': 'Risky',
            'veryexpensive': 'Very Expensive',
            'very expensive': 'Very Expensive',
            'expensive': 'Expensive',
            'fair': 'Fair',
            'attractive': 'Attractive',
            'veryattractive': 'Very Attractive',
            'very attractive': 'Very Attractive'
        }

        # Clean and try exact match
        clean_grade = grade.lower().strip()
        if clean_grade in grade_map:
            return grade_map[clean_grade]

        # Try without spaces
        clean_no_space = clean_grade.replace(' ', '')
        if clean_no_space in grade_map:
            return grade_map[clean_no_space]

        # If not found, return as-is with warning
        print(f"[WARNING] Unknown valuation grade: {grade}")
        return grade.title()

    def _format_technical_trend(self, trend: str) -> str:
        """
        Format technical trend to proper case
        Official grades: Mildly Bullish, Bullish, Sideways, Mildly Bearish, Bearish

        Args:
            trend: Raw trend from database (e.g., 'bullish', 'mildly bearish')

        Returns:
            Formatted trend string (e.g., 'Bullish', 'Mildly Bearish')
        """
        trend_map = {
            # MongoDB format -> Display format
            'mildlybullish': 'Mildly Bullish',
            'mildly bullish': 'Mildly Bullish',
            'bullish': 'Bullish',
            'sideways': 'Sideways',
            'mildlybearish': 'Mildly Bearish',
            'mildly bearish': 'Mildly Bearish',
            'bearish': 'Bearish'
        }

        # Clean and try exact match
        clean_trend = trend.lower().strip()
        if clean_trend in trend_map:
            return trend_map[clean_trend]

        # Try without spaces
        clean_no_space = clean_trend.replace(' ', '')
        if clean_no_space in trend_map:
            return trend_map[clean_no_space]

        # If not found, return as-is with warning
        print(f"[WARNING] Unknown technical trend: {trend}")
        return trend.title()

    def _format_quality_grade(self, grade: str) -> str:
        """
        Format quality grade to proper case
        Official grades: Below Average, Average, Good, Excellent

        Args:
            grade: Raw grade from database (e.g., 'excellent', 'good')

        Returns:
            Formatted grade string (e.g., 'Excellent', 'Good')
        """
        grade_map = {
            # MongoDB format -> Display format
            'belowaverage': 'Below Average',
            'below average': 'Below Average',
            'average': 'Average',
            'good': 'Good',
            'excellent': 'Excellent'
        }

        # Clean and try exact match
        clean_grade = grade.lower().strip()
        if clean_grade in grade_map:
            return grade_map[clean_grade]

        # Try without spaces
        clean_no_space = clean_grade.replace(' ', '')
        if clean_no_space in grade_map:
            return grade_map[clean_no_space]

        # If not found, return as-is with warning
        print(f"[WARNING] Unknown quality grade: {grade}")
        return grade.title()

    def _format_financial_trend(self, trend: str) -> str:
        """
        Format financial trend to proper case
        Official grades: Very Negative, Negative, Flat, Positive, Very Positive, Outstanding

        Args:
            trend: Raw trend from database (e.g., 'positive', 'very positive')

        Returns:
            Formatted trend string (e.g., 'Positive', 'Very Positive')
        """
        trend_map = {
            # MongoDB format -> Display format
            'verynegative': 'Very Negative',
            'very negative': 'Very Negative',
            'negative': 'Negative',
            'flat': 'Flat',
            'positive': 'Positive',
            'verypositive': 'Very Positive',
            'very positive': 'Very Positive',
            'outstanding': 'Outstanding'
        }

        # Clean and try exact match
        clean_trend = trend.lower().strip()
        if clean_trend in trend_map:
            return trend_map[clean_trend]

        # Try without spaces
        clean_no_space = clean_trend.replace(' ', '')
        if clean_no_space in trend_map:
            return trend_map[clean_no_space]

        # If not found, return as-is with warning
        print(f"[WARNING] Unknown financial trend: {trend}")
        return trend.title()

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed")


# Test function
if __name__ == "__main__":
    # Test with TCS (513374)
    handler = MongoDBHandler()

    print("Testing MongoDB Handler for TCS (513374)")
    print("=" * 60)

    # Get current grade
    current_grade = handler.get_current_valuation_grade(513374)
    print(f"\nCurrent Valuation Grade: {current_grade}")

    # Get valuation history
    val_history = handler.get_valuation_grade_history(513374, limit=5)
    print("\nValuation Grade History (Last 5 changes):")
    for i, change in enumerate(val_history, 1):
        print(f"{i}. Changed to {change['to_grade']} from {change['from_grade']}: {change['formatted_date']}")

    # Test with Bank of Maharashtra (291436)
    print("\n" + "=" * 60)
    print("Testing for Bank of Maharashtra (291436)")
    print("=" * 60)

    current_grade = handler.get_current_valuation_grade(291436)
    print(f"\nCurrent Valuation Grade: {current_grade}")

    val_history = handler.get_valuation_grade_history(291436, limit=5)
    print("\nValuation Grade History (Last 5 changes):")
    for i, change in enumerate(val_history, 1):
        print(f"{i}. Changed to {change['to_grade']} from {change['from_grade']}: {change['formatted_date']}")

    handler.close()