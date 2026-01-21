import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
EDMUNDS_API_KEY = os.getenv('EDMUNDS_API_KEY', '')
NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api"

# App Configuration
APP_TITLE = "AI Car Lease Assistant"
APP_ICON = "🚗"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# File upload settings
ALLOWED_FILE_TYPES = ['.pdf', '.png', '.jpg', '.jpeg']
MAX_FILE_SIZE_MB = 10

# OCR Configuration
TESSERACT_PATH = os.getenv('TESSERACT_PATH', '')
USE_GPU = os.getenv('USE_GPU', 'False').lower() == 'true'

# Database Configuration (if using)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///contracts.db')

# Feature flags
ENABLE_OPENAI = bool(OPENAI_API_KEY)
ENABLE_VEHICLE_API = bool(EDMUNDS_API_KEY)
ENABLE_DATABASE = True

# Cache settings
CACHE_TTL = 3600  # 1 hour

# Display settings
DEFAULT_THEME = "light"
LANGUAGE = "en"