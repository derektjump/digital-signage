"""Glow in the Grid family look, behind a per-person switch.

A copy of the Grid's "Try the new look" switch (customer-lifecycle
`lifecycle/new_look.py`, and Flux's `main/new_look.py`). Nobody's screens
change unless they turn it on, and only superusers see the switch while the
look is being built (Glow has no roles of its own).

The choice is kept in a long-lived cookie on that browser, so no migration is
needed. It is only honoured for people who may try the look: a cookie left on
a shared machine does nothing for anyone else.

`signage/base.html` adds `class="look-family"` to <html> and loads
`signage/css/family.css` and `signage/css/kit.css` when it is on; every rule
there is scoped under that class, so with it off the page is exactly as before.
"""

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

COOKIE = 'glow_new_look'
COOKIE_AGE = 60 * 60 * 24 * 365

# The Grid's apps, as its launcher names them (lifecycle/new_look.APPS).
GRID_URL = 'https://the-grid.digital'
FLUX_URL = 'https://shopify-manager-grc7a7fpbee0eqdx.canadaeast-01.azurewebsites.net/home/'
APPS = (
    ('cycle', 'Cycle', 'Customer Intelligence', GRID_URL + '/dashboard/'),
    ('relay', 'Relay', 'Business Hub', GRID_URL + '/business/work/'),
    ('pulse', 'Pulse', 'Front Desk', GRID_URL + '/pulse/'),
    ('track', 'Track', 'Sales Performance', GRID_URL + '/track/'),
    ('flux', 'Flux', 'Storefront', FLUX_URL),
    ('glow', 'Glow', 'Digital Signage', '/'),
)


def can_try(user):
    """Who sees the switch: superusers only while the look is being built."""
    return bool(user is not None and getattr(user, 'is_authenticated', False)
                and user.is_superuser)


def is_on(request):
    """True when this person has the new look turned on."""
    cached = getattr(request, '_new_look', None)
    if cached is not None:
        return cached
    on = can_try(getattr(request, 'user', None)) and request.COOKIES.get(COOKIE) == '1'
    request._new_look = on
    return on


def context(request):
    """Template values for the switch and the new-look sidebar."""
    on = is_on(request)
    return {
        'new_look': on,
        'can_try_new_look': can_try(getattr(request, 'user', None)),
        'grid_url': GRID_URL,
        'grid_switch_apps': [
            {'key': k, 'name': n, 'full': f, 'url': u} for k, n, f, u in APPS
        ] if on else [],
    }


@require_POST
def toggle(request):
    """Turn the new look on or off for the signed-in person, then go back."""
    if not can_try(request.user):
        return HttpResponseForbidden('The new look is not open to you yet.')
    back = request.POST.get('next') or '/'
    if not url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()},
                                           require_https=request.is_secure()):
        back = '/'
    response = redirect(back)
    if is_on(request):
        response.delete_cookie(COOKIE)
    else:
        response.set_cookie(COOKIE, '1', max_age=COOKIE_AGE, httponly=True,
                            secure=request.is_secure(), samesite='Lax')
    return response
