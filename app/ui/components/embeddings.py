"""
Reusable UI components for the Generative AI presentation.
"""

import numpy as np
from typing import Optional, Callable, Union, Awaitable
from nicegui import ui
import tiktoken

def token_visualizer(
        text: str,
        on_token_click: Optional[Callable[[str], Union[None, Awaitable[None]]]] = None
) -> None:
    """
    Renders a text string into visually distinct tokens using the 
    cl100k_base encoder. 
    
    Args:
        text (str): The input text to tokenize.
        on_token_click (Callable, optional): Callback executed when a token is clicked.
            Passes the decoded token string as an argument.
    """
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    
    with ui.row().classes('w-full items-center gap-1 flex-wrap bg-dark p-4 '
                          + 'rounded shadow'):
        for token_id in tokens:
            token_str: str = encoder.decode([token_id])

            box_classes = 'token-box items-center p-2 rounded transition-colors '
            if on_token_click:
                box_classes += 'cursor-pointer hover:bg-primary hover:text-white'
            else:
                box_classes += 'bg-gray-800'

            with ui.column().classes(box_classes) as box:
                ui.label(repr(token_str)).classes(
                    'text-accent font-bold text-lg pointer-events-none'
                )
                ui.label(str(token_id)).classes(
                    'text-xs text-gray-400 pointer-events-none'
                )
                
                if on_token_click:
                    box.on('click', lambda e, t=token_str: on_token_click(t))

def vector_display(
    vector: np.ndarray, 
    title: str, 
    compare_with: Optional[np.ndarray] = None,
    compare_label: Optional[str] = None,
    display_limit: int = 50,
    diff_threshold: float = 0.1
) -> None:
    """
    Displays an embedding vector. If compare_with is provided,
    highlights significant differences and calculates similarity stats.

    Args:
        vector (np.ndarray): Target vector to display.
        title (str): Title for the vector card.
        compare_with (Optional[np.ndarray]): Vector to compare against.
        compare_label (Optional[str]): Human-readable label of the compared vector.
        display_limit (int): Number of dimensions to render visually (default 50).
        diff_threshold (float): Threshold above which a difference is highlighted.
    """
    dim_count = len(vector)
    is_truncated = dim_count > display_limit
    display_vector = vector[:display_limit]

    with ui.card().classes('w-full mt-4 p-4 bg-dark border border-gray-800 rounded-lg shadow'):
        with ui.row().classes('w-full items-center justify-between flex-wrap gap-2'):
            ui.label(f"{title} ({dim_count} dimensions)").classes(
                'text-lg font-bold text-primary'
            )

            if compare_with is not None:
                eval_len = min(len(vector), len(compare_with))
                diff_mask = np.abs(vector[:eval_len] - compare_with[:eval_len]) > diff_threshold
                diff_count = int(np.sum(diff_mask))
                similar_count = eval_len - diff_count
                similarity_pct = (similar_count / eval_len) * 100 if eval_len > 0 else 0

                with ui.row().classes('items-center gap-2 flex-wrap'):
                    if compare_label:
                        ui.badge(f"Compared with: {compare_label}", color="info").classes('text-xs p-1.5')
                    
                    ui.badge(
                        f"Similar dimensions: {similar_count}/{eval_len} ({similarity_pct:.1f}%)", 
                        color="positive" if similarity_pct >= 70 else "warning"
                    ).classes('text-xs p-1.5')

        # Vector Grid Cells Display
        with ui.row().classes('w-full flex-wrap gap-1 mt-3'):
            for i, val in enumerate(display_vector):
                cell_class = 'vector-cell text-gray-300 text-xs font-mono p-1 bg-gray-800 rounded'
                
                # Highlight differences if comparing
                if compare_with is not None and i < len(compare_with):
                    diff = abs(val - compare_with[i])
                    if diff > diff_threshold:
                        cell_class += ' highlight-diff text-white bg-red-900 border border-red-500 font-bold'

                ui.label(f"{val:.3f}").classes(cell_class)
            
            if is_truncated:
                ui.label(f"... (+{dim_count - display_limit} more)").classes(
                    'vector-cell text-gray-500 font-bold text-xs p-1'
                )