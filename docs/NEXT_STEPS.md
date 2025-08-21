## Next Steps for St. Edward Parish Directory

This checklist captures remaining work and safeguards. Follow in order.

### 1) Production readiness (Render)
- [ ] Verify environment variables:
  - [ ] `DEBUG=False`
  - [ ] `SECRET_KEY` set
  - [ ] `ALLOWED_HOSTS=parish-directory.onrender.com`
  - [ ] `MEDIA_ROOT=/opt/render/project/src/media`
  - [ ] `DATABASE_URL` present (postgresql://)
  - [ ] `CSRF_TRUSTED_ORIGINS=https://*.onrender.com` (or exact domain)
- [ ] Health Check Path: `/health` or `/healthz`
- [ ] Start: `gunicorn config.wsgi:application --preload --bind 0.0.0.0:10000`
- [ ] Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- [ ] Persistent Disk attached at `/opt/render/project/src/media`

### 2) Email verification
- [ ] Choose provider (recommend SES for cost, SendGrid for simplicity)
- [ ] Add env vars and update settings accordingly
  - SES: `EMAIL_HOST=email-smtp.<region>.amazonaws.com`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS=True`
  - SendGrid: `EMAIL_HOST=smtp.sendgrid.net`, `EMAIL_HOST_USER=apikey`, `EMAIL_HOST_PASSWORD=<API_KEY>`
- [ ] Verify sending domain and from-address
- [ ] Keep console backend fallback for safety in non-prod

### 3) Directory functionality
- [ ] Implement profile create/edit form view for users (`directory/profile_form.html` already present)
- [ ] Enforce that `Profile.parish` and `Profile.user` are set; create on first login if missing
- [ ] Approvals: admin sets `approved=True`; optionally add bulk approve action
- [ ] Directory list pagination (e.g., 24 per page)

### 4) Media security and processing
- [ ] Ensure all template image tags use `{% url 'directory:protected_media' path=profile.photo.name %}`
- [ ] Test portrait and landscape uploads; verify 600×400 or 400×600 and EXIF stripped
- [ ] Validate 25MB max upload (already in `ProfileForm`)

### 5) Tests (add before larger changes)
- [ ] Model image processing test (resize + format)
- [ ] Directory filter test (approved + opt_in)
- [ ] Protected media requires auth test
- [ ] Smoke tests: `/`, `/health`, signup/login flow

### 6) Admin UX
- [ ] Add `approved` bulk action
- [ ] Add readonly thumbnail preview in `ProfileAdmin`

### 7) Security hygiene
- [ ] Confirm `robots.txt` disallows indexing (route provided and file exists)
- [ ] Review headers in prod (HSTS, secure cookies already on)
- [ ] No public media URLs or PII in templates

### 8) Nice-to-haves (future)
- [ ] Multiple photos per profile
- [ ] Family pages and grouping
- [ ] Search/filter UI
- [ ] Rate limiting / lockout (`django-axes`)

---

### Command snippets
- Create superuser: `python manage.py createsuperuser`
- Run tests: `python manage.py test`

### Notes
- Root path redirects to directory or login.
- Email verification page styled at `templates/account/verification_sent.html`.

