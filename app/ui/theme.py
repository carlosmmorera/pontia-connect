"""
UI Theme configuration module.
Defines the standard color palette and typography for the application.
"""

from nicegui import ui

def apply_theme():
    """Applies global styling and color variables to the NiceGUI application."""
    # Modern dark theme palette
    ui.colors(
        primary='#6366f1',     # Indigo
        secondary='#ec4899',   # Pink
        accent='#14b8a6',      # Teal
        dark='#0f172a',        # Slate 900
        positive='#22c55e',    # Green
        negative='#ef4444',    # Red
        info='#3b82f6',        # Blue
        warning='#f59e0b'      # Amber
    )
    
    # Global CSS for consistent component styling
    ui.add_head_html('<link href="/static/style.css" rel="stylesheet">')