# Technical Signal Vote Hunt Webapp

Interactive research console for the `technical_signal_vote_hunt` study.

The app has two processes:

- Python JSON API: serves `/api/health`, `/api/strategies`, `/api/report`.
- React/Vite frontend: renders the dashboard and proxies `/api/*` to the Python API in development.

All commands below assume the repository root is `/var/www/github/finances/market-lab`.

## 1. Install

Install Python dependencies from the repository as usual, then install frontend dependencies:

```bash
cd /var/www/github/finances/market-lab/studies/technical_signal_vote_hunt/webapp
make install
```

For a local development run:

```bash
make dev
```

Open:

```text
http://127.0.0.1:5173
```

If the port is busy, choose explicit ports:

```bash
make dev HOST=127.0.0.1 API_PORT=8773 WEB_PORT=5174
```

## 2. Run In Background

For VPS usage, prefer serving the production frontend with Nginx and keeping only the Python API as a background service.

Build the frontend:

```bash
cd /var/www/github/finances/market-lab/studies/technical_signal_vote_hunt/webapp
make build
```

The static frontend is generated at:

```text
/var/www/github/finances/market-lab/studies/technical_signal_vote_hunt/webapp/frontend/dist
```

Create a systemd service for the API:

```bash
sudo tee /etc/systemd/system/market-lab-tsvh-api.service >/dev/null <<'EOF'
[Unit]
Description=Market Lab Technical Signal Vote Hunt API
After=network.target

[Service]
Type=simple
WorkingDirectory=/var/www/github/finances/market-lab
ExecStart=/usr/bin/env uv run python -m studies.technical_signal_vote_hunt.webapp.api_server --host 127.0.0.1 --port 8765
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now market-lab-tsvh-api
sudo systemctl status market-lab-tsvh-api
```

Check the API:

```bash
curl -fsS http://127.0.0.1:8765/api/health
```

Useful service commands:

```bash
sudo systemctl restart market-lab-tsvh-api
sudo journalctl -u market-lab-tsvh-api -f
```

## 3. Nginx Proxy

Example Nginx site for `research.example.com`:

```nginx
server {
    listen 80;
    server_name research.example.com;

    root /var/www/github/finances/market-lab/studies/technical_signal_vote_hunt/webapp/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8765/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Install it:

```bash
sudo tee /etc/nginx/sites-available/market-lab-tsvh >/dev/null < nginx-site.conf
sudo ln -s /etc/nginx/sites-available/market-lab-tsvh /etc/nginx/sites-enabled/market-lab-tsvh
sudo nginx -t
sudo systemctl reload nginx
```

If using Certbot:

```bash
sudo certbot --nginx -d research.example.com
```

## Deployment Checklist

After code changes:

```bash
cd /var/www/github/finances/market-lab/studies/technical_signal_vote_hunt/webapp
make install
make build
sudo systemctl restart market-lab-tsvh-api
sudo systemctl reload nginx
```

Verify:

```bash
curl -fsS http://127.0.0.1:8765/api/health
curl -I https://research.example.com
```

## Notes

- The API intentionally binds to `127.0.0.1`; Nginx is the public entry point.
- Do not expose the Python API port directly on the internet.
- `node_modules/` is ignored by Git; commit `package.json` and `package-lock.json` instead.
- The app is research-only. DSR/PBO failures still block promotion under the project mandate.
