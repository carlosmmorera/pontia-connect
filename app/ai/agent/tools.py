"""
Pontia Connect Networking Agent Tools.
Contains ADK-compatible tools for real-time external data retrieval.
"""

from loguru import logger
from thefuzz import fuzz
from functools import lru_cache

from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.ai.agent import config

@lru_cache(maxsize=128)
def get_attendee_info(name: str) -> str:
    """
    Retrieves the attendee's profile from the private Pontia Connect 
    Google Sheet. Uses Google Application Default Credentials (ADC) for 
    secure authentication. It retrieves with typo tolerance.
    Results are cached in memory to avoid redundant API calls.
    
    Args:
        name: The full name of the attendee to look up.
        
    Returns:
        A formatted string containing the attendee's role and company, 
        or a fallback message.
    """
    logger.info(f"Fetching attendee info for: {name}")
    try:
        # Load ADC credentials scoped for Google Sheets read-only access
        credentials, _ = default(
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        # Execute the API call
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=config.SPREADSHEET_ID,
            range=config.ATTENDEE_RANGE
        ).execute()
        values = result.get('values', [])
        
        if not values:
            return "No data found in the attendee database."
            
        target_name = name.lower().strip()
        
        best_match = None
        highest_score = 0
        
        for row in values:
            if len(row) >= 3:
                candidate_name = row[0].lower().strip()
                # Use token set ratio to handle middle names or swapped names 
                # (e.g., "Perez Juan" vs "Juan Perez")
                score = fuzz.token_set_ratio(target_name, candidate_name)
                
                if score > highest_score:
                    highest_score = score
                    best_match = row
                    
        if highest_score >= config.MATCH_THRESHOLD and best_match:
            role = best_match[1]
            company = best_match[2]
            logger.info(f"Match found: {best_match[0]} with score {highest_score}")
            return f"Attendee Found: {best_match[0]} is currently {role} at {company}."
                
        return f"Attendee '{name}' not found in the Pontia Connect database (Best match score: {highest_score})."
        
    except HttpError as err:
        logger.error(f"Google Sheets API error: {err}")
        return "Internal system error: Unable to connect to the database right now."
    except Exception as err:
        logger.error(f"Unexpected error retrieving attendee: {err}")
        return "Internal system error: Database lookup failed."

@lru_cache(maxsize=128)
def search_recent_company_news(company_name: str) -> str:
    """
    Searches the internet using Google Custom Search API.
    Cached to prevent duplicate quota usage.
    """
    logger.info(f"Searching Google for: {company_name}")
    try:
        if not config.GOOGLE_SEARCH_API_KEY or not config.GOOGLE_SEARCH_ENGINE_ID:
            logger.warning("Google Search API credentials missing. Returning fallback.")
            return f"Cannot search news for {company_name} because search is not configured."

        service = build(
            "customsearch", 
            "v1", 
            developerKey=config.GOOGLE_SEARCH_API_KEY
        )
        query = f"{company_name} artificial intelligence news"
        
        # Execute Google Search query
        result = service.cse().list(
            q=query,
            cx=config.GOOGLE_SEARCH_ENGINE_ID,
            num=3,          # Limit to top 3 results
            dateRestrict="y1" # Restrict to past year (y1) or past month (m1)
        ).execute()
        
        search_items = result.get("items", [])
        if not search_items:
            return f"No recent AI news found for {company_name}."
            
        headlines = [
            f"- {item.get('title')}: {item.get('snippet')}" 
            for item in search_items
        ]
        return "Recent News from Google Search:\n" + "\n".join(headlines)
        
    except HttpError as err:
        logger.error(f"Google Search API failed: {err}")
        return f"Could not retrieve news for {company_name} due to an API error."