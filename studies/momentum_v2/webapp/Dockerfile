# Optional container for the momentum_v2 portfolio web-app (one uvicorn process
# serving the API + the built SPA). Build from the REPO ROOT:
#   docker build -f studies/momentum_v2/webapp/Dockerfile -t momentum-portfolio .
#   docker run -p 8000:8000 momentum-portfolio
# The exported snapshot under studies/momentum_v2/universes/<u>/<window>/portfolio/
# must exist at build time (run the funnel + portfolio_export.py first) or be mounted.

# --- frontend build ---
FROM node:20-slim AS frontend
WORKDIR /fe
COPY studies/momentum_v2/webapp/frontend/package*.json ./
RUN npm install
COPY studies/momentum_v2/webapp/frontend/ ./
RUN npm run build

# --- python runtime ---
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml README.md ./
COPY src ./src
COPY studies ./studies
RUN uv pip install --system -e '.[webapp]'
COPY --from=frontend /fe/dist studies/momentum_v2/webapp/frontend/dist
EXPOSE 8000
CMD ["uvicorn", "studies.momentum_v2.webapp.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
