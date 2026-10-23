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
        
        with ui.link(target='/').classes('flex items-center gap-2 no-underline'):
            ui.icon('hub', color='primary', size='sm')
            ui.label('PontIA Connect: GenAI Engine').classes('text-2xl font-bold text-primary')
        
        with ui.row().classes('gap-6'):
            with ui.link(target='/agent').classes('flex items-center gap-1 text-white hover:text-secondary transition-colors no-underline'):
                ui.icon('smart_toy', size='sm')
                ui.label('Agent').classes('text-lg font-semibold')
                
            with ui.link(target='/generator').classes('flex items-center gap-1 text-white hover:text-secondary transition-colors no-underline'):
                ui.icon('auto_awesome', size='sm')
                ui.label('Generation').classes('text-lg font-semibold')
                
            with ui.link(target='/tokens').classes('flex items-center gap-1 text-white hover:text-secondary transition-colors no-underline'):
                ui.icon('data_object', size='sm')
                ui.label('Tokens').classes('text-lg font-semibold')
                
            with ui.link(target='/arithmetic').classes('flex items-center gap-1 text-white hover:text-secondary transition-colors no-underline'):
                ui.icon('calculate', size='sm')
                ui.label('Arithmetic').classes('text-lg font-semibold')