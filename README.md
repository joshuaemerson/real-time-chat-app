# Real-Time Chat Application

A scalable real-time chat application built with Flask-SocketIO, Redis, Docker, and Kubernetes.

## Architecture

- **Flask-SocketIO**: WebSocket server for real-time communication
- **Redis**: Message broker for pub/sub across multiple server instances
- **Docker**: Containerization
- **Kubernetes**: Orchestration with horizontal scaling

## Features

- ✅ Real-time messaging with WebSockets
- ✅ Multiple chat rooms
- ✅ Typing indicators
- ✅ User join/leave notifications
- ✅ Horizontal scaling (multiple server replicas)
- ✅ Session affinity for WebSocket connections
- ✅ Health checks and auto-healing
- ✅ Auto-scaling based on CPU/memory usage

## Project Structure

```
chat-app/
├── app.py                      # Flask-SocketIO application
├── templates/
│   └── index.html              # Chat UI
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── kubernetes-manifests.yaml   # K8s resources
└── README.md                   # This file
```

## Local Development

### Prerequisites
- Python 3.11+
- Redis

### Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start Redis**:
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

3. **Run the application**:
```bash
python app/app.py
```

4. **Open in browser**: http://localhost:5000

## Docker Deployment

### Build the image

```bash
docker build -t chat-app:latest .
```

### Run with Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  chat-app:
    image: chat-app:latest
    ports:
      - "5000:5000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - SECRET_KEY=your-secret-key
    depends_on:
      - redis
```

```bash
docker-compose up
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (minikube)
- kubectl configured

### Deploy to Kubernetes

1. **Apply all manifests**:
```bash
kubectl apply -f k8s/kubernetes-manifests.yaml
```

2. **Check deployment status**:
```bash
kubectl get pods -n chat-app
kubectl get services -n chat-app
```

3. **Get service URL**:

For **Minikube**:
```bash
minikube service chat-app -n chat-app
```

### View logs

```bash
# All pods
kubectl logs -l app=chat-app -n chat-app --tail=50 -f

# Specific pod
kubectl logs <pod-name> -n chat-app -f
```

### Monitor auto-scaling

```bash
kubectl get hpa -n chat-app -w
```

## Testing the Chat

1. Open the application in multiple browser tabs or windows
2. Enter different usernames in each
3. Send messages and see them appear in real-time across all clients
4. Try different rooms to see message isolation
5. Watch typing indicators when someone is typing

## Configuration

### Environment Variables

- `REDIS_HOST`: Redis server hostname (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `SECRET_KEY`: Flask secret key for sessions
- `PORT`: Application port (default: 5000)

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n chat-app
```

## Clean Up

```bash
kubectl delete namespace chat-app
```
