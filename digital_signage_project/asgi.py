"""
ASGI config for Digital Signage project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_signage_project.settings')

application = get_asgi_application()
