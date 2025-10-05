# Multi-stage Dockerfile for all services
ARG SERVICE_TYPE=backend
ARG SERVICE_NAME

##############################
# Backend services stage
##############################
FROM python:3.9-slim AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy services
COPY services/ ./services/

# Install any additional service-specific requirements
ARG SERVICE_NAME
RUN if [ -f "./services/${SERVICE_NAME}/requirements.txt" ]; then \
    pip install --no-cache-dir -r "./services/${SERVICE_NAME}/requirements.txt"; \
    fi

WORKDIR /app/services/${SERVICE_NAME}

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

##############################
# Frontend stage
##############################
FROM node:22-alpine AS frontend
WORKDIR /app

# Copy package files first
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build app
RUN npm run build

EXPOSE 5173
CMD ["npm", "run", "dev"]



##############################
# Final stage (select type)
##############################
FROM ${SERVICE_TYPE} AS final
