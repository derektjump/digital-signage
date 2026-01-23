# The Grid - Application Starter Kit

**Version:** 1.0
**Last Updated:** December 2024
**Purpose:** Template for spinning up new Grid ecosystem applications

---

## Overview

This guide provides everything needed to create a new application in The Grid ecosystem. It captures the design system, authentication patterns, project structure, and deployment workflow used across all Grid apps.

When creating a new application, provide Claude with:
1. The application name
2. The Git repository URL
3. The Azure Web App name (for deployment)

---

## Table of Contents

1. [Design System](#design-system)
2. [Project Structure](#project-structure)
3. [Authentication Setup](#authentication-setup)
4. [Navbar Component](#navbar-component)
5. [Interactive Grid Background](#interactive-grid-background)
6. [Base Styling](#base-styling)
7. [Git & Deployment](#git--deployment)
8. [Quick Start Checklist](#quick-start-checklist)

---

## Design System

### Color Palette

```css
/* Primary Brand Colors */
--grid-primary: #01ffff;          /* Cyan - accent color */
--grid-primary-glow: rgba(1, 255, 255, 0.15);

/* Background Colors */
--grid-bg-dark: #181818;          /* Main dark background */
--grid-bg-darker: #131315;        /* Deeper dark */
--grid-bg-card: #1e293b;          /* Card backgrounds (slate-800) */
--grid-bg-card-hover: #334155;    /* Card hover (slate-700) */

/* Text Colors */
--grid-text-primary: #e4e8ec;     /* Primary text (light) */
--grid-text-muted: #8b929a;       /* Muted/secondary text */
--grid-text-dark: #23263b;        /* Dark text (for light backgrounds) */

/* Border Colors */
--grid-border: rgba(255, 255, 255, 0.08);
--grid-border-hover: rgba(255, 255, 255, 0.14);
--grid-border-solid: #374151;     /* Gray-700 */

/* Button Colors */
--grid-button-primary: #2563eb;   /* Blue-600 */
--grid-button-hover: #60a5fa;     /* Blue-500 */

/* Chromatic Aberration (for grid effect) */
--grid-chroma-pink: rgba(255, 59, 129, 1);
--grid-chroma-cyan: rgba(0, 240, 255, 1);
--grid-chroma-purple: rgba(100, 52, 248, 1);
```

### Typography

```css
/* Font Families */
--font-primary: 'Onest', sans-serif;       /* Body text, UI elements */
--font-display: 'Oxanium', sans-serif;     /* Headings, buttons, badges */

/* Font Sizes */
--text-xs: 9px;      /* Labels, badges */
--text-sm: 11px;     /* Small text, captions */
--text-base: 12px;   /* Body text */
--text-md: 14px;     /* Medium text */
--text-lg: 16px;     /* Large text */
--text-xl: 18px;     /* Headings */
--text-2xl: 24px;    /* Large headings */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Google Fonts Import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&family=Oxanium:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@300;400;500&display=swap" rel="stylesheet">
```

### Border & Shadow Standards

```css
/* Borders */
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 6px;   /* Standard */
border-radius: 4px;   /* Small elements */
border-radius: 8px;   /* Cards, modals */

/* Shadows */
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);           /* Dropdowns */
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);           /* Cards */
box-shadow: 0 0 20px rgba(1, 255, 255, 0.15);        /* Cyan glow */
```

---

## Project Structure

```
{app_name}/
├── {app_name}/                    # Django project config
│   ├── __init__.py
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL config
│   ├── asgi.py                   # ASGI (WebSocket support)
│   ├── wsgi.py                   # WSGI (production)
│   └── middleware.py             # Custom middleware
│
├── {main_app}/                   # Main application
│   ├── models.py                 # Data models
│   ├── views.py                  # View handlers
│   ├── auth_views.py             # Azure AD authentication
│   ├── urls.py                   # App URL routing
│   ├── admin.py                  # Django admin
│   ├── context_processors.py     # Theme context
│   │
│   ├── services/                 # Business logic
│   │   └── (service modules)
│   │
│   ├── templates/
│   │   └── {main_app}/
│   │       ├── base.html         # Base template
│   │       ├── home.html         # Home page
│   │       └── partials/         # Reusable components
│   │           ├── _grid_badge.html
│   │           └── _user_menu.html
│   │
│   ├── static/
│   │   └── {main_app}/
│   │       ├── css/
│   │       │   ├── base.css
│   │       │   ├── navbar-grid.css
│   │       │   └── grid-badge.css
│   │       ├── js/
│   │       │   ├── navbar-grid.js
│   │       │   └── grid-badge.js
│   │       └── img/
│   │
│   └── migrations/               # Database migrations
│
├── staticfiles/                  # Collected static files
├── templates/                    # Root templates (if needed)
├── manage.py
├── requirements.txt
├── .env                          # Environment variables (not in git)
├── .env.example                  # Example env file
├── .gitignore
└── README.md
```

---

## Authentication Setup

### Environment Variables

```bash
# .env file
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET_VALUE=your-client-secret

# Database
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app.azurewebsites.net,localhost

# Redis (for caching/sessions)
REDIS_URL=redis://localhost:6379/0
```

### settings.py Authentication Config

```python
import os

# Azure AD / Microsoft Entra ID
MS_ENTRA_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
MS_ENTRA_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
MS_ENTRA_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET_VALUE')
MS_ENTRA_API_SCOPE = f'api://{MS_ENTRA_CLIENT_ID}/access'  # Adjust scope as needed

# Authentication
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'auth_login'
LOGIN_REDIRECT_URL = '/home/'

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True  # Production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# HTTPS settings (production)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
```

### auth_views.py - Complete Authentication Flow

```python
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
    redirect_uri = request.build_absolute_uri(reverse('auth_callback'))

    auth_url = msal_app.get_authorization_request_url(
        scopes=[settings.MS_ENTRA_API_SCOPE],
        state=state,
        redirect_uri=redirect_uri,
    )

    return redirect(auth_url)


def callback_view(request):
    """Handle Azure AD callback and create/update user."""
    # Validate state
    if request.GET.get('state') != request.session.get('auth_state'):
        return redirect('auth_login')

    # Check for errors
    if 'error' in request.GET:
        error = request.GET.get('error_description', request.GET.get('error'))
        # Handle error (log, show message, etc.)
        return redirect('auth_login')

    # Exchange code for tokens
    code = request.GET.get('code')
    if not code:
        return redirect('auth_login')

    msal_app = get_msal_app()
    redirect_uri = request.build_absolute_uri(reverse('auth_callback'))

    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=[settings.MS_ENTRA_API_SCOPE],
        redirect_uri=redirect_uri,
    )

    if 'error' in result:
        return redirect('auth_login')

    # Extract user info from ID token claims
    id_token_claims = result.get('id_token_claims', {})
    email = id_token_claims.get('preferred_username') or id_token_claims.get('email', '')

    if not email:
        return redirect('auth_login')

    # Create or update Django user
    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email': email}
    )

    if created:
        # Set user attributes from Azure AD claims
        user.first_name = id_token_claims.get('given_name', '')
        user.last_name = id_token_claims.get('family_name', '')
        user.save()

    # Store tokens in session
    request.session['access_token'] = result.get('access_token')
    request.session['refresh_token'] = result.get('refresh_token')
    request.session['id_token'] = result.get('id_token')
    request.session['id_token_claims'] = id_token_claims

    # Optionally store in database for persistence (UserSession model)
    # UserSession.objects.update_or_create(user=user, defaults={...})

    # Log user in
    login(request, user)

    # Clean up state
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
```

### URL Configuration

```python
# urls.py
from django.urls import path
from . import auth_views

urlpatterns = [
    path('login/', auth_views.login_view, name='auth_login'),
    path('callback/', auth_views.callback_view, name='auth_callback'),
    path('logout/', auth_views.logout_view, name='auth_logout'),
]
```

### UserSession Model (Optional - for token persistence)

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class UserSession(models.Model):
    """Persistent storage for user authentication tokens."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='session_data')
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    id_token = models.TextField(blank=True)
    token_type = models.CharField(max_length=50, default='Bearer')
    expires_at = models.DateTimeField(null=True, blank=True)
    scopes = models.JSONField(default=list)
    id_token_claims = models.JSONField(default=dict)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.user.username}"
```

---

## Navbar Component

### HTML Structure (base.html navbar section)

```html
<!-- Left Sidebar Navigation -->
<nav x-data="{
    open: false,
    miniNav: localStorage.getItem('miniNav') === 'true',
    isMobile: window.innerWidth < 768,
    showNavText: true
}"
     x-init="
         window.addEventListener('resize', () => { isMobile = window.innerWidth < 768 });
         $watch('miniNav', value => localStorage.setItem('miniNav', value));
     "
     x-effect="if (!miniNav) { setTimeout(() => showNavText = true, 500); } else { showNavText = false }"
     :class="{
         '-translate-x-full': isMobile && !open,
         'translate-x-0': !isMobile || open,
         'w-20': !isMobile && miniNav,
         'w-64': isMobile || !miniNav
     }"
     class="fixed top-0 left-0 h-screen z-30 transform transition-all duration-300 ease-in-out"
     style="background: #181818;">

  <!-- Interactive Grid Background -->
  <div class="navbar-grid-container">
    <canvas id="navbar-grid-canvas" class="navbar-grid-canvas"></canvas>
  </div>

  <!-- Mobile Close Button -->
  <button @click="open = false" x-show="open"
          class="absolute top-6 right-[-16px] z-50 flex items-center justify-center w-9 h-9 rounded-full md:hidden"
          style="background: #181818; border: 2px solid #374151;">
    <span class="material-symbols-outlined" style="font-size: 1.3rem; color: white;">close</span>
  </button>

  <div class="flex flex-col h-full">

    <!-- Logo Section -->
    <div class="flex flex-col items-stretch w-full">
      <div class="py-6 pb-3 px-4 flex flex-row items-center justify-center gap-2">
        <span style="font-family: 'Onest', sans-serif;">
          <img src="{% static 'app/img/logo.png' %}" alt="Logo"
               style="height: 50px; width: auto;"
               x-bind:style="miniNav ? 'height: 32px;' : 'height: 50px;'">
        </span>
      </div>
    </div>

    <!-- Grid App Badge -->
    <div class="px-4 mt-2" :class="miniNav ? 'px-3 flex justify-center' : 'px-4'">
      {% include 'partials/_grid_badge.html' %}
    </div>

    <!-- Collapse/Expand Button -->
    <button @click="miniNav = !miniNav"
            class="absolute top-6 right-[-16px] z-50 hidden md:flex items-center justify-center w-9 h-9 rounded-full"
            style="background: #181818; border: 2px solid #374151;">
      <span class="material-symbols-outlined" style="font-size: 1.3rem; color: white;"
            x-text="miniNav ? 'chevron_right' : 'chevron_left'"></span>
    </button>

    <!-- Navigation Items -->
    <ul class="space-y-1 px-3 mt-6 flex-1">
      <li>
        <a href="/home/" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors"
           :class="miniNav ? 'justify-center' : ''">
          <span class="material-symbols-outlined" style="color: #01ffff;">home</span>
          <span x-show="!miniNav" x-transition class="text-white text-sm" style="font-family: 'Onest';">Home</span>
        </a>
      </li>
      <!-- Add more nav items... -->
    </ul>

    <!-- User Menu (bottom of nav) -->
    <div class="mt-auto p-4 border-t border-white/10">
      {% include 'partials/_user_menu.html' %}
    </div>

  </div>
</nav>

<!-- Mobile Menu Toggle -->
<button @click="open = !open"
        class="fixed bottom-4 left-4 z-40 md:hidden flex items-center justify-center w-12 h-12 rounded-full"
        style="background: #181818; border: 2px solid #374151;">
  <span class="material-symbols-outlined text-white">menu</span>
</button>

<!-- Main Content Area -->
<main class="transition-all duration-300 min-h-screen"
      :class="isMobile ? 'ml-0' : (miniNav ? 'ml-20' : 'ml-64')"
      style="background: #0a0a0b;">
  {% block content %}{% endblock %}
</main>
```

---

## Interactive Grid Background

### CSS (navbar-grid.css)

```css
/**
 * Interactive Grid Background for Navbar
 */

.navbar-grid-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.navbar-grid-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

/* Fallback for no-JS */
.no-js .navbar-grid-container {
  background:
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}
```

### JavaScript (navbar-grid.js)

```javascript
/**
 * Interactive Mouse-Reactive Grid Background
 * Creates a Tron-like grid with chromatic aberration glow effect
 */

(function() {
  'use strict';

  const canvas = document.getElementById('navbar-grid-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const container = canvas.parentElement;

  // Configuration
  const config = {
    cellSize: 50,
    baseAlpha: 0.02,
    glowRadius: 150,
    influenceRadius: 300,
    lineWidth: 1,
    colors: {
      verticalLeft: 'rgba(255,59,129,',    // Pink
      verticalRight: 'rgba(0,240,255,',    // Cyan
      horizontalAbove: 'rgba(100,52,248,', // Purple
      horizontalBelow: 'rgba(255,255,255,' // White
    }
  };

  let mouseX = null, mouseY = null, isMouseInside = false;
  let animationFrameId = null, previousWidth = 0;

  function resizeCanvas() {
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    previousWidth = rect.width;

    // Smaller cells for collapsed nav
    if (rect.width < 100) {
      config.cellSize = 30;
      config.glowRadius = 100;
      config.influenceRadius = 200;
    } else {
      config.cellSize = 50;
      config.glowRadius = 150;
      config.influenceRadius = 300;
    }
    drawGrid();
  }

  function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = config.lineWidth;

    const { cellSize, baseAlpha, glowRadius, influenceRadius, colors } = config;

    // Vertical lines
    for (let x = 0; x <= canvas.width; x += cellSize) {
      const dx = mouseX !== null ? x - mouseX : null;
      let distanceFactor = 0;

      if (mouseX !== null && mouseY !== null && isMouseInside) {
        distanceFactor = Math.max(0, 1 - Math.abs(dx) / influenceRadius);
      }

      // Base line
      const alpha = baseAlpha + distanceFactor * 0.04;
      ctx.strokeStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
      ctx.beginPath();
      ctx.moveTo(x + 0.5, 0);
      ctx.lineTo(x + 0.5, canvas.height);
      ctx.stroke();

      // Glow segment
      if (mouseX !== null && mouseY !== null && isMouseInside && distanceFactor > 0) {
        let chromaIntensity = distanceFactor * 0.25;
        if (Math.abs(dx) < cellSize * 0.5) chromaIntensity = Math.min(0.6, chromaIntensity * 2);

        const yStart = Math.max(0, mouseY - glowRadius);
        const yEnd = Math.min(canvas.height, mouseY + glowRadius);
        const color = dx < 0 ? colors.verticalLeft : colors.verticalRight;

        const grad = ctx.createLinearGradient(0, yStart, 0, yEnd);
        const mid = Math.max(0, Math.min(1, (mouseY - yStart) / (yEnd - yStart)));

        grad.addColorStop(0.0, color + '0)');
        if (mid - 0.15 > 0) grad.addColorStop(mid - 0.15, color + (chromaIntensity * 0.3).toFixed(3) + ')');
        if (mid - 0.05 > 0) grad.addColorStop(mid - 0.05, color + (chromaIntensity * 0.8).toFixed(3) + ')');
        grad.addColorStop(mid, color + chromaIntensity.toFixed(3) + ')');
        if (mid + 0.05 < 1) grad.addColorStop(mid + 0.05, color + (chromaIntensity * 0.8).toFixed(3) + ')');
        if (mid + 0.15 < 1) grad.addColorStop(mid + 0.15, color + (chromaIntensity * 0.3).toFixed(3) + ')');
        grad.addColorStop(1.0, color + '0)');

        ctx.strokeStyle = grad;
        ctx.beginPath();
        ctx.moveTo(x + 0.5, yStart);
        ctx.lineTo(x + 0.5, yEnd);
        ctx.stroke();
      }
    }

    // Horizontal lines (similar pattern)
    for (let y = 0; y <= canvas.height; y += cellSize) {
      const dy = mouseY !== null ? y - mouseY : null;
      let distanceFactor = 0;

      if (mouseX !== null && mouseY !== null && isMouseInside) {
        distanceFactor = Math.max(0, 1 - Math.abs(dy) / (cellSize * 4));
      }

      const alpha = baseAlpha + distanceFactor * 0.04;
      ctx.strokeStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
      ctx.beginPath();
      ctx.moveTo(0, y + 0.5);
      ctx.lineTo(canvas.width, y + 0.5);
      ctx.stroke();

      if (mouseX !== null && mouseY !== null && isMouseInside && distanceFactor > 0) {
        let chromaIntensity = distanceFactor * 0.25;
        if (Math.abs(dy) < cellSize * 0.5) chromaIntensity = Math.min(0.6, chromaIntensity * 2);

        const xStart = Math.max(0, mouseX - glowRadius);
        const xEnd = Math.min(canvas.width, mouseX + glowRadius);
        const color = dy < 0 ? colors.horizontalAbove : colors.horizontalBelow;
        let maxAlpha = chromaIntensity;
        if (dy >= 0) maxAlpha *= 0.5;

        const grad = ctx.createLinearGradient(xStart, 0, xEnd, 0);
        const mid = Math.max(0, Math.min(1, (mouseX - xStart) / (xEnd - xStart)));

        grad.addColorStop(0.0, color + '0)');
        if (mid - 0.15 > 0) grad.addColorStop(mid - 0.15, color + (maxAlpha * 0.3).toFixed(3) + ')');
        if (mid - 0.05 > 0) grad.addColorStop(mid - 0.05, color + (maxAlpha * 0.8).toFixed(3) + ')');
        grad.addColorStop(mid, color + maxAlpha.toFixed(3) + ')');
        if (mid + 0.05 < 1) grad.addColorStop(mid + 0.05, color + (maxAlpha * 0.8).toFixed(3) + ')');
        if (mid + 0.15 < 1) grad.addColorStop(mid + 0.15, color + (maxAlpha * 0.3).toFixed(3) + ')');
        grad.addColorStop(1.0, color + '0)');

        ctx.strokeStyle = grad;
        ctx.beginPath();
        ctx.moveTo(xStart, y + 0.5);
        ctx.lineTo(xEnd, y + 0.5);
        ctx.stroke();
      }
    }
  }

  function animate() {
    const currentWidth = container.offsetWidth;
    if (Math.abs(currentWidth - previousWidth) > 10) resizeCanvas();
    drawGrid();
    animationFrameId = requestAnimationFrame(animate);
  }

  function handleMouseMove(e) {
    const rect = container.getBoundingClientRect();
    if (e.clientX >= rect.left && e.clientX <= rect.right &&
        e.clientY >= rect.top && e.clientY <= rect.bottom) {
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
      isMouseInside = true;
    } else {
      isMouseInside = false;
    }
  }

  // Initialize
  window.addEventListener('resize', () => setTimeout(resizeCanvas, 150));
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseleave', () => { isMouseInside = false; });

  // Handle collapse button
  document.querySelector('.collapse-expand-btn')?.addEventListener('click', () => {
    setTimeout(resizeCanvas, 50);
  });

  setTimeout(() => {
    if (container.offsetWidth > 0) {
      resizeCanvas();
      animate();
    }
  }, 50);
})();
```

---

## Grid Badge Component

### HTML (_grid_badge.html)

```html
{% load static %}

<button type="button" class="grid-badge"
        aria-label="Open The Grid app menu"
        aria-expanded="false" aria-haspopup="true" tabindex="0">

  <!-- Header: Icon + Title -->
  <div class="grid-badge__header">
    <span class="grid-badge__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none">
        <rect x="3" y="3" width="5" height="5" rx="1" fill="currentColor"/>
        <rect x="10" y="3" width="5" height="5" rx="1" fill="currentColor" fill-opacity="0.7"/>
        <rect x="17" y="3" width="5" height="5" rx="1" fill="currentColor" fill-opacity="0.5"/>
        <rect x="3" y="10" width="5" height="5" rx="1" fill="currentColor" fill-opacity="0.7"/>
        <rect x="10" y="10" width="5" height="5" rx="1" fill="currentColor"/>
        <rect x="17" y="10" width="5" height="5" rx="1" fill="currentColor" fill-opacity="0.7"/>
        <rect x="3" y="17" width="5" height="5" rx="1" fill="currentColor" fill-opacity="0.5"/>
        <rect x="10" y="17" width="5" height="5" rx="1" fill="currentColor" fill-opacity="0.7"/>
        <rect x="17" y="17" width="5" height="5" rx="1" fill="currentColor"/>
      </svg>
    </span>
    <span class="grid-badge__title">The Grid</span>
  </div>

  <!-- Connector + App Name -->
  <div class="grid-badge__app-row">
    <span class="grid-badge__connector" aria-hidden="true">
      <span class="grid-badge__connector-dot"></span>
    </span>
    <span class="grid-badge__app-name">{{ app_name|default:"App Name" }}</span>
  </div>

  <!-- Tooltip (collapsed state) -->
  <span class="grid-badge__tooltip" role="tooltip">The Grid &mdash; Open apps</span>

  <!-- Dropdown Menu -->
  <nav class="grid-badge__menu" role="menu" aria-label="Grid apps">
    <div class="grid-badge__menu-header">
      <a href="https://the-grid-hub-url.com/" class="grid-badge__menu-hub-link" role="menuitem">
        <span class="grid-badge__menu-hub-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
            <path d="M10 19l-7-7 7-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M3 12h18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </span>
        <span>Back to The Grid</span>
      </a>
    </div>

    <div class="grid-badge__menu-section-title">Switch Apps</div>

    <!-- App Links -->
    <a href="/" class="grid-badge__menu-item grid-badge__menu-item--current" role="menuitem" aria-current="page">Current App</a>
    <a href="https://other-app.com/" class="grid-badge__menu-item" role="menuitem">Other App</a>
    <span class="grid-badge__menu-item grid-badge__menu-item--disabled" role="menuitem" aria-disabled="true">
      Future App <span class="grid-badge__coming-soon">Coming Soon</span>
    </span>
  </nav>
</button>
```

### CSS (grid-badge.css) - Key Styles

```css
/* See full implementation in ai_chat/static/ai_chat/css/grid-badge.css */

:root {
  --grid-badge-bg: rgba(255, 255, 255, 0.04);
  --grid-badge-bg-hover: rgba(255, 255, 255, 0.08);
  --grid-badge-border: rgba(255, 255, 255, 0.08);
  --grid-badge-text: #e4e8ec;
  --grid-badge-text-muted: #8b929a;
  --grid-badge-accent: #01ffff;
  --grid-badge-glow: rgba(1, 255, 255, 0.15);
}

.grid-badge {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 12px 16px 14px;
  background: var(--grid-badge-bg);
  border: 1px solid var(--grid-badge-border);
  border-radius: 6px;
  cursor: pointer;
}

/* Collapsed state */
.grid-badge--collapsed {
  padding: 12px;
  width: auto;
}

.grid-badge--collapsed .grid-badge__title,
.grid-badge--collapsed .grid-badge__app-row {
  max-width: 0;
  opacity: 0;
}
```

---

## Base Styling

### Main Background (for content area)

```css
/* Dark gradient background */
main {
  background: #0a0a0b;
  min-height: 100vh;
}

/* Alternative: subtle gradient */
main {
  background: linear-gradient(180deg, #0a0a0b 0%, #111113 100%);
}
```

### Card Components

```css
.card {
  background: rgba(30, 41, 59, 0.8);  /* slate-800 with transparency */
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 1rem;
}

.card:hover {
  background: rgba(51, 65, 85, 0.8);  /* slate-700 */
  border-color: rgba(255, 255, 255, 0.14);
}
```

### Buttons

```css
.btn-primary {
  background: #2563eb;
  color: white;
  font-family: 'Oxanium', sans-serif;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  transition: background 150ms ease;
}

.btn-primary:hover {
  background: #3b82f6;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.06);
  color: #e4e8ec;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}
```

---

## Git & Deployment

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Django
*.log
local_settings.py
db.sqlite3
media/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Static files (if using collectstatic)
# staticfiles/

# Temporary
*.tmp
*.temp
```

### Azure Deployment

**startup.txt** (Azure App Service startup command):
```bash
gunicorn --bind=0.0.0.0 --timeout 600 --workers 2 {project_name}.wsgi
```

**requirements.txt** (core dependencies):
```txt
Django>=5.0
gunicorn
whitenoise
psycopg2-binary
msal
python-dotenv
redis
django-redis
```

### Git Workflow

```bash
# Initial setup
git init
git remote add origin https://github.com/{org}/{repo}.git

# Standard workflow
git add .
git commit -m "Description of changes"
git push origin main

# Azure auto-deploys from main branch via GitHub Actions or Azure DevOps
```

### GitHub Actions (optional - .github/workflows/azure.yml)

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

---

## Quick Start Checklist

When creating a new Grid application:

### 1. Project Setup
- [ ] Create Django project: `django-admin startproject {project_name}`
- [ ] Create main app: `python manage.py startapp {app_name}`
- [ ] Copy base templates from this guide
- [ ] Copy static files (CSS, JS) from this guide
- [ ] Set up `.env` with Azure AD credentials

### 2. Authentication
- [ ] Add `auth_views.py` with login/callback/logout
- [ ] Configure `settings.py` with Azure AD settings
- [ ] Add auth URLs to `urls.py`
- [ ] Test login flow

### 3. Navbar & Styling
- [ ] Add navbar HTML to `base.html`
- [ ] Include `navbar-grid.css` and `navbar-grid.js`
- [ ] Include `grid-badge.css` and `grid-badge.js`
- [ ] Add `_grid_badge.html` partial
- [ ] Update Grid Badge with app-specific links

### 4. Database
- [ ] Configure PostgreSQL connection
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`

### 5. Git & Deployment
- [ ] Initialize git repository
- [ ] Add `.gitignore`
- [ ] Create Azure Web App
- [ ] Configure deployment (GitHub Actions or Azure DevOps)
- [ ] Set environment variables in Azure

### 6. Customization
- [ ] Update app name in navbar
- [ ] Update logo image
- [ ] Add app-specific navigation items
- [ ] Customize Grid Badge dropdown links
- [ ] Add app-specific views and functionality

---

## File Reference

Key files to copy from the reference implementation:

| File | Purpose |
|------|---------|
| `static/css/navbar-grid.css` | Grid background styles |
| `static/js/navbar-grid.js` | Interactive grid effect |
| `static/css/grid-badge.css` | Grid badge component |
| `static/js/grid-badge.js` | Badge dropdown behavior |
| `templates/partials/_grid_badge.html` | Badge HTML template |
| `auth_views.py` | Azure AD authentication |

---

*This guide is maintained as part of The Grid ecosystem. For updates, see the Prompted application repository.*
