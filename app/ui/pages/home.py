from nicegui import ui
from app.ui.theme import apply_theme

def create_home_page():
    """Builds a neutral landing page for the presentation."""
    @ui.page('/')
    def home_ui():
        apply_theme()
        
        with ui.column().classes('w-full h-[80vh] items-center justify-center gap-6 p-6'):
            ui.icon('hub', color='primary', size='100px').classes('mb-4')
            
            ui.label("¿La Inteligencia Artificial piensa?").classes(
                'text-5xl font-extrabold text-white text-center'
            )
            ui.label("PontIA Connect Demo Engine").classes(
                'text-2xl text-gray-400 text-center mb-8'
            )
            
            with ui.row().classes('gap-4'):
                ui.button('Agent Demo', icon='smart_toy', on_click=lambda: ui.navigate.to('/agent')).classes('px-6 py-3 text-lg').props('rounded outline')
                ui.button('Generation', icon='auto_awesome', on_click=lambda: ui.navigate.to('/generator')).classes('px-6 py-3 text-lg').props('rounded outline')