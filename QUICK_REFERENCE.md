# Render Deployment Quick Reference

## File Overview

| File | Purpose | Action |
|------|---------|--------|
| `requirements.txt` | Production dependencies | Updated ✅ |
| `pharm/settings.py` | Django configuration | Updated ✅ |
| `render.yaml` | Render deployment config | Created ✅ |
| `Procfile` | Process definition | Created ✅ |
| `.env.example` | Environment variables template | Created ✅ |
| `.env` | Actual environment variables | **Create locally, DON'T commit** |
| `build.sh` | Build script | Created ✅ |
| `DEPLOYMENT.md` | Deployment instructions | Created ✅ |
| `DEVELOPMENT.md` | Dev setup guide | Created ✅ |

## Environment Variables Required

```env
# Django
DEBUG=False                                    # Set to False in production
SECRET_KEY=<generate-secure-key>             # Use Django's get_random_secret_key()

# Database
DATABASE_URL=postgresql://user:pass@host/db  # Provided by Render

# Hosts
ALLOWED_HOSTS=your-app-name.onrender.com     # Your Render domain
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com

# Email (Gmail)
EMAIL_HOST_USER=your-email@gmail.com         # Your Gmail
EMAIL_HOST_PASSWORD=<16-char-app-password>   # Generate via myaccount.google.com
```

## Deployment Flow

```
GitHub Push
    ↓
Render detects push
    ↓
Builds image (render.yaml)
    ↓
pip install -r requirements.txt
    ↓
python manage.py collectstatic --noinput
    ↓
python manage.py migrate
    ↓
gunicorn pharm.wsgi:application
    ↓
App running at your-app-name.onrender.com ✅
```

## Quick Commands

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver

# Test production build
gunicorn pharm.wsgi:application
```

### Generate Django Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --plan  # Preview
```

## Render Dashboard Steps

1. **Sign up/Login** at render.com
2. **Create PostgreSQL** → Copy Internal Database URL
3. **Create Web Service** → Select GitHub repo
4. **Configure** → Set build and start commands (or use render.yaml)
5. **Environment Variables** → Add all from .env.example
6. **Deploy** → Watch build logs
7. **Test** → Visit your-app-name.onrender.com

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Static files not loading | Run: `python manage.py collectstatic` |
| Database connection error | Check DATABASE_URL in environment vars |
| Email not sending | Verify EMAIL_HOST_USER and app password |
| ModuleNotFoundError | Check all packages in requirements.txt |
| 500 Internal Error | Check Render logs, verify migrations |
| CSRF token error | Add domain to CSRF_TRUSTED_ORIGINS |

## Security Checklist

- [ ] SECRET_KEY is unique and not in code
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS is set to your domain
- [ ] CSRF_TRUSTED_ORIGINS includes your domain
- [ ] Database credentials never in code
- [ ] Email password is app password (not real password)
- [ ] HTTPS is enforced (automatic with Render)
- [ ] Admin password is strong

## Production Best Practices

✅ Use environment variables for all secrets
✅ Enable HTTPS (automatic with Render)
✅ Use strong database passwords
✅ Regularly backup database
✅ Monitor application logs
✅ Set up email alerts for errors
✅ Keep dependencies updated
✅ Run migrations before deployment

❌ Never hardcode secrets
❌ Don't use DEBUG=True in production
❌ Don't commit .env file
❌ Don't expose database credentials
❌ Don't ignore security warnings

## Links & Resources

- [Render Documentation](https://render.com/docs)
- [Django 4.2 Docs](https://docs.djangoproject.com/en/4.2/)
- [Gunicorn Docs](https://gunicorn.org/)
- [Gmail App Passwords](https://myaccount.google.com/apppasswords)
- [Django Secret Key Generator](https://djecrety.ir/)

## Support

For deployment issues:
1. Check Render logs: Dashboard → Logs
2. Read [DEPLOYMENT.md](DEPLOYMENT.md)
3. Review Django deployment checklist
4. Check environment variables

---

**Ready to Deploy?** 
→ Follow [DEPLOYMENT.md](DEPLOYMENT.md) step-by-step
