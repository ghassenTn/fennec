# Docker and Deployment Guide 🦊

Complete guide for deploying Fennec applications using Docker, Docker Compose, and various cloud platforms.

## Project Structure

```
deployment/
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Multi-service orchestration
├── nginx.conf              # Nginx reverse proxy config
├── requirements.txt        # Python dependencies
├── .dockerignore          # Docker build exclusions
├── .env.example           # Environment variables template
├── main.py                # Production-ready app example
└── README.md              # This file
```

## Quick Start

### 1. Clone and Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access the Application

- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Nginx Proxy**: http://localhost:80

## Docker

### Building the Image

```bash
# Build image
docker build -t fennec-api:latest .

# Build with specific tag
docker build -t fennec-api:1.0.0 .
```

### Running a Container

```bash
# Run container
docker run -d \
  --name fennec-api \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://... \
  fennec-api:latest

# View logs
docker logs -f fennec-api

# Stop container
docker stop fennec-api

# Remove container
docker rm fennec-api
```

### Multi-Stage Build Benefits

The Dockerfile uses multi-stage builds for:
- **Smaller image size**: Only production dependencies
- **Security**: No build tools in final image
- **Speed**: Cached build layers

## Docker Compose

### Services

1. **api**: Fennec application
2. **postgres**: PostgreSQL database
3. **redis**: Redis cache
4. **nginx**: Reverse proxy and load balancer

### Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# View logs
docker-compose logs -f api

# Execute command in container
docker-compose exec api python manage.py migrate

# Scale service
docker-compose up -d --scale api=3

# Restart service
docker-compose restart api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Environment Variables

Create `.env` file:

```bash
SECRET_KEY=your-secret-key-change-in-production
DEBUG=false
DATABASE_URL=postgresql://postgres:password@postgres:5432/fennec_db
REDIS_URL=redis://redis:6379/0
```

## Nginx Configuration

### Features

- **Reverse Proxy**: Routes requests to API
- **Load Balancing**: Distributes traffic
- **Rate Limiting**: Prevents abuse
- **WebSocket Support**: For real-time features
- **SSL/TLS**: HTTPS support (commented out)
- **Gzip Compression**: Reduces bandwidth
- **Security Headers**: XSS, clickjacking protection

### SSL/TLS Setup

1. Generate certificates:
```bash
# Self-signed (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Let's Encrypt (production)
certbot certonly --standalone -d yourdomain.com
```

2. Uncomment HTTPS server block in `nginx.conf`

3. Update certificate paths

4. Restart nginx:
```bash
docker-compose restart nginx
```

## Production Deployment

### AWS (Elastic Beanstalk)

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
eb init -p docker fennec-api
```

3. Create environment:
```bash
eb create fennec-prod
```

4. Deploy:
```bash
eb deploy
```

5. Open application:
```bash
eb open
```

### AWS (ECS)

1. Build and push image:
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t fennec-api .
docker tag fennec-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/fennec-api:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/fennec-api:latest
```

2. Create ECS task definition

3. Create ECS service

4. Configure load balancer

### Google Cloud (Cloud Run)

1. Build and push:
```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT-ID/fennec-api

# Deploy
gcloud run deploy fennec-api \
  --image gcr.io/PROJECT-ID/fennec-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku

1. Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
# Login
heroku login

# Create app
heroku create fennec-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Open
heroku open
```

### DigitalOcean (App Platform)

1. Create `app.yaml`:
```yaml
name: fennec-api
services:
- name: api
  github:
    repo: your-username/fennec-api
    branch: main
  dockerfile_path: Dockerfile
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
databases:
- name: fennec-db
  engine: PG
  version: "15"
```

2. Deploy via CLI or web interface

### Kubernetes

1. Create deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fennec-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fennec-api
  template:
    metadata:
      labels:
        app: fennec-api
    spec:
      containers:
      - name: api
        image: fennec-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: fennec-secrets
              key: secret-key
```

2. Create service:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fennec-api
spec:
  selector:
    app: fennec-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

3. Apply:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## Performance Optimization

### 1. Use Gunicorn with Uvicorn Workers

```bash
# Install
pip install gunicorn

# Run
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

Update Dockerfile CMD:
```dockerfile
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 2. Enable Caching

```python
from fennec import Application
import redis

app = Application()
cache = redis.Redis.from_url(os.getenv("REDIS_URL"))

@app.middleware("http")
async def cache_middleware(request, call_next):
    # Check cache
    cached = cache.get(request.path)
    if cached:
        return Response(cached)
    
    # Process request
    response = await call_next(request)
    
    # Cache response
    cache.setex(request.path, 300, response.body)
    
    return response
```

### 3. Database Connection Pooling

Already configured in PostgreSQL example with asyncpg.

### 4. Horizontal Scaling

```bash
# Scale with Docker Compose
docker-compose up -d --scale api=5

# Scale with Kubernetes
kubectl scale deployment fennec-api --replicas=5
```

## Monitoring and Logging

### 1. Application Logs

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### 2. Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    REQUEST_COUNT.inc()
    
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 3. Health Checks

```python
@app.get("/health")
async def health_check():
    # Check database
    try:
        await db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Check Redis
    try:
        redis.ping()
        cache_status = "healthy"
    except:
        cache_status = "unhealthy"
    
    overall = "healthy" if all([
        db_status == "healthy",
        cache_status == "healthy"
    ]) else "unhealthy"
    
    return JSONResponse(data={
        "status": overall,
        "database": db_status,
        "cache": cache_status
    })
```

## Security Best Practices

1. **Use HTTPS**: Always use SSL/TLS in production
2. **Environment Variables**: Never commit secrets
3. **Non-root User**: Run containers as non-root
4. **Security Headers**: Use SecurityHeadersMiddleware
5. **Rate Limiting**: Prevent abuse
6. **Input Validation**: Validate all inputs
7. **SQL Injection**: Use parameterized queries
8. **CORS**: Configure allowed origins
9. **Secrets Management**: Use AWS Secrets Manager, HashiCorp Vault
10. **Regular Updates**: Keep dependencies updated

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs fennec-api

# Check if port is in use
lsof -i :8000

# Inspect container
docker inspect fennec-api
```

### Database Connection Issues

```bash
# Test database connection
docker-compose exec api python -c "import asyncpg; print('OK')"

# Check database logs
docker-compose logs postgres

# Verify network
docker network inspect deployment_fennec-network
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Limit memory
docker run -m 512m fennec-api

# In docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
```

## CI/CD Pipeline

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build image
        run: docker build -t fennec-api .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push fennec-api
      
      - name: Deploy
        run: |
          # Deploy to your platform
```

## Learn More

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Fennec Documentation](https://github.com/your-repo/fennec)
