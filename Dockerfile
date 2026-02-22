# ============================================================
# Stage 1: Build React frontend
# ============================================================
FROM node:18-alpine AS frontend-build

WORKDIR /app/web/frontend

# Install dependencies first (cache layer)
COPY web/frontend/package.json web/frontend/package-lock.json ./
RUN npm ci

# Copy source and build
COPY web/frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Python backend
# ============================================================
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system deps for C extensions, then clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn[standard] python-multipart && \
    apt-get purge -y --auto-remove gcc

# Copy application code
COPY pyproject.toml ./
COPY src/ ./src/
COPY web/backend/ ./web/backend/

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8007

CMD ["python", "-m", "uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8007"]

# ============================================================
# Stage 3: nginx serving frontend + proxying API
# ============================================================
FROM nginx:alpine AS nginx

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy built frontend from stage 1
COPY --from=frontend-build /app/web/frontend/dist/ /usr/share/nginx/html/

# Copy custom nginx config
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
