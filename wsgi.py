"""
SAMUDRA AI — WSGI Entry Point
वेब सर्वर इंटरफेस

Render.com deployment entry point for Gunicorn
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.api import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
