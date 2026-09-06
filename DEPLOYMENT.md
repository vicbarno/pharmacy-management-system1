# Deployment Guide for Render

This document provides step-by-step instructions to deploy the Pharmacy Management System to Render.com.

## Prerequisites

1. A Render.com account (free tier available)
2. A GitHub repository with your code
3. A PostgreSQL database (the included `render.yaml` provisions one)
4. Environment variables configured

## Step 1: Prepare Your Repository

1. Push your code to GitHub with the new files:
   - `requirements.txt` (updated with production dependencies)
   - `render.yaml` or `Procfile`
   - `.env.example`
   - `pharm/settings.py` (updated for production)

2. Create a `.env` file locally (do NOT commit to Git):
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your actual values:
   ```
   SECRET_KEY=generate-a-secure-key-using-secrets.token_urlsafe()
   DEBUG=False
   DATABASE_URL=postgresql://...  (will be set by Render)
   ALLOWED_HOSTS=your-app-name.onrender.com
   CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

## Step 2: Create a PostgreSQL Database on Render

1. Go to Render.com and sign in
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `pharmacy-db` (or your choice)
   - Database: `pharmacy_db`
   - User: `pharmacy_user`
   - Region: Same as your web service
   - Version: Latest available

4. Copy the Internal Database URL (you'll need this for DATABASE_URL)

## Step 3: Deploy Your Web Service

### Option A: Using render.yaml (Recommended)

1. Push the repository to GitHub.
2. Go to Render.com → "New +" → "Blueprint".
3. Select your GitHub repository and choose the branch to deploy.
4. Render will provision the PostgreSQL database and web service from `render.yaml`.
5. Set `SECRET_KEY`, `EMAIL_HOST_USER`, and `EMAIL_HOST_PASSWORD` when prompted, then deploy.

### Option B: Manual Configuration

1. Go to Render.com → "New +" → "Web Service"
2. Select your GitHub repository
3. Configure the following:
   - **Name**: `pharmacy-management`
   - **Environment**: `Python 3.11`
   - **Build Command**:
     ```bash
       ./build.sh
     ```
   - **Start Command**: 
     ```bash
     gunicorn pharm.wsgi:application
     ```
   - **Plan**: Free tier (or paid)

## Step 4: Set Environment Variables

In the Render dashboard for your web service:

1. Go to **Environment** tab
2. Add these environment variables:
   - `DEBUG`: `False`
   - `SECRET_KEY`: Generate using Python: 
     ```python
     from django.core.management.utils import get_random_secret_key
     print(get_random_secret_key())
     ```
   - `DATABASE_URL`: Paste the Internal Database URL from PostgreSQL service
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://your-app-name.onrender.com`
   - `EMAIL_HOST_USER`: Your Gmail address
   - `EMAIL_HOST_PASSWORD`: Your Gmail app password (not regular password)

3. For Gmail:
   - Enable 2-factor authentication on your Gmail account
   - Generate an [App Password](https://myaccount.google.com/apppasswords)
   - Use that as `EMAIL_HOST_PASSWORD`

## Step 5: Enable Internal Networking

1. In Render dashboard, go to your PostgreSQL database
2. Note the Internal Database URL
3. In your web service environment variables, set `DATABASE_URL` to this Internal URL

## Step 6: Test Your Deployment

1. Wait for the deployment to complete
2. Visit: `https://your-app-name.onrender.com`
3. Check logs in Render dashboard if there are issues

## Step 7: Create Superuser (Admin)

After first successful deployment:

1. Go to your web service on Render
2. Click the three dots menu → "Connect"
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow the prompts to create an admin account
5. Access admin at: `https://your-app-name.onrender.com/admin`

## Troubleshooting

### Static Files Not Loading

- Ensure `STATIC_ROOT` is set correctly in `settings.py`
- Run `python manage.py collectstatic` locally to test
- Check that WhiteNoise middleware is installed

### Database Connection Errors

- Verify `DATABASE_URL` is correct in environment variables
- Ensure PostgreSQL service is running on Render
- Check that web service can access PostgreSQL (same region)

### Import Errors

- Verify all requirements are in `requirements.txt`
- Check that app imports work locally

### Migration Errors

- Run migrations locally to ensure they work: `python manage.py migrate --plan`
- Push migrations before deploying if needed

## Updates and Redeployment

Every time you push to GitHub:

1. Render automatically redeploys your application
2. `build.sh` (or build command) runs automatically
3. Database migrations run automatically
4. Static files are collected

To manually redeploy:
- In Render dashboard, click "Manual Deploy" on your service

## Monitoring

1. Check logs in Render dashboard under "Logs"
2. Set up alerts in "Settings" if needed
3. Monitor database usage

## Important Notes

- **Never commit `.env` file to GitHub** - it contains sensitive data
- Keep `SECRET_KEY` secure in environment variables
- Use strong passwords for database and admin accounts
- Enable HTTPS (automatic with Render)
- Test locally before pushing to production
- Regularly update dependencies for security patches

## Useful Commands

SSH into your Render service (for debugging):
```bash
# From Render dashboard, click "Connect" and use the provided command
```

View recent logs:
```bash
# In Render dashboard → Logs tab
```

Restart the service:
```bash
# In Render dashboard, click three dots → Restart
```

## Additional Resources

- [Render Docs](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://gunicorn.org/)
