# The Grid App Template - Setup Guide

This is a template for creating new applications within The Grid ecosystem. Follow this guide when starting a new app from this template.

---

## Instructions for AI Assistant

When a user wants to create a new app from this template, follow these steps:

### 1. Gather Required Information

Ask the user for the following (one message, all questions):

```
I'll help you set up a new Grid app from this template. Please provide:

1. **App Name** - Display name (e.g., "Shopify Manager")
2. **Project Slug** - For Django project folder, snake_case (e.g., "shopify_manager")
3. **App Slug** - For Django app folder, snake_case (e.g., "shopify")
4. **Repository URL** - Where to push the code (GitHub/Azure DevOps)
5. **Database** - New Azure PostgreSQL, or connection string if existing
6. **Azure AD** - Create new app registration, or provide existing credentials
```

### 2. Perform Renaming

After gathering info, rename in this order:
1. Update `context_processors.py` with new app name
2. Rename folders (project folder, app folder, static/templates subfolders)
3. Update all Python files with new import paths
4. Update all template files with new paths
5. Update settings.py with all new references

### 3. Configure Environment

Create/update `.env` file with:
- APP_NAME and APP_SHORT_NAME
- Database connection
- Azure AD credentials
- Secret key

### 4. Git Setup

```bash
rm -rf .git
git init
git add .
git commit -m "Initial commit: {App Name} from Grid template"
git remote add origin {repository_url}
git push -u origin main
```

### 5. Verify

- Run `python manage.py migrate`
- Run `python manage.py runserver`
- Test authentication flow
- Verify all static files load

---

## Quick Start Checklist

When starting a new app, the assistant should ask for:

1. **App Name** - Display name (e.g., "Shopify Manager", "Digital Signage")
2. **Project Slug** - Snake_case for Django project (e.g., `shopify_manager`)
3. **App Slug** - Snake_case for Django app (e.g., `shopify`)
4. **Repository URL** - GitHub/Azure DevOps repo URL
5. **Azure AD App Registration** - Client ID, Tenant ID, Client Secret (or create new)
6. **Database** - Connection string or create new Azure PostgreSQL

---

## Project Structure

```
├── customer_lifecycle/          # Django PROJECT folder (rename this)
│   ├── __init__.py
│   ├── settings.py              # Main configuration
│   ├── urls.py                  # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
├── lifecycle/                   # Django APP folder (rename this)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── auth_views.py            # Azure AD authentication
│   ├── models.py
│   ├── urls.py                  # App URL routing
│   ├── views.py
│   ├── static/lifecycle/        # Static files (rename inner folder)
│   │   ├── css/
│   │   └── js/
│   └── templates/lifecycle/     # Templates (rename inner folder)
│       ├── base.html
│       ├── home.html
│       └── partials/
├── manage.py
├── requirements.txt
└── .env                         # Environment variables (create this)
```

---

## Renaming the Project

### Step 1: Rename Folders

1. Rename `customer_lifecycle/` to `{project_slug}/`
2. Rename `lifecycle/` to `{app_slug}/`
3. Rename `lifecycle/static/lifecycle/` to `{app_slug}/static/{app_slug}/`
4. Rename `lifecycle/templates/lifecycle/` to `{app_slug}/templates/{app_slug}/`

### Step 2: Update Files

**manage.py:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_slug}.settings')
```

**{project_slug}/settings.py:**
```python
ROOT_URLCONF = '{project_slug}.urls'
WSGI_APPLICATION = '{project_slug}.wsgi.application'

INSTALLED_APPS = [
    ...
    '{app_slug}',
]

TEMPLATES = [
    {
        ...
        'DIRS': [BASE_DIR / '{app_slug}' / 'templates'],
        ...
    }
]
```

**{project_slug}/urls.py:**
```python
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('{app_slug}.urls')),
]
```

**{project_slug}/wsgi.py & asgi.py:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_slug}.settings')
```

**{app_slug}/apps.py:**
```python
class {AppSlugCamelCase}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_slug}'
```

**All template files** - Update paths:
- `{% extends '{app_slug}/base.html' %}`
- `{% include '{app_slug}/partials/_grid_badge.html' %}`
- `{% static '{app_slug}/css/...' %}`
- `{% static '{app_slug}/js/...' %}`

---

## Environment Variables

Create a `.env` file in the project root:

```env
# ===========================================
# App Identity (shown in UI)
# ===========================================
APP_NAME=Your App Name
APP_SHORT_NAME=AppName

# ===========================================
# Django Core
# ===========================================
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.azurewebsites.net

# ===========================================
# Database (Azure PostgreSQL)
# ===========================================
DATABASE_URL=postgres://user:password@host:5432/dbname

# ===========================================
# Azure AD / Microsoft Entra ID
# ===========================================
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET_VALUE=your-client-secret

# ===========================================
# Redis (optional, for caching/sessions)
# ===========================================
REDIS_URL=redis://localhost:6379/0
```

