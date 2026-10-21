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
        
        with ui.column().classes('w-full max-w-6xl mx-auto p-6'):
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
                    value="Alejandro Jiménez"
                ).classes('w-full max-w-md text-lg')
                
                run_btn = ui.button(
                    "Analyze & Break Ice", 
                    color="primary", 
                    icon="psychology"
                ).classes('h-14 px-6')

            panels_container = ui.row().classes('w-full gap-8 items-stretch')
            
            with panels_container:
                
                # LEFT PANEL
                left_panel = ui.column().classes('flex-grow transition-all duration-500 bg-gray-800 p-6 rounded-lg shadow-lg')
                
                with left_panel:
                    ui.label("Front-End (The Magic)").classes('text-xl font-bold text-accent mb-4')
                    chat_container = ui.column().classes('w-full gap-4')
                    spinner = ui.spinner('dots', size='lg', color='primary').classes('hidden mt-4')
                
                # RIGHT PANEL
                right_panel = ui.column().classes('w-[600px] hidden transition-all duration-500 bg-black p-6 rounded-lg shadow-lg border border-gray-700')
                
                with right_panel:
                    ui.label("Back-End (The Reality)").classes('text-xl font-bold text-secondary mb-4')
                    
                    backend_scroll_area = ui.scroll_area().classes('w-full h-[600px] border border-gray-800 rounded p-2')

            def toggle_backend():
                is_hidden = 'hidden' in right_panel.classes
                if is_hidden:
                    right_panel.classes(remove='hidden')
                    reveal_btn.set_text("Hide Reality")
                    reveal_btn.props('icon=visibility_off')
                else:
                    right_panel.classes(add='hidden')
                    reveal_btn.set_text("Reveal the Reality")
                    reveal_btn.props('icon=visibility')
                    
            reveal_btn.on_click(toggle_backend)
            
            async def run_agent():
                chat_container.clear()
                backend_scroll_area.clear()
                spinner.classes(remove='hidden')
                run_btn.disable()
                
                name = attendee_input.value
                if not name or not isinstance(name, str) or not name.strip():
                    ui.notify("Please enter a valid attendee name.", type="warning")
                    spinner.classes(add='hidden')
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
                        tool_calls = getattr(event, 'tool_calls', [])
                        # Interpret event for the magic UI
                        if tool_calls:
                            for tc in tool_calls:
                                func_name = getattr(tc.function, 'name', 'UnknownTool')
                                func_args = str(getattr(tc.function, 'args', {}))
                                create_log_entry(
                                    backend_scroll_area, 
                                    f"TOOL CALL REQUESTED: {func_name}", 
                                    func_args, 
                                    "tool_call"
                                )

                                with chat_container:
                                    ui.chat_message(
                                        f"<i>Using tool: {func_name}...</i>", 
                                        name="System", 
                                        text_html=True,
                                        avatar="https://cdn-icons-png.flaticon.com/512/2885/2885412.png"
                                    )

                        tool_response = getattr(event, 'tool_response', None) or getattr(event, 'function_response', None)
                        if tool_response:
                            create_log_entry(
                                backend_scroll_area, 
                                "TOOL EXECUTION RESULT", 
                                str(tool_response), 
                                "tool_result"
                            )
                        
                        elif event.is_final_response() and event.content:
                            parts = getattr(event.content, 'parts', None)
                            if parts and isinstance(parts, list) and len(parts) > 0:
                                final_text = getattr(parts[0], 'text', "")
                                if final_text:
                                    create_log_entry(
                                        backend_scroll_area, 
                                        "FINAL LLM TEXT GENERATION", 
                                        final_text, 
                                        "final_text"
                                    )
                                    
                                    with chat_container:
                                        ui.chat_message(
                                            final_text, 
                                            name="Pontia Agent", 
                                            avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                                        )
                        elif hasattr(event, 'text'):
                            create_log_entry(
                                backend_scroll_area, 
                                "LLM REASONING CHUNK", 
                                getattr(event, 'text'),
                                "info"
                            )
                except Exception as e:
                    logger.error(f"Agent error: {e}")
                    create_log_entry(backend_scroll_area, "ERROR", str(e), "info")
                    with chat_container:
                        ui.chat_message("Connection failed.", name="System")
                finally:
                    spinner.classes(add='hidden')
                    run_btn.enable()

            run_btn.on_click(run_agent)