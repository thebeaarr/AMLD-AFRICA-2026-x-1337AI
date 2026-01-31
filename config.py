# config.py - API keys and IDs
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Validate that keys are set
if not NOTION_API_KEY:
    raise ValueError("❌ NOTION_API_KEY not found. Create a .env file with your API key.")
if not NOTION_DATABASE_ID:
    raise ValueError("❌ NOTION_DATABASE_ID not found. Create a .env file with your database ID.")