# backend/app/config.py

import os

# Base directory of backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Upload directory
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Max number of files allowed per upload
MAX_FILES = 3
