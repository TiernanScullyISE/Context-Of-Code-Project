import sys
import os

# Add your project directory to the sys.path
path = '/home/yourusername/myapp'
if path not in sys.path:
    sys.path.append(path)

from app import app as application  # noqa

# Initialize the database
from app import init_db
with application.app_context():
    init_db() 