# Parish Directory

A secure, login-required parish directory where members opt-in, create profiles (individual + family), and upload photos. Photos are automatically resized, EXIF-stripped, and optimized for security and performance.

## Features

- **Secure Authentication**: Email/password with mandatory email verification via django-allauth
- **Profile Management**: Individual and family profiles with photo uploads
- **Image Processing**: Automatic resize to 600×400 (landscape) or 400×600 (portrait), EXIF stripping, and optimization
- **Privacy Controls**: Opt-in directory with admin approval required
- **Protected Media**: All photos served through authenticated routes only

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (copy from `config/env.example`):
   ```bash
   cp config/env.example .env
   # Edit .env with your local settings
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Start development server:
   ```bash
   python manage.py runserver
   ```

## Render.com Deployment

### Build Command
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start Command
```bash
gunicorn config.wsgi:application --preload --bind 0.0.0.0:10000
```

### Environment Variables
Set these in your Render.com environment:

**Required:**
- `DEBUG=False`
- `SECRET_KEY` - Generate a secure random key
- `ALLOWED_HOSTS` - Your render domain (e.g., `your-app.onrender.com`)
- `DATABASE_URL` - PostgreSQL connection string from Render
- `MEDIA_ROOT=/opt/render/project/src/media`

**Email (choose one):**
- `EMAIL_HOST` - SMTP server (e.g., `smtp.sendgrid.net`)
- `EMAIL_HOST_USER` - Your email username/API key
- `EMAIL_HOST_PASSWORD` - Your email password/API secret
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `DEFAULT_FROM_EMAIL=directory@yourdomain.org`

**Optional:**
- `EMAIL_BACKEND` - Defaults to console backend if email settings omitted

### Persistent Disk Setup

**IMPORTANT**: Attach a Persistent Disk to your Render service:
- Mount point: `/opt/render/project/src/media`
- This ensures uploaded photos persist across deployments

### Security Features

- All directory and media routes require authentication
- Photos served through protected routes only
- HTTPS enforced in production
- Secure cookies and HSTS headers
- EXIF data stripped from uploaded images
- File size validation (25MB max)

## Architecture

- **Framework**: Django 5 with server-rendered templates
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: django-allauth with email verification
- **Static Files**: WhiteNoise with compression and manifest
- **Image Processing**: Pillow for resize, crop, and optimization
- **Media Storage**: Local filesystem with protected serving

## Models

- **Parish**: Church/parish information
- **Family**: Family units within a parish
- **Profile**: User profiles with photos and contact info

## Admin Interface

Access `/admin/` to:
- Approve profile directory opt-ins
- Manage parishes and families
- Monitor user registrations
- Control directory visibility

## Testing

Run basic tests:
```bash
python manage.py test directory
```

## License

Private project - PII-sensitive data handling.