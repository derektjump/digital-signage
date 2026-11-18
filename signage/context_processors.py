"""
Context processors for Digital Signage application.

These values are available in all templates.
Configure via environment variables or change defaults here.
"""

import os

from . import new_look


def app_context(request):
    """Add app-specific context to all templates."""
    ctx = {
        'app_name': os.environ.get('APP_NAME', 'Digital Signage'),
        'app_short_name': os.environ.get('APP_SHORT_NAME', 'Signage'),
    }
    ctx.update(new_look.context(request))
    return ctx
