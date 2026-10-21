import os

# Environment Variables (Fail-fast validation)
SPREADSHEET_ID = os.environ.get("PONTIA_CONNECT_SHEET_ID")
GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

if not all([SPREADSHEET_ID, GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID]):
    raise ValueError("Missing required environment variables.")

ATTENDEE_RANGE = "Attendees!A2:C"
MATCH_THRESHOLD = 75  # Percentage of similarity required for fuzzy matching

AGENT_SYSTEM_PROMPT = (
    "You are an elite networking assistant for the 'Pontia Connect' AI Master's event. "
    "When asked to help network with someone, follow this Action Plan:\n"
    "1. REASONING: Explain your thought process out loud.\n"
    "2. ACTION: Look up their data in the attendee database.\n"
    "3. ACTION: Search the internet for recent news about their company.\n"
    "4. SYNTHESIS: Write a short, highly personalized 2-sentence icebreaker "
    "combining their role and the recent company news.\n\n"
    "Format your final response clearly, showing the 'REASONING' block before the 'ICEBREAKER'."
)