# Production deployment examples

The files in this directory are sanitized examples, not a copy of private server configuration.

1. Create a dedicated `arttoslipaway` system user.
2. Place the project in `/srv/arttoslipaway` and create its virtual environment as `.venv`.
3. Keep `/srv/arttoslipaway/.env` readable only by the service user.
4. Add the rate-limit declarations from `nginx/http-context.conf.example` to the Nginx `http {}` context.
5. Install the site configuration, validate it with `nginx -t`, then reload Nginx.
6. Install the systemd unit, run `systemctl daemon-reload`, and enable the service.

Replace the sample domain and certificate paths when deploying under another hostname.
