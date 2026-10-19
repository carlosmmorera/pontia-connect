"""
Embeddings demonstration page.
Handles tokenization, vector generation, and vector arithmetic.
"""

from nicegui import ui
from loguru import logger

from app.ai.embeddings.lowdimservice import LowDimEmbeddingService
from app.ui.theme import apply_theme
from app.ui.components import token_visualizer, vector_display

def create_embeddings_page():
    """Builds the main embeddings UI route."""
    
    # Initialize the service globally for this page
    logger.info("Initializing Low Dimensional Embedding Service...")
    embed_service = LowDimEmbeddingService()
    
    @ui.page('/')
    def embeddings_ui():
        apply_theme()

        with ui.column().classes('w-full max-w-4xl mx-auto p-6'):
            ui.label("Generative AI Engine: Tokens & Embeddings").classes(
                'text-3xl font-extrabold text-white mb-6'
            )
            
            # --- SECTION 1: Tokenization ---
            ui.label("1. Tokenization").classes(
                'text-xl font-bold text-secondary mt-4'
            )
            token_input = ui.input(
                label="Enter text to tokenize", 
                value="The PontIA Connect event was amazing, unforgettable and incredible."
            ).classes('w-full text-lg')
            token_container = ui.column().classes('w-full mt-2')
            
            def update_tokens(e=None):
                token_container.clear()
                with token_container:
                    token_visualizer(token_input.value or "")
                    
            token_input.on('change', update_tokens)
            update_tokens()
            
            ui.separator().classes('my-6')
            
            # --- SECTION 2: Vector Arithmetic (King - Man + Woman) ---
            ui.label("2. Vector Arithmetic & Semantics").classes(
                'text-xl font-bold text-secondary mt-4'
            )
            
            with ui.row().classes('w-full gap-4 items-center mt-2'):
                word1 = ui.input(value="king").classes('w-32')
                ui.label("-").classes('text-2xl font-bold')
                word2 = ui.input(value="man").classes('w-32')
                ui.label("+").classes('text-2xl font-bold')
                word3 = ui.input(value="woman").classes('w-32')
                calc_btn = ui.button("Calculate", color="primary", 
                                     icon="calculate")
                
            results_container = ui.column().classes('w-full mt-4')
            
            def calculate_vectors(e):
                w1 = word1.value or ""
                w2 = word2.value or ""
                w3 = word3.value or ""

                logger.debug(f"Calculating arithmetic for: {w1} - {w2} + {w3}")
                results_container.clear()

                if not (w1 and w2 and w3):
                    ui.notify("Please fill all fields to calculate.", 
                              type="warning")
                    return
                
                v1 = embed_service.get_embedding(w1)
                v2 = embed_service.get_embedding(w2)
                v3 = embed_service.get_embedding(w3)
                
                # Perform the operation
                result_vector = v1 - v2 + v3
                
                # Find closest words
                closest = embed_service.get_closest_words(result_vector,
                                                          top_n=5)
                
                with results_container:
                    ui.label("Closest semantic matches:").classes(
                        'font-bold text-info'
                    )
                    with ui.row().classes('gap-4 mb-4'):
                        for word, score in closest:
                            ui.badge(f"{word} ({score:.2f})", color="accent"
                                     ).classes('text-md p-2')
                    
                    # Resulting vector vs the first word to highlight differences
                    vector_display(result_vector, title="Resulting Vector", 
                                   compare_with=v1)
                    
            calc_btn.on_click(calculate_vectors)