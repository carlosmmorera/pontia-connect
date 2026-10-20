"""
Main application entry point.
Configures logging, initializes the NiceGUI server, and mounts the UI pages.
"""

import sys
from loguru import logger
from nicegui import app, ui

from app.ui.pages import create_embeddings_page, create_generator_page

def filtrar_gensim(record):
    if record["name"] == "gensim.downloader":
        return record["level"].no >= logger.level("WARNING").no
    return True

def setup_logging():
    """Configures Loguru to output structured logs to stdout and a 
    rolling file."""
    logger.remove()
    
    logger.add(
        sys.stdout,
        format=("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                + "<level>{level: <8}</level> | <cyan>{name}</cyan>:"
                + "<cyan>{function}</cyan> - <level>{message}</level>"),
        level="INFO",
        colorize=True
    )
    
    logger.add(
        "logs/microservice.log",
        rotation="10 MB",
        retention="14 days",
        level="DEBUG",
        format=("{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:"
                + "{line} | {message}")
    )

    logger.add(sys.stderr, level="DEBUG", filter=filtrar_gensim)

# NiceGUI lifecycle events
@app.on_startup
def startup_event():
    setup_logging()
    logger.info("Starting Pontia Connect Demo App...")

@app.on_shutdown
def shutdown_event():
    logger.info("Shutting down Pontia Connect Demo App...")

# Initialize the UI
app.add_static_files('/static', 'app/static')
create_embeddings_page()
create_generator_page()

# Run the application
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Generative AI Demo", port=8080, dark=True)