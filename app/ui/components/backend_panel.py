from nicegui import ui
import json

def create_log_entry(container, title: str, content: str, entry_type: str = "info"):
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
        with ui.card().classes(f'w-full border-l-4 mb-2 p-3 shadow-md {styles}'):
            ui.label(title).classes('font-bold text-sm uppercase tracking-wider mb-1 opacity-80')
            
            # Format JSON content beautifully if possible, otherwise show raw text
            try:
                # Try to parse as JSON to pretty-print
                if isinstance(content, dict):
                    formatted_content = json.dumps(content, indent=2)
                else:
                    parsed = json.loads(content)
                    formatted_content = json.dumps(parsed, indent=2)
            except (ValueError, TypeError):
                formatted_content = str(content)
                
            ui.code(formatted_content).classes('text-xs bg-transparent p-0 m-0 whitespace-pre-wrap break-all')