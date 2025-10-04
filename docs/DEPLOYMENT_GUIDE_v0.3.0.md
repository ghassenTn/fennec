# Fennec v0.3.0 Deployment Guide

Complete guide for deploying Fennec v0.3.0 applications to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Deployments](#cloud-deployments)
5. [Monitoring Setup](#monitoring-setup)
6. [Production Checklist](#production-checklist)

---

## Prerequisites

### Required Services

- **PostgreSQL**: Database
- **Redis**: Caching and queue backend
- **RabbitMQ**: Message queue (optional, can use Redis)
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

### Environment Variables

```bash
# Application
DEBUG=false
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Cache & Queues
REDIS_URL=redis://host:6379/0
RABBITMQ_URL=amqp://user:password@host:5672/

# Features
ENABLE_ADMIN=true
ENABLE_CACHE=true
ENABLE_MONITORING=true
ENABLE_QUEUES=true
```

---

## Docker Deployment

### 1. Build Image

```bash
cd examples/deployment
docker build -t fennec-api:latest .
```

### 2. Run with Docker Compose

```bash
docker-compose up -d
```

This starts:
- Fennec API (port 8000)
- Queue Worker
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (ports 5672, 15672)
- Prometheus (port 9090)
- Grafana (port 3000)
- Nginx (ports 80, 443)

### 3. Access Services

- **API**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **RabbitMQ Management**: http://localhost:15672
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### 4. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

### 5. Scale Services

```bash
# Scale API instances
docker-compose up -d --scale api=3

# Scale workers
docker-compose up -d --scale worker=5
```

---

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace fennec
```

### 2. Apply Secrets

```bash
# Edit secrets first!
kubectl apply -f kubernetes/secrets.yaml -n fennec
```

### 3. Apply ConfigMap

```bash
kubectl apply -f kubernetes/configmap.yaml -n fennec
```

### 4. Deploy Application

```bash
kubectl apply -f kubernetes/deployment.yaml -n fennec
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n fennec

# Check services
kubectl get svc -n fennec

# Check logs
kubectl logs -f deployment/fennec-api -n fennec
```

### 6. Access Application

```bash
# Port forward for testing
kubectl port-forward svc/fennec-api 8000:8000 -n fennec

# Or use ingress
kubectl get ingress -n fennec
```

### 7. Scale Deployment

```bash
# Scale API
kubectl scale deployment fennec-api --replicas=5 -n fennec

# Scale workers
kubectl scale deployment fennec-worker --replicas=10 -n fennec
```

### 8. Rolling Update

```bash
# Update image
kubectl set image deployment/fennec-api api=fennec-api:v0.3.1 -n fennec

# Check rollout status
kubectl rollout status deployment/fennec-api -n fennec

# Rollback if needed
kubectl rollout undo deployment/fennec-api -n fennec
```

---

## Cloud Deployments

### AWS

#### Using ECS

```bash
# Create ECR repository
aws ecr create-repository --repository-name fennec-api

# Build and push image
docker build -t fennec-api .
docker tag fennec-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/fennec-api:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/fennec-api:latest

# Create ECS cluster
aws ecs create-cluster --cluster-name fennec-cluster

# Create task definition and service
aws ecs create-service --cluster fennec-cluster --service-name fennec-api ...
```

#### Using EKS

```bash
# Create EKS cluster
eksctl create cluster --name fennec-cluster --region us-east-1

# Deploy application
kubectl apply -f kubernetes/ -n fennec
```

#### Managed Services

- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis
- **Queue**: Amazon SQS or Amazon MQ (RabbitMQ)
- **Monitoring**: CloudWatch
- **Load Balancer**: ALB

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/fennec-api

# Deploy to Cloud Run
gcloud run deploy fennec-api \
  --image gcr.io/PROJECT_ID/fennec-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Using GKE

```bash
# Create GKE cluster
gcloud container clusters create fennec-cluster --num-nodes=3

# Deploy application
kubectl apply -f kubernetes/ -n fennec
```

#### Managed Services

- **Database**: Cloud SQL PostgreSQL
- **Cache**: Memorystore Redis
- **Queue**: Cloud Pub/Sub
- **Monitoring**: Cloud Monitoring
- **Load Balancer**: Cloud Load Balancing

### Azure

#### Using Container Instances

```bash
# Create resource group
az group create --name fennec-rg --location eastus

# Create container
az container create \
  --resource-group fennec-rg \
  --name fennec-api \
  --image fennec-api:latest \
  --ports 8000
```

#### Using AKS

```bash
# Create AKS cluster
az aks create --resource-group fennec-rg --name fennec-cluster --node-count 3

# Deploy application
kubectl apply -f kubernetes/ -n fennec
```

#### Managed Services

- **Database**: Azure Database for PostgreSQL
- **Cache**: Azure Cache for Redis
- **Queue**: Azure Service Bus
- **Monitoring**: Azure Monitor
- **Load Balancer**: Azure Load Balancer

---

## Monitoring Setup

### Prometheus

1. **Configure scrape targets** in `prometheus.yml`
2. **Access Prometheus UI**: http://localhost:9090
3. **Query metrics**: `http_requests_total`, `http_request_duration_seconds`

### Grafana

1. **Access Grafana**: http://localhost:3000 (admin/admin)
2. **Add Prometheus datasource** (auto-configured)
3. **Import dashboard** from `grafana/dashboards/`
4. **Create alerts** for critical metrics

### Key Metrics to Monitor

- **Request Rate**: `rate(http_requests_total[5m])`
- **Error Rate**: `rate(http_errors_total[5m])`
- **Response Time (p95)**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Cache Hit Rate**: `rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))`
- **Queue Depth**: `queue_depth`
- **Active Connections**: `http_requests_active`

### Alerts

Create alerts for:
- High error rate (>5%)
- Slow response times (p95 >1s)
- Low cache hit rate (<70%)
- High queue depth (>1000)
- Service down

---

## Production Checklist

### Security

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Use security headers middleware
- [ ] Enable CSRF protection
- [ ] Sanitize user inputs
- [ ] Use environment variables for secrets
- [ ] Restrict admin dashboard access

### Performance

- [ ] Enable Redis caching
- [ ] Configure connection pooling
- [ ] Set appropriate cache TTLs
- [ ] Use CDN for static assets
- [ ] Enable gzip compression
- [ ] Optimize database queries
- [ ] Add database indexes
- [ ] Configure worker concurrency

### Reliability

- [ ] Set up health checks
- [ ] Configure auto-scaling
- [ ] Enable graceful shutdown
- [ ] Implement circuit breakers
- [ ] Set up database backups
- [ ] Configure retry logic
- [ ] Use dead letter queues
- [ ] Test disaster recovery

### Monitoring

- [ ] Set up Prometheus metrics
- [ ] Configure Grafana dashboards
- [ ] Enable structured logging
- [ ] Set up log aggregation
- [ ] Configure alerts
- [ ] Monitor queue depths
- [ ] Track cache hit rates
- [ ] Monitor database performance

### Operations

- [ ] Document deployment process
- [ ] Set up CI/CD pipeline
- [ ] Configure log rotation
- [ ] Plan backup strategy
- [ ] Test rollback procedure
- [ ] Set up monitoring alerts
- [ ] Create runbooks
- [ ] Schedule maintenance windows

---

## Troubleshooting

### High Memory Usage

```bash
# Check container memory
docker stats

# Increase memory limits
docker-compose up -d --scale api=2
```

### Database Connection Issues

```bash
# Check database connectivity
docker-compose exec api python -c "import asyncpg; print('OK')"

# Check connection pool
# Monitor active_connections metric
```

### Queue Backlog

```bash
# Check queue depth
curl http://localhost:8000/queues/status

# Scale workers
docker-compose up -d --scale worker=10
```

### Cache Issues

```bash
# Check Redis connectivity
docker-compose exec redis redis-cli ping

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-repo/fennec
- Documentation: https://fennec-docs.example.com
- Community: https://discord.gg/fennec
