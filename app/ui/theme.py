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

    # Global Navigation Header
    with ui.header().classes(
        'items-center justify-between bg-dark border-b border-gray-700 p-4'):
        ui.label(
            'PontIA Connect: GenAI Engine'
        ).classes('text-2xl font-bold text-primary')
        
        with ui.row().classes('gap-6'):
            ui.link('1. Tokens', '/').classes(
                'text-white text-lg font-semibold hover:text-secondary transition-colors no-underline'
            )
            ui.link('2. Arithmetic', '/arithmetic').classes(
                'text-white text-lg font-semibold hover:text-secondary transition-colors no-underline'
            )
            ui.link('3. Generation', '/generator').classes(
                'text-white text-lg font-semibold hover:text-secondary transition-colors no-underline'
            )
            ui.link('4. The Agent', '/agent').classes(
                'text-white text-lg font-semibold hover:text-secondary transition-colors no-underline'
            )