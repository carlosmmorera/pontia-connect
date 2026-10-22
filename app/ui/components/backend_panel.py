from nicegui import ui
import json
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
    if len(content_str) > 300:
        with ui.expansion('Read more...', icon='unfold_more').classes('w-full text-xs bg-black/30 rounded'):
            ui.code(content_str).classes('text-xs bg-transparent p-2 m-0 whitespace-pre-wrap break-words w-full')
    else:
        ui.code(content_str).classes('text-xs bg-transparent p-0 m-0 whitespace-pre-wrap break-words w-full')

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
        with ui.card().classes(f'w-full border-l-4 mb-4 p-4 shadow-md {styles}'):
            ui.label(title).classes('font-bold text-sm uppercase tracking-wider mb-2 opacity-90')
            
            if llm_input:
                ui.label("▼ INPUT TO LLM").classes('text-[10px] font-bold text-gray-400 mb-1 tracking-wide')
                render_code_block(format_content(llm_input))
                ui.label("▼ OUTPUT FROM LLM").classes('text-[10px] font-bold text-gray-400 mt-4 mb-1 tracking-wide')
            
            render_code_block(format_content(content))