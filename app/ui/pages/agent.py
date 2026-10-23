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
        intermediate_elements = []
        
        with ui.column().classes('w-full max-w-[90rem] mx-auto p-6'):
            with ui.row().classes('w-full justify-between items-center mb-6'):
                ui.label(
                    "Agents: The Illusion of Reasoning"
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
                left_panel = ui.column().classes(
                    'flex-grow w-full transition-all duration-500 bg-gray-800 p-6 rounded-lg shadow-lg min-w-0'
                )
                
                with left_panel:
                    ui.label("Front-End (The Magic)").classes('text-xl font-bold text-accent mb-4')
                    chat_container = ui.column().classes('w-full gap-4')
                    
                    with ui.row().classes('items-center gap-3 mt-4 hidden') as loading_indicator:
                        ui.spinner('dots', size='md', color='primary')
                        status_text = ui.label("Initializing agent...").classes('text-sm text-gray-400 italic')
                
                # RIGHT PANEL
                right_panel = ui.column().classes(
                    'w-0 opacity-0 px-0 py-0 border-0 transition-all duration-500 bg-black rounded-lg shadow-lg border-gray-700 overflow-hidden min-w-0'
                )
                
                with right_panel:
                    ui.label("Back-End (The Reality)").classes('text-xl font-bold text-secondary mb-4')
                    backend_scroll_area = ui.scroll_area().classes('w-full h-[600px] border border-gray-800 rounded p-2')

            def toggle_backend():
                ui_state["revealed"] = not ui_state["revealed"]
                
                if ui_state["revealed"]:
                    right_panel.classes(remove='w-0 opacity-0 px-0 py-0 border-0').classes(add='w-1/2 p-6 border')
                    left_panel.classes(remove='w-full').classes(add='w-1/2')
                    reveal_btn.set_text("Hide Reality")
                    reveal_btn.props('icon=visibility_off')
                else:
                    right_panel.classes(remove='w-1/2 p-6 border').classes(add='w-0 opacity-0 px-0 py-0 border-0')
                    left_panel.classes(remove='w-1/2').classes(add='w-full')
                    reveal_btn.set_text("Reveal the Reality")
                    reveal_btn.props('icon=visibility')

                for el in intermediate_elements:
                    el.set_visibility(ui_state["revealed"])
                    
            reveal_btn.on_click(toggle_backend)
            
            async def run_agent():
                chat_container.clear()
                backend_scroll_area.clear()
                intermediate_elements.clear()

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
                
                last_llm_input = f"[System Prompt Loaded]\n\nUser Request: {prompt_text}"
                                
                with chat_container:
                    ui.chat_message(
                        f"¿Me puedes ayudar a entablar conversación con {name}?", 
                        name="User", 
                        sent=True
                    )
                
                try:
                    async for event in agent.generate_networking_strategy(name):
                        
                        current_input_to_print = last_llm_input
                        last_llm_input = None 
                        
                        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                            for part in getattr(event.content, "parts", []):
                                
                                # 1. Check for Text (Reasoning or Final Generation)
                                if hasattr(part, 'text') and part.text:
                                    text_content = part.text.strip()

                                    is_final = event.is_final_response()

                                    if is_final and "ROMPEHIELOS:" in text_content:
                                        parts_split = text_content.split("ROMPEHIELOS:")
                                        reasoning_text = parts_split[0].strip()
                                        final_icebreaker = f"ROMPEHIELOS:\n{parts_split[1].strip()}"

                                        if reasoning_text:
                                            create_log_entry(
                                                backend_scroll_area, 
                                                "LLM REASONING", 
                                                reasoning_text, "info",
                                                llm_input=current_input_to_print
                                            )
                                            current_input_to_print = None
                                            
                                            with chat_container:
                                                msg_reasoning = ui.chat_message(
                                                    reasoning_text, name="Pontia Agent", 
                                                    avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                                                )
                                                msg_reasoning.set_visibility(ui_state["revealed"])
                                                intermediate_elements.append(msg_reasoning)

                                        if final_icebreaker:
                                            create_log_entry(
                                                backend_scroll_area, "FINAL LLM TEXT GENERATION", final_icebreaker, "final_text",
                                                llm_input=current_input_to_print
                                            )
                                            current_input_to_print = None
                                            
                                            with chat_container:
                                                ui.chat_message(
                                                    final_icebreaker, name="Pontia Agent", 
                                                    avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                                                )

                                    else:
                                        card_type = "final_text" if is_final else "info"
                                        title = "FINAL LLM TEXT GENERATION" if is_final else "LLM REASONING"
                                        
                                        create_log_entry(
                                            backend_scroll_area, 
                                            title, 
                                            text_content, 
                                            card_type,
                                            llm_input=current_input_to_print
                                        )
                                        current_input_to_print = None

                                        if is_final:
                                            with chat_container:
                                                ui.chat_message(
                                                    text_content, 
                                                    name="Pontia Agent", 
                                                    avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                                                )
                                        else:
                                            status_text.set_text("Agent is reasoning about the strategy...")
                                            with chat_container:
                                                msg = ui.chat_message(
                                                    text_content, name="Pontia Agent", 
                                                    avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                                                )
                                                msg.set_visibility(ui_state["revealed"])
                                                intermediate_elements.append(msg)

                                # 2. Check for Tool Call Requests
                                if hasattr(part, 'function_call') and part.function_call:
                                    func_name = getattr(part.function_call, 'name', 'UnknownTool')
                                    func_args = str(getattr(part.function_call, 'args', {}))

                                    create_log_entry(
                                        backend_scroll_area, 
                                        f"TOOL CALL REQUESTED: {func_name}", 
                                        func_args, 
                                        "tool_call",
                                        llm_input=current_input_to_print
                                    )
                                    current_input_to_print = None 

                                    status_text.set_text(f"Executing internal tool: {func_name}...")
                                    
                                    with chat_container:
                                        msg = ui.chat_message(
                                            f"<i>Using tool: {func_name}...</i>", name="System", 
                                            text_html=True, avatar="https://cdn-icons-png.flaticon.com/512/2885/2885412.png"
                                        )
                                        msg.set_visibility(ui_state["revealed"])
                                        intermediate_elements.append(msg)

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
                                    
                                    last_llm_input = f"Tool Execution Result ({func_name}):\n{func_data}"
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