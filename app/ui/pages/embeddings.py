"""
Embeddings demonstration page.
Handles tokenization, vector generation, and vector arithmetic.
"""

from nicegui import ui
from loguru import logger
import numpy as np

from app.ai.dependencies import get_low_dim_service, get_high_dim_service
from app.ui.theme import apply_theme
from app.ui.components import token_visualizer, vector_display

def create_tokenization_page():
    """Builds the Tokenization and Embedding generation UI route."""
    @ui.page('/')
    def tokenization_ui():
        apply_theme()
        embed_service_low = get_low_dim_service()
        embed_service_high = get_high_dim_service()

        with ui.column().classes('w-full max-w-4xl mx-auto p-6'):
            ui.label("1. Tokens & Embeddings").classes(
                'text-3xl font-extrabold text-white mb-6'
            )
            
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                ui.label("Select Embedding Model:").classes('font-bold')
                model_options = {'low': 'GloVe (50-dim)'}
                
                if embed_service_high:
                    model_options['high'] = 'Vertex AI (768-dim)'
                
                model_selector = ui.radio(
                    options=model_options, 
                    value='low'
                ).props('inline')
                
                if not embed_service_high:
                    ui.label("(Vertex AI disabled - missing GCP auth)").classes(
                        'text-xs text-negative italic'
                    )

            token_input = ui.input(
                label="Enter text to tokenize", 
                value="The PontIA Connect event was amazing, unforgettable and incredible."
            ).classes('w-full text-lg')
            
            token_container = ui.column().classes('w-full mt-2')
            token_vector_container = ui.column().classes('w-full mt-4')

            async def handle_token_click(token: str):
                token_vector_container.clear()
                with token_vector_container:
                    ui.spinner(size='lg', color='primary')
                    ui.label(f"Fetching embedding for {repr(token)}...").classes('text-sm text-gray-400')

                try:
                    if model_selector.value == 'low':
                        vec = embed_service_low.get_embedding(token)
                    elif embed_service_high is not None:
                        vec = await embed_service_high.get_embedding_async(token)
                    
                    token_vector_container.clear()
                    with token_vector_container:
                        vector_display(vec, title=f"Vector for {repr(token)}")
                
                except Exception as e:
                    token_vector_container.clear()
                    ui.notify(f"Error fetching embedding: {str(e)}", type="negative")
                    logger.error(f"Embedding error: {e}")
            
            def update_tokens(e=None):
                token_container.clear()
                token_vector_container.clear()
                with token_container:
                    token_visualizer(token_input.value or "", on_token_click=handle_token_click)
                    
            token_input.on('change', update_tokens)
            update_tokens()

def create_arithmetic_page():
    """Builds the Vector Arithmetic UI route."""
    
    @ui.page('/arithmetic')
    def arithmetic_ui():
        apply_theme()
        
        # Arithmetic page only needs the low dimensional service
        embed_service_low = get_low_dim_service()

        with ui.column().classes('w-full max-w-4xl mx-auto p-6'):
            ui.label("2. Vector Arithmetic & Semantics").classes(
                'text-3xl font-extrabold text-white mb-6'
            )
            ui.label("Reverse mapping is performed via Gensim local spatial indexing.").classes(
                'text-sm text-gray-400 mb-4'
            )
            
            with ui.row().classes('w-full gap-4 items-center mt-2'):
                word1 = ui.input(value="king").classes('w-32')
                ui.label("-").classes('text-2xl font-bold')
                word2 = ui.input(value="man").classes('w-32')
                ui.label("+").classes('text-2xl font-bold')
                word3 = ui.input(value="woman").classes('w-32')
                calc_btn = ui.button("Calculate", color="primary", icon="calculate")
                
            results_container = ui.column().classes('w-full mt-4')
            closest_comparison_container = ui.column().classes('w-full mt-2')

            def handle_closest_word_click(word: str, reference_vector: np.ndarray):
                closest_comparison_container.clear()
                word_vec = embed_service_low.get_embedding(word)
                with closest_comparison_container:
                    vector_display(
                        vector=word_vec, 
                        title=f"Vector for {repr(word)}", 
                        compare_with=reference_vector
                    )
            
            def calculate_vectors(e):
                w1 = word1.value or ""
                w2 = word2.value or ""
                w3 = word3.value or ""

                results_container.clear()
                closest_comparison_container.clear()

                if not (w1 and w2 and w3):
                    ui.notify("Please fill all fields to calculate.", type="warning")
                    return
                
                v1 = embed_service_low.get_embedding(w1)
                v2 = embed_service_low.get_embedding(w2)
                v3 = embed_service_low.get_embedding(w3)
                
                result_vector = v1 - v2 + v3
                closest = embed_service_low.get_closest_words(result_vector, top_n=5)
                
                with results_container:
                    ui.label("Closest semantic matches:").classes('font-bold text-info')
                    with ui.row().classes('gap-4 mb-4'):
                        for word, score in closest:
                            ui.button(
                                f"{word} ({score:.2f})", 
                                color="accent",
                                on_click=lambda e, w=word: handle_closest_word_click(w, result_vector)
                            ).classes('rounded-full px-4 text-sm')
                    
                    vector_display(result_vector, title="Resulting Vector", compare_with=v1)
                    
            calc_btn.on_click(calculate_vectors)