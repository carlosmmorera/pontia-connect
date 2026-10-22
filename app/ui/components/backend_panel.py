from nicegui import ui
import json
import html
from typing import Optional

def format_content(content):
    """Helper to safely format dicts/JSON strings or return plain text."""
    try:
        if isinstance(content, dict):
            return json.dumps(content, indent=2)
        else:
            parsed = json.loads(content)
            return json.dumps(parsed, indent=2)
    except (ValueError, TypeError):
        return str(content)

def render_code_block(content_str: str):
    """Helper to render a code block with 'Read more' if it's too long."""

    wrap_style = 'white-space: pre-wrap !important; word-break: break-word !important; overflow-wrap: break-word !important; overflow-x: hidden !important; font-family: monospace; margin: 0;'
    safe_html = html.escape(content_str)

    if len(content_str) > 300:
        with ui.expansion('Read more...', icon='unfold_more').classes('w-full max-w-full overflow-hidden text-xs bg-black/30 rounded'):
            ui.html(f'<pre style="{wrap_style} padding: 0.5rem;">{safe_html}</pre>').classes('w-full max-w-full bg-transparent text-xs')
    else:
        ui.html(f'<pre style="{wrap_style} padding: 0;">{safe_html}</pre>').classes('w-full max-w-full bg-transparent text-xs')

def create_log_entry(container, title: str, content: str, entry_type: str = "info", llm_input: Optional[str] = None):
    """
    Creates a styled, visual card for a backend log entry.
    
    Args:
        container: The NiceGUI container (e.g., ui.scroll_area) to append to.
        title: The header for the log entry (e.g., "TOOL CALL: get_attendee_info").
        content: The detailed payload, prompt, or response.
        entry_type: 'prompt', 'tool_call', 'tool_result', 'final_text', or 'info' to dictate styling.
    """
    # Color mapping for different event types to make parsing visual
    color_map = {
        "prompt": "border-blue-500 bg-blue-900/20 text-blue-300",
        "tool_call": "border-yellow-500 bg-yellow-900/20 text-yellow-300",
        "tool_result": "border-purple-500 bg-purple-900/20 text-purple-300",
        "final_text": "border-green-500 bg-green-900/20 text-green-300",
        "info": "border-gray-500 bg-gray-900/20 text-gray-300"
    }
    
    styles = color_map.get(entry_type, color_map["info"])
    
    with container:
        with ui.card().classes(f'w-full max-w-full overflow-hidden border-l-4 mb-4 p-4 shadow-md {styles}'):
            ui.label(title).classes('font-bold text-sm uppercase tracking-wider mb-2 opacity-90')
            
            if llm_input:
                ui.label("▼ INPUT TO LLM").classes('text-[10px] font-bold text-gray-400 mb-1 tracking-wide')
                render_code_block(format_content(llm_input))
                ui.label("▼ OUTPUT FROM LLM").classes('text-[10px] font-bold text-gray-400 mt-4 mb-1 tracking-wide')
            
            render_code_block(format_content(content))