"""
Networking Agent UI Page.
Demonstrates the agentic loop, function calling, and reasoning process.
"""

from nicegui import ui
from loguru import logger
from app.ai.agent import NetworkingAgent
from app.ui.theme import apply_theme

from app.ui.components import create_log_entry

def create_agent_page():
    agent = NetworkingAgent()

    @ui.page('/agent')
    def agent_ui():
        apply_theme()

        ui_state = {"revealed": False}
        
        with ui.column().classes('w-full max-w-[90rem] mx-auto p-6'):
            with ui.row().classes('w-full justify-between items-center mb-6'):
                ui.label(
                    "3. Agents: The Illusion of Reasoning"
                ).classes('text-3xl font-extrabold text-white')

                reveal_btn = ui.button(
                    "Reveal the Reality", 
                    icon="visibility", 
                    color="warning"
                ).props('outline')
            
            with ui.row().classes('w-full items-end gap-4 mb-8'):
                attendee_input = ui.input(
                    label="Attendee Name", 
                    value="Carlos Moreno"
                ).classes('w-full max-w-md text-lg')
                
                run_btn = ui.button(
                    "Analyze & Break Ice", 
                    color="primary", 
                    icon="psychology"
                ).classes('h-14 px-6')

            panels_container = ui.row().classes('w-full flex-nowrap gap-8 items-stretch')
            
            with panels_container:
                
                # LEFT PANEL
                left_panel = ui.column().classes('flex-grow w-1/2 transition-all duration-500 bg-gray-800 p-6 rounded-lg shadow-lg')
                
                with left_panel:
                    ui.label("Front-End (The Magic)").classes('text-xl font-bold text-accent mb-4')
                    chat_container = ui.column().classes('w-full gap-4')
                    
                    with ui.row().classes('items-center gap-3 mt-4 hidden') as loading_indicator:
                        ui.spinner('dots', size='md', color='primary')
                        status_text = ui.label("Initializing agent...").classes('text-sm text-gray-400 italic')
                
                # RIGHT PANEL
                right_panel = ui.column().classes('w-1/2 hidden transition-all duration-500 bg-black p-6 rounded-lg shadow-lg border border-gray-700')
                
                with right_panel:
                    ui.label("Back-End (The Reality)").classes('text-xl font-bold text-secondary mb-4')
                    backend_scroll_area = ui.scroll_area().classes('w-full h-[600px] border border-gray-800 rounded p-2')

            def toggle_backend():
                ui_state["revealed"] = not ui_state["revealed"]
                if ui_state["revealed"]:
                    right_panel.classes(remove='hidden')
                    left_panel.classes(remove='w-full')
                    left_panel.classes(add='w-1/2')
                    reveal_btn.set_text("Hide Reality")
                    reveal_btn.props('icon=visibility_off')
                else:
                    right_panel.classes(add='hidden')
                    left_panel.classes(remove='w-1/2')
                    left_panel.classes(add='w-full')
                    reveal_btn.set_text("Reveal the Reality")
                    reveal_btn.props('icon=visibility')
                    
            reveal_btn.on_click(toggle_backend)
            
            async def run_agent():
                chat_container.clear()
                backend_scroll_area.clear()

                loading_indicator.classes(remove='hidden')
                status_text.set_text("Connecting to LLM...")
                run_btn.disable()
                
                name = attendee_input.value
                if not name or not isinstance(name, str) or not name.strip():
                    ui.notify("Please enter a valid attendee name.", type="warning")
                    loading_indicator.classes(add='hidden')
                    run_btn.enable()
                    return

                name = name.strip()
                prompt_text = f"Ayúdame a crear una estrategia de networking para el asistente llamado {name}."
                create_log_entry(
                    backend_scroll_area, 
                    "1. INITIAL SYSTEM PROMPT SENT TO LLM", 
                    prompt_text, 
                    "prompt"
                )
                
                with chat_container:
                    ui.chat_message(
                        f"¿Me puedes ayudar a entablar conversación con {name}?", 
                        name="User", 
                        sent=True
                    )
                
                try:
                    # Iterate through the asynchronous generator
                    async for event in agent.generate_networking_strategy(name):
                        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                            for part in getattr(event.content, "parts", []):
                                
                                # 1. Check for Text (Reasoning or Final Generation)
                                if hasattr(part, 'text') and part.text:
                                    text_content = part.text.strip()

                                    is_final = event.is_final_response()
                                    card_type = "final_text" if is_final else "info"
                                    title = "FINAL LLM TEXT GENERATION" if is_final else "LLM REASONING"
                                    
                                    create_log_entry(
                                        backend_scroll_area, 
                                        title, 
                                        text_content, 
                                        card_type
                                    )

                                    if event.is_final_response():
                                        with chat_container:
                                            ui.chat_message(
                                                text_content, 
                                                name="Pontia Agent", 
                                                avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                                            )
                                    else:
                                        status_text.set_text("Agent is reasoning about the strategy...")
                                        if ui_state["revealed"]:
                                            with chat_container:
                                                ui.chat_message(
                                                    text_content, 
                                                    name="Pontia Agent", 
                                                    avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                                                )

                                # 2. Check for Tool Call Requests
                                if hasattr(part, 'function_call') and part.function_call:
                                    func_name = getattr(part.function_call, 'name', 'UnknownTool')
                                    func_args = str(getattr(part.function_call, 'args', {}))

                                    create_log_entry(
                                        backend_scroll_area, 
                                        f"TOOL CALL REQUESTED: {func_name}", 
                                        func_args, 
                                        "tool_call"
                                    )

                                    status_text.set_text(f"Executing internal tool: {func_name}...")
                                    
                                    if ui_state["revealed"]:
                                        with chat_container:
                                            ui.chat_message(
                                                f"<i>Using tool: {func_name}...</i>", 
                                                name="System", 
                                                text_html=True,
                                                avatar="https://cdn-icons-png.flaticon.com/512/2885/2885412.png"
                                            )

                                # 3. Check for Tool Execution Results
                                if hasattr(part, 'function_response') and part.function_response:
                                    func_name = getattr(part.function_response, 'name', 'UnknownTool')
                                    func_data = str(getattr(part.function_response, 'response', {}))
                                    
                                    create_log_entry(
                                        backend_scroll_area, 
                                        f"TOOL EXECUTION RESULT: {func_name}", 
                                        func_data, 
                                        "tool_result"
                                    )
                                    status_text.set_text(f"Processing results from {func_name}...")
                except Exception as e:
                    logger.error(f"Agent error: {e}")
                    create_log_entry(backend_scroll_area, "ERROR", str(e), "info")
                    with chat_container:
                        ui.chat_message("Connection failed.", name="System")
                finally:
                    loading_indicator.classes(add='hidden')
                    run_btn.enable()

            run_btn.on_click(run_agent)