"""
Token generation demonstration page.
Allows users to explore how Temperature, Top-K, and Top-P affect the 
next predicted token.
"""

__version__ = "1.0.0"
__author__ = "Carlos Moreno Morera"

from nicegui import ui
from loguru import logger
from app.ai.dependencies import get_generator_service

from app.ui.theme import apply_theme

def create_generator_page():
    """Builds the next-token generation UI route."""    
    @ui.page('/generator')
    def generator_ui():
        apply_theme()
        generation_service = get_generator_service()
        
        with ui.column().classes('w-full max-w-4xl mx-auto p-6'):
            ui.label(
                "Generative AI Engine: Next Token Prediction"
            ).classes('text-3xl font-extrabold text-white mb-6')
            
            with ui.row().classes('w-full gap-8'):
                with ui.column().classes('w-1/2'):
                    ui.label(
                        "Model Parameters"
                    ).classes('text-xl font-bold text-secondary mb-2')
                    
                    ui.label("Temperature (Randomness)")
                    temp_slider = ui.slider(
                        min=0.0, max=2.0, step=0.1, value=0.0
                    ).classes('w-full')
                    ui.label().bind_text_from(
                        temp_slider, 'value', backward=lambda v: f"{v:.1f}"
                    )
                    
                    ui.label("Top-K (Vocabulary pool limit)")
                    top_k_slider = ui.slider(
                        min=1, max=40, step=1, value=40
                    ).classes('w-full')
                    ui.label().bind_text_from(
                        top_k_slider, 'value', backward=lambda v: str(int(v))
                    )
                    
                    ui.label("Top-P (Nucleus sampling)")
                    top_p_slider = ui.slider(
                        min=0.0, max=1.0, step=0.05, value=0.95
                    ).classes('w-full')
                    ui.label().bind_text_from(
                        top_p_slider, 'value', backward=lambda v: f"{v:.2f}"
                    )
                    
                    ui.separator().classes('my-4')
                    
                    prompt_input = ui.textarea(
                        label="Incomplete sentence...", 
                        value="La capital de Francia es"
                    ).classes('w-full')
                    gen_btn = ui.button(
                        "Predict Next Token", color="primary", icon="smart_toy"
                    ).classes('w-full mt-2')

                with ui.column().classes('w-5/12 ml-auto'):
                    ui.label(
                        "Probabilities (Logprobs)"
                    ).classes('text-xl font-bold text-secondary mb-2')
                    results_container = ui.column().classes('w-full')
                    
            async def on_generate(e):
                if not prompt_input.value or not prompt_input.value.strip():
                    ui.notify("Please enter a prompt.", type="warning")
                    return
                if generation_service is None:
                    ui.notify("Error loading generation model.", type="negative")
                    return
                    
                gen_btn.disable()
                results_container.clear()
                with results_container:
                    ui.spinner('dots', size='lg', color='primary')
                
                try:
                    result = await generation_service.predict_next_token(
                        prompt=prompt_input.value,
                        temperature=temp_slider.value,
                        top_k=(int(top_k_slider.value) if top_k_slider.value 
                               else None),
                        top_p=top_p_slider.value
                    )
                    
                    results_container.clear()
                    if result is None:
                        with results_container:
                            ui.label(
                                "Generation blocked by safety settings or API error."
                            ).classes('text-warning font-bold')
                        return
                    
                    with results_container:
                        ui.label(
                            f"Chosen Token: '{result.chosen_token}'"
                        ).classes('text-2xl font-bold text-positive mb-4')
                        
                        for alt in result.alternatives:
                            with ui.row().classes('w-full items-center mb-2'):
                                ui.label(
                                    f"'{alt.token}'"
                                ).classes('w-1/3 font-mono text-gray-300 text-lg')
                                ui.linear_progress(
                                    value=alt.probability / 100.0, color='info'
                                ).classes('w-1/2 mx-2 h-4 rounded')
                                ui.label(
                                    f"{alt.probability:.2f}%"
                                ).classes('w-1/6 text-right text-sm text-gray-400')
                                
                except Exception as ex:
                    results_container.clear()
                    logger.error(f"Generation error: {ex}")
                    with results_container:
                        ui.label(
                            f"Error connecting to Vertex AI: {ex}"
                        ).classes('text-negative')
                finally:
                    gen_btn.enable()
                        
            gen_btn.on_click(on_generate)