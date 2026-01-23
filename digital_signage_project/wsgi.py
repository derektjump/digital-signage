"""
WSGI config for Digital Signage project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_signage_project.settings')

application = get_wsgi_application()
