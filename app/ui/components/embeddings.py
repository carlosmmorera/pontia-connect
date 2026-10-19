"""
Reusable UI components for the Generative AI presentation.
"""

import numpy as np
from typing import Optional
from nicegui import ui
import tiktoken

def token_visualizer(text: str) -> None:
    """
    Renders a text string into visually distinct tokens using the 
    cl100k_base encoder (GPT-4 standard).
    """
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    
    with ui.row().classes('w-full items-center gap-1 flex-wrap bg-dark p-4 '
                          + 'rounded shadow'):
        for token_id in tokens:
            token_str = encoder.decode([token_id])
            # Display both the text string and the integer ID
            with ui.column().classes('token-box items-center'):
                ui.label(repr(token_str)).classes('text-accent font-bold '
                                                  + 'text-lg')
                ui.label(str(token_id)).classes('text-xs text-gray-400')

def vector_display(
        vector: np.ndarray, 
        title: str, 
        compare_with: Optional[np.ndarray] = None
) -> None:
    """
    Displays an embedding vector. If compare_with is provided,
    highlights significant differences.
    For high-dimensional vectors, truncates the display visually.
    """
    with ui.card().classes('w-full mt-4'):
        ui.label(f"{title} ({len(vector)} dimensions)").classes('text-lg '
                                                                + 'font-bold '
                                                                + 'text-primary')
        
        # Determine how many dimensions to show (truncate high dim)
        display_limit = 50
        is_truncated = len(vector) > display_limit
        display_vector = vector[:display_limit]
        
        with ui.row().classes('w-full flex-wrap gap-1 mt-2'):
            for i, val in enumerate(display_vector):
                cell_class = 'vector-cell text-gray-300'
                
                # Highlight differences if comparing
                if compare_with is not None:
                    diff = abs(val - compare_with[i])
                    if diff > 0.1: # Threshold for highlighting
                        cell_class += ' highlight-diff text-white font-bold'
                
                ui.label(f"{val:.3f}").classes(cell_class)
                
            if is_truncated:
                ui.label("...").classes('vector-cell text-gray-500 font-bold')