"""
Context processors for Digital Signage application.

These values are available in all templates.
Configure via environment variables or change defaults here.
"""

import os


def app_context(request):
    """Add app-specific context to all templates."""
    return {
        'app_name': os.environ.get('APP_NAME', 'Digital Signage'),
        'app_short_name': os.environ.get('APP_SHORT_NAME', 'Signage'),
    }
