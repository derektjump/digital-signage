"""
Azure AD Authentication Views

Handles Microsoft Entra ID (Azure AD) authentication flow:
1. Login - Redirect to Azure AD
2. Callback - Exchange code for tokens, create/update user
3. Logout - Clear session and redirect to Azure AD logout
"""

import uuid
import msal
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse


def get_msal_app():
    """Create MSAL confidential client application."""
    return msal.ConfidentialClientApplication(
        settings.MS_ENTRA_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MS_ENTRA_TENANT_ID}",
        client_credential=settings.MS_ENTRA_CLIENT_SECRET,
    )


def login_view(request):
    """Initiate Azure AD login flow."""
    # Generate state for CSRF protection
    state = str(uuid.uuid4())
    request.session['auth_state'] = state

    # Build authorization URL
    msal_app = get_msal_app()
    redirect_uri = request.build_absolute_uri(reverse('signage:auth_callback'))

    auth_url = msal_app.get_authorization_request_url(
        scopes=settings.MS_ENTRA_SCOPES,
        state=state,
        redirect_uri=redirect_uri,
    )

    return redirect(auth_url)


def callback_view(request):
    """Handle Azure AD callback and create/update user."""
    # Validate state
    if request.GET.get('state') != request.session.get('auth_state'):
        return redirect('signage:auth_login')

    # Check for errors
    if 'error' in request.GET:
        error = request.GET.get('error_description', request.GET.get('error'))
        # Handle error (log, show message, etc.)
        return redirect('signage:auth_login')

    # Exchange code for tokens
    code = request.GET.get('code')
    if not code:
        return redirect('signage:auth_login')

    msal_app = get_msal_app()
    redirect_uri = request.build_absolute_uri(reverse('signage:auth_callback'))

    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=settings.MS_ENTRA_SCOPES,
        redirect_uri=redirect_uri,
    )

    if 'error' in result:
        return redirect('signage:auth_login')

    # Extract user info from ID token claims
    id_token_claims = result.get('id_token_claims', {})
    email = id_token_claims.get('preferred_username') or id_token_claims.get('email', '')

    if not email:
        return redirect('signage:auth_login')

    # Create or update Django user
    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email': email}
    )

    # Always sync user attributes from Azure AD claims on every login
    user.email = email

    # Try to get name from various claim keys
    given_name = id_token_claims.get('given_name', '')
    family_name = id_token_claims.get('family_name', '')

    # Fallback: if no given_name/family_name, try to parse from 'name' claim
    if not given_name and not family_name:
        full_name = id_token_claims.get('name', '')
        if full_name:
            name_parts = full_name.split(' ', 1)
            given_name = name_parts[0] if name_parts else ''
            family_name = name_parts[1] if len(name_parts) > 1 else ''

    user.first_name = given_name
    user.last_name = family_name
    user.save()

    # Store tokens in session
    request.session['access_token'] = result.get('access_token')
    request.session['refresh_token'] = result.get('refresh_token')
    request.session['id_token'] = result.get('id_token')
    request.session['id_token_claims'] = id_token_claims

    # Log user in
    login(request, user)

    # Clean up state
    if 'auth_state' in request.session:
        del request.session['auth_state']

    return redirect(settings.LOGIN_REDIRECT_URL)


def logout_view(request):
    """Log out user and redirect to Azure AD logout."""
    logout(request)

    # Build Azure AD logout URL
    post_logout_redirect = request.build_absolute_uri('/')
    logout_url = (
        f"https://login.microsoftonline.com/{settings.MS_ENTRA_TENANT_ID}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri={post_logout_redirect}"
    )

    return redirect(logout_url)