---

## Azure AD App Registration

### Create New App Registration

1. Go to Azure Portal > Microsoft Entra ID > App registrations
2. Click "New registration"
3. Configure:
   - **Name**: Your app name
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Web - `https://your-app.azurewebsites.net/callback/`
4. After creation, note:
   - **Application (client) ID** → `AZURE_CLIENT_ID`
   - **Directory (tenant) ID** → `AZURE_TENANT_ID`
5. Go to "Certificates & secrets" > "New client secret"
   - Copy the **Value** → `AZURE_CLIENT_SECRET_VALUE`

### API Permissions

Ensure these permissions are granted:
- Microsoft Graph > User.Read (Delegated)

---

## Database Setup

### Azure PostgreSQL

1. Create Azure Database for PostgreSQL flexible server
2. Configure firewall rules
3. Create database
4. Get connection string for `DATABASE_URL`

### Local Development

```bash
# Use SQLite for local dev (already configured as fallback)
# Or run PostgreSQL locally via Docker:
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

---

## Git Repository Setup

```bash
# Remove existing git history
rm -rf .git

# Initialize new repo
git init
git add .
git commit -m "Initial commit from Grid template"

# Add remote and push
git remote add origin {repository_url}
git branch -M main
git push -u origin main
```

---

## Design System Reference

### Colors

| Name | Hex | Usage |
|------|-----|-------|
| Cyan (Primary) | `#01ffff` | Primary buttons, accents, icons |
| Cyan Hover | `#00e6e6` | Button hover states |
| Cyan Glow | `rgba(1, 255, 255, 0.15)` | Shadows, glows |
| Dark Background | `#0a0a0b` | Nav background |
| Dark Surface | `rgba(20, 20, 22, 0.97)` | Dropdowns, modals |
| Light Background | `#eaeff4` | Main content area |
| Text Primary | `#e4e8ec` | Light text on dark |
| Text Muted | `#8b929a` | Secondary text |
| Text Dark | `#23263b` | Dark text on light |
| Border Light | `rgba(255, 255, 255, 0.08)` | Subtle borders on dark |

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Headings | Oxanium | 500-600 | 14-24px |
| Body | Onest | 400 | 12-14px |
| Nav Links | Oxanium | 200 | 14px |
| Labels | Onest | 500 | 9-11px |

### Components

**Primary Button (Cyan)**
```html
<button class="inline-flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
        style="font-family: 'Oxanium', sans-serif; background: #01ffff; color: #131315;"
        onmouseover="this.style.background='#00e6e6'"
        onmouseout="this.style.background='#01ffff'">
    <span class="material-symbols-outlined" style="font-size: 1.1rem;">add</span>
    Button Text
</button>
```

**Secondary Button (White/Outlined)**
```html
<button class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        style="font-family: 'Oxanium', sans-serif;">
    <span class="material-symbols-outlined" style="font-size: 1.1rem;">icon</span>
    Button Text
</button>
```

**Dropdown/Modal Background**
```css
background: rgba(20, 20, 22, 0.97);
border: 1px solid rgba(255, 255, 255, 0.08);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5),
            0 0 1px rgba(255, 255, 255, 0.1),
            0 0 20px rgba(1, 255, 255, 0.15);
```

### Icons

Using Google Material Symbols Outlined with variable font settings:
```css
.ultra-thin-icon {
    font-variation-settings: 'FILL' 0, 'wght' 200, 'GRAD' 0, 'opsz' 24;
}
```

---

## Grid Badge Configuration

The Grid Badge (`_grid_badge.html`) shows the current app and links to other Grid apps. Update:

1. **Current app name** in the template
2. **App links** in the dropdown menu
3. **"Back to The Grid"** link to your Grid hub

---

## Deployment Checklist

- [ ] Renamed project and app folders
- [ ] Updated all import paths and settings
- [ ] Created `.env` with all required variables
- [ ] Set up Azure AD app registration
- [ ] Configured database connection
- [ ] Updated Grid Badge with correct app links
- [ ] Pushed to new repository
- [ ] Deployed to Azure App Service
- [ ] Configured Azure App Service environment variables
- [ ] Tested authentication flow
- [ ] Verified all static files load correctly

---

## Common Issues

### Static files not loading
- Run `python manage.py collectstatic`
- Check `STATIC_URL` and `STATICFILES_DIRS` in settings

### Authentication redirect errors
- Verify redirect URI matches exactly in Azure AD
- Check `ALLOWED_HOSTS` includes your domain

### Template not found
- Ensure template paths updated to new app name
- Check `TEMPLATES['DIRS']` in settings

### Database connection issues
- Verify `DATABASE_URL` format
- Check Azure firewall rules
- Ensure SSL mode configured if required
