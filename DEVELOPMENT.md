# Development Setup Guide

This guide helps you set up the Pharmacy Management System for local development.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git
- PostgreSQL (optional, SQLite is used for development by default)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd pharmacy-management
```

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` for development:
```
DEBUG=True
SECRET_KEY=django-insecure-your-development-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Collect Static Files (Optional for Development)

```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

Admin panel: `http://localhost:8000/admin`

## Development Workflow

### Making Changes

1. Make your code changes
2. Test locally: `python manage.py test`
3. Check code quality: `flake8 pharmacy/`
4. Format code: `black pharmacy/`
5. Sort imports: `isort pharmacy/`

### Creating Migrations

After modifying models:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Database Management

View all tables:
```bash
python manage.py dbshell
```

Reset database (WARNING: deletes all data):
```bash
python manage.py flush
```

### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=pharmacy
```

## Useful Django Commands

```bash
# Create a new app
python manage.py startapp app_name

# Check for problems
python manage.py check

# View all installed apps
python manage.py shell

# Dump data to file
python manage.py dumpdata > data.json

# Load data from file
python manage.py loaddata data.json

# Change password
python manage.py changepassword username

# Clear cache
python manage.py clear_cache
```

## Code Style Guidelines

- Follow PEP 8 style guide
- Use Black for code formatting
- Use isort for import organization
- Use type hints where applicable
- Write docstrings for functions and classes

## Project Structure

```
pharmacy-management/
├── pharm/                  # Main Django project
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── pharmacy/               # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # App URL routing
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin interface
│   └── migrations/         # Database migrations
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── manage.py               # Django command-line utility
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md               # Project documentation
```

## Troubleshooting

### Module Not Found Error

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements-dev.txt
```

### Database Error

```bash
# Reset database
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Not Loading

```bash
python manage.py collectstatic --clear --noinput
```

### Port 8000 Already in Use

```bash
python manage.py runserver 8001
```

## VS Code Setup (Recommended)

Install extensions:
- Python
- Django
- Pylance
- Black Formatter

Create `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

## Next Steps

1. Read the main [README.md](README.md)
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
3. Review the codebase structure
4. Set up your IDE of choice
5. Start developing!

## Getting Help

- Django Documentation: https://docs.djangoproject.com/
- Django Community: https://www.djangoproject.com/community/
- Stack Overflow: Tag your questions with `django` and `python`
