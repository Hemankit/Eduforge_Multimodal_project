#!/bin/bash
# EduForge Docker - Local Testing Script
# Run this script to build and test Docker container locally before deploying to HF Spaces

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}=============================================${NC}"
echo -e "${CYAN}  EduForge Docker - Local Testing${NC}"
echo -e "${CYAN}=============================================${NC}"
echo ""

# Check if Docker is installed
echo -e "${YELLOW}Checking Docker installation...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ Docker found: ${DOCKER_VERSION}${NC}"
else
    echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
    echo -e "${YELLOW}  Visit: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if .env file exists
echo ""
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file found${NC}"
else
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}  Creating from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file from .env.example${NC}"
        echo -e "${YELLOW}  ⚠ Please edit .env and add your API keys!${NC}"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Exiting. Please configure .env first.${NC}"
            exit 0
        fi
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
fi

# Menu
echo ""
echo -e "${CYAN}What would you like to do?${NC}"
echo "  1) Build and run Docker container"
echo "  2) Run existing container (if already built)"
echo "  3) Build only (don't run)"
echo "  4) Run tests (container must be running)"
echo "  5) Stop and remove container"
echo "  6) Use Docker Compose (recommended)"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Building Docker image...${NC}"
        docker build -t eduforge:latest .
        
        echo ""
        echo -e "${YELLOW}Starting container...${NC}"
        docker run -d \
            --name eduforge-test \
            -p 8000:7860 \
            --env-file .env \
            -v "$(pwd)/generated_outputs:/app/generated_outputs" \
            eduforge:latest
        
        echo -e "${GREEN}✓ Container started successfully!${NC}"
        echo ""
        echo -e "${YELLOW}Waiting for container to be ready...${NC}"
        sleep 10
        
        echo ""
        echo -e "${GREEN}Container is running! You can now:${NC}"
        echo "  - View logs: docker logs -f eduforge-test"
        echo "  - Test API: http://localhost:8000/docs"
        echo "  - Run tests: python test_docker_deployment.py"
        echo "  - Stop container: docker stop eduforge-test"
        
        echo ""
        read -p "View container logs? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker logs -f eduforge-test
        fi
        ;;
    
    2)
        echo ""
        echo -e "${YELLOW}Starting container...${NC}"
        docker start eduforge-test
        
        echo -e "${GREEN}✓ Container started!${NC}"
        sleep 5
        docker logs --tail 50 eduforge-test
        ;;
    
    3)
        echo ""
        echo -e "${YELLOW}Building Docker image...${NC}"
        docker build -t eduforge:latest .
        
        echo -e "${GREEN}✓ Build successful!${NC}"
        echo "  Image: eduforge:latest"
        echo "  To run: docker run -d --name eduforge-test -p 8000:7860 --env-file .env eduforge:latest"
        ;;
    
    4)
        echo ""
        echo -e "${YELLOW}Running tests...${NC}"
        echo ""
        python3 test_docker_deployment.py
        ;;
    
    5)
        echo ""
        echo -e "${YELLOW}Stopping and removing container...${NC}"
        docker stop eduforge-test || true
        docker rm eduforge-test || true
        echo -e "${GREEN}✓ Container stopped and removed${NC}"
        ;;
    
    6)
        echo ""
        echo -e "${YELLOW}Using Docker Compose (recommended for testing)...${NC}"
        echo ""
        echo -e "${YELLOW}Starting services with Docker Compose...${NC}"
        docker-compose up -d
        
        echo ""
        echo -e "${GREEN}✓ Services started!${NC}"
        echo ""
        echo -e "${YELLOW}Waiting for container to be ready...${NC}"
        sleep 10
        
        echo ""
        echo -e "${GREEN}Services running! You can now:${NC}"
        echo "  - View logs: docker-compose logs -f"
        echo "  - Test API: http://localhost:8000/docs"
        echo "  - Run tests: python3 test_docker_deployment.py"
        echo "  - Stop services: docker-compose down"
        
        echo ""
        read -p "View container logs? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose logs -f
        fi
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}=============================================${NC}"
echo -e "${CYAN}  Done!${NC}"
echo -e "${CYAN}=============================================${NC}"
echo ""
