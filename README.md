# Customer Lifecycle

Part of **The Grid** ecosystem.

## Overview

Customer Lifecycle is a Django application for tracking and managing customer journey stages from acquisition to retention.

## Setup

### Prerequisites
- Python 3.11+
- Azure AD tenant (for authentication)

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure AD credentials
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Open http://localhost:8000 in your browser.

## Deployment

This application is configured for Azure App Service deployment.

### Azure Web App
- App Name: `customer-lifecycle`
- Startup Command: Contents of `startup.txt`

### Environment Variables
Set the following in Azure App Service Configuration:
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET_VALUE`
- `DATABASE_URL`
- `CSRF_TRUSTED_ORIGINS`

## Tech Stack

- **Backend:** Django 5.0+
- **Authentication:** Microsoft Entra ID (Azure AD)
- **Styling:** Tailwind CSS, Custom Grid Design System
- **Frontend:** Alpine.js
- **Database:** PostgreSQL (production), SQLite (development)
