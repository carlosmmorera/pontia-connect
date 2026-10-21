"""
Networking Agent UI Page.
Demonstrates the agentic loop, function calling, and reasoning process.
"""

from nicegui import ui
from loguru import logger
from app.ai.agent import NetworkingAgent
from app.ui.theme import apply_theme

def create_agent_page():
    agent = NetworkingAgent()

    @ui.page('/agent')
    def agent_ui():
        apply_theme()
        
        with ui.column().classes('w-full max-w-6xl mx-auto p-6'):
            ui.label(
                "3. Agents: The Illusion of Reasoning"
            ).classes('text-3xl font-extrabold text-white mb-6')
            
            attendee_input = ui.input(
                label="Attendee Name", 
                value="Carlos Moreno"
            ).classes('w-full max-w-md text-lg')
            run_btn = ui.button(
                "Analyze & Break Ice", 
                color="primary", 
                icon="psychology"
            )
            
            with ui.row().classes('w-full mt-8 gap-8'):
                
                # LEFT PANEL
                with ui.column().classes('w-5/12 bg-gray-800 p-6 rounded-lg shadow-lg'):
                    ui.label(
                        "Front-End (The Magic)"
                    ).classes('text-xl font-bold text-accent mb-4')
                    chat_container = ui.column().classes('w-full gap-2')
                    spinner = ui.spinner(
                        'dots', 
                        size='lg', 
                        color='primary'
                    ).classes('hidden mt-4')
                
                # RIGHT PANEL
                with ui.column().classes('w-6/12 bg-black p-6 rounded-lg shadow-lg border border-gray-700'):
                    ui.label(
                        "Back-End (The Reality - LLM Text Generation)"
                    ).classes('text-xl font-bold text-secondary mb-4')
                    log_container = ui.log(
                        max_lines=50
                    ).classes('w-full h-96 font-mono text-xs text-green-400 bg-transparent')

            async def run_agent():
                chat_container.clear()
                log_container.clear()
                spinner.classes(remove='hidden')
                run_btn.disable()
                
                name = attendee_input.value
                if not name or not isinstance(name, str) or not name.strip():
                    ui.notify("Please enter a valid attendee name.", type="warning")
                    spinner.classes(add='hidden')
                    run_btn.enable()
                    return

                name = name.strip()
                log_container.push(f"> Initiating Agent Runner for target: {name}...\n")
                
                with chat_container:
                    ui.chat_message(
                        f"Can you help me network with {name}?", 
                        name="User", 
                        sent=True
                    )
                
                try:
                    # Iterate through the asynchronous generator
                    async for event in agent.generate_networking_strategy(name):
                        
                        # Show raw ADK event in the reality log
                        log_container.push(f"Event Received: {type(event).__name__}")

                        tool_calls = getattr(event, 'tool_calls', [])
                        # Interpret event for the magic UI
                        if tool_calls:
                            for tc in tool_calls:
                                log_container.push(f"  [TOOL CALL] -> {tc.function.name}({tc.function.args})")
                                with chat_container:
                                    ui.chat_message(
                                        f"Calling system function: {tc.function.name}...", 
                                        name="System", 
                                        text_html=True,
                                        avatar="https://cdn-icons-png.flaticon.com/512/2885/2885412.png"
                                    )
                        
                        elif event.is_final_response() and event.content:
                            parts = getattr(event.content, 'parts', None)
                            if parts and isinstance(parts, list) and len(parts) > 0:
                                final_text = getattr(parts[0], 'text', "")
                                if final_text:
                                    log_container.push(f"\n[FINAL LLM TEXT GENERATION]:\n{final_text}\n")
                                    
                                    with chat_container:
                                        ui.chat_message(final_text, name="Pontia Agent", avatar="https://cdn-icons-png.flaticon.com/512/4712/4712035.png")

                except Exception as e:
                    logger.error(f"Agent error: {e}")
                    log_container.push(f"[ERROR]: {e}")
                    with chat_container:
                        ui.chat_message("Connection failed.", name="System")
                finally:
                    spinner.classes(add='hidden')
                    run_btn.enable()

            run_btn.on_click(run_agent)