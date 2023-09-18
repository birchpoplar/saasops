from src import classes, display, database, calc, visualization, export
from src.commands import app
from rich.console import Console
from rich.text import Text
from dotenv import load_dotenv
import os
from datetime import date, timedelta
import pandas as pd
import logging
import typer

load_dotenv()

logging.basicConfig(level=logging.ERROR)
 
if __name__ == "__main__":
    app()
