#!/bin/bash

# Production deployment script for Tourist Safety System
# Usage: ./deploy.sh [local|heroku|docker]

set -e

DEPLOYMENT_TYPE=${1:-local}

echo "🚀 Starting Tourist Safety System Deployment"
echo "Deployment type: $DEPLOYMENT_TYPE"

case $DEPLOYMENT_TYPE in
    "local")
        echo "📦 Installing dependencies..."
        cd backend
        pip install -r requirements.txt
        
        echo "🗄️ Setting up database..."
        python -c "from app import init_db; init_db()"
        
        echo "🌟 Starting local server..."
        python app.py
        ;;
        
    "heroku")
        echo "☁️ Deploying to Heroku..."
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not found. Please install it first."
            exit 1
        fi
        
        # Login and create app
        heroku login
        heroku create tourist-safety-system-$(date +%s) || true
        
        # Set environment variables
        heroku config:set FLASK_ENV=production
        heroku config:set SECRET_KEY=$(openssl rand -hex 32)
        
        # Deploy
        git add .
        git commit -m "Deploy to Heroku - $(date)" || true
        git push heroku main
        
        echo "✅ Deployed to Heroku!"
        heroku open
        ;;
        
    "docker")
        echo "🐳 Building Docker container..."
        
        # Build image
        docker build -t tourist-safety-system .
        
        # Stop existing container
        docker stop tourist-safety-system || true
        docker rm tourist-safety-system || true
        
        # Run new container
        docker run -d \
            --name tourist-safety-system \
            -p 5000:5000 \
            -v $(pwd)/data:/app/data \
            -e FLASK_ENV=production \
            -e SECRET_KEY=$(openssl rand -hex 32) \
            tourist-safety-system
        
        echo "✅ Docker container started!"
        echo "🌐 Access at: http://localhost:5000"
        ;;
        
    *)
        echo "❌ Unknown deployment type: $DEPLOYMENT_TYPE"
        echo "Usage: ./deploy.sh [local|heroku|docker]"
        exit 1
        ;;
esac

echo "🎉 Deployment complete!"