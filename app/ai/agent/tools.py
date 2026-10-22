"""
Pontia Connect Networking Agent Tools.
Contains ADK-compatible tools for real-time external data retrieval.
"""

from typing import Optional
from loguru import logger
from thefuzz import fuzz
from functools import lru_cache

from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import get_settings

settings = get_settings()

@lru_cache(maxsize=128)
def _fetch_attendee_from_sheets(name: str) -> Optional[str]:
    """Internal function to handle the cached Google Sheets API call."""
    try:
        credentials, _ = default(
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=settings.SPREADSHEET_ID,
            range=settings.ATTENDEE_RANGE
        ).execute()
        return result.get('values', [])
    except HttpError as err:
        logger.error(f"Google Sheets API error: {err}")
        return None
    except Exception as err:
        logger.error(f"Unexpected error retrieving attendee: {err}")
        return None

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
    values = _fetch_attendee_from_sheets(name)

    if values is None:
        return "Internal system error: Unable to connect to the database right now."
    
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
                
    if highest_score >= settings.MATCH_THRESHOLD and best_match:
        role = best_match[1]
        company = best_match[2]
        logger.info(f"Match found: {best_match[0]} with score {highest_score}")
        return f"Attendee Found: {best_match[0]} is currently {role} at {company}."

    if best_match:
        return (f"There is no attendee with name '{name}' in the Pontia Connect"
            + " database. However the best match is with the attendee with "
            + f"name {best_match[0]} (Best match score: {highest_score}).")

    return "No attendee found in the Pontia Connect database"
