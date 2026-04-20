# EduForge Docker - Local Testing Script
# Run this script to build and test Docker container locally before deploying

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  EduForge Docker - Local Testing" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "  Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
Write-Host ""
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
    Write-Host "  Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file from .env.example" -ForegroundColor Green
        Write-Host "  ⚠ Please edit .env and add your API keys!" -ForegroundColor Yellow
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y") {
            Write-Host "Exiting. Please configure .env first." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "✗ .env.example not found" -ForegroundColor Red
        exit 1
    }
}

# Ask user what to do
Write-Host ""
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host "  1) Build and run Docker container" -ForegroundColor White
Write-Host "  2) Run existing container (if already built)" -ForegroundColor White
Write-Host "  3) Build only (don't run)" -ForegroundColor White
Write-Host "  4) Run tests (container must be running)" -ForegroundColor White
Write-Host "  5) Stop and remove container" -ForegroundColor White
Write-Host "  6) Use Docker Compose (recommended)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Building Docker image..." -ForegroundColor Yellow
        docker build -t eduforge:latest .
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Build successful!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Starting container..." -ForegroundColor Yellow
            docker run -d `
                --name eduforge-test `
                -p 8000:7860 `
                --env-file .env `
                -v ${PWD}/generated_outputs:/app/generated_outputs `
                eduforge:latest
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Container started successfully!" -ForegroundColor Green
                Write-Host ""
                Write-Host "Waiting for container to be ready..." -ForegroundColor Yellow
                Start-Sleep -Seconds 10
                
                Write-Host ""
                Write-Host "Container is running! You can now:" -ForegroundColor Green
                Write-Host "  - View logs: docker logs -f eduforge-test" -ForegroundColor White
                Write-Host "  - Test API: http://localhost:8000/docs" -ForegroundColor White
                Write-Host "  - Run tests: python test_docker_deployment.py" -ForegroundColor White
                Write-Host "  - Stop container: docker stop eduforge-test" -ForegroundColor White
                
                # Ask if user wants to see logs
                Write-Host ""
                $showLogs = Read-Host "View container logs? (y/n)"
                if ($showLogs -eq "y") {
                    docker logs -f eduforge-test
                }
            } else {
                Write-Host "✗ Failed to start container" -ForegroundColor Red
            }
        } else {
            Write-Host "✗ Build failed. Check errors above." -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Starting container..." -ForegroundColor Yellow
        docker start eduforge-test
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Container started!" -ForegroundColor Green
            Start-Sleep -Seconds 5
            docker logs --tail 50 eduforge-test
        } else {
            Write-Host "✗ Failed to start container. It may not exist yet." -ForegroundColor Red
            Write-Host "  Try option 1 to build and run first." -ForegroundColor Yellow
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Building Docker image..." -ForegroundColor Yellow
        docker build -t eduforge:latest .
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Build successful!" -ForegroundColor Green
            Write-Host "  Image: eduforge:latest" -ForegroundColor White
            Write-Host "  To run: docker run -d --name eduforge-test -p 8000:7860 --env-file .env eduforge:latest" -ForegroundColor White
        } else {
            Write-Host "✗ Build failed" -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "Running tests..." -ForegroundColor Yellow
        Write-Host ""
        python test_docker_deployment.py
    }
    
    "5" {
        Write-Host ""
        Write-Host "Stopping and removing container..." -ForegroundColor Yellow
        docker stop eduforge-test
        docker rm eduforge-test
        Write-Host "✓ Container stopped and removed" -ForegroundColor Green
    }
    
    "6" {
        Write-Host ""
        Write-Host "Using Docker Compose (recommended for testing)..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Starting services with Docker Compose..." -ForegroundColor Yellow
        docker-compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Services started!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Waiting for container to be ready..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
            
            Write-Host ""
            Write-Host "Services running! You can now:" -ForegroundColor Green
            Write-Host "  - View logs: docker-compose logs -f" -ForegroundColor White
            Write-Host "  - Test API: http://localhost:8000/docs" -ForegroundColor White
            Write-Host "  - Run tests: python test_docker_deployment.py" -ForegroundColor White
            Write-Host "  - Stop services: docker-compose down" -ForegroundColor White
            
            Write-Host ""
            $showLogs = Read-Host "View container logs? (y/n)"
            if ($showLogs -eq "y") {
                docker-compose logs -f
            }
        } else {
            Write-Host "✗ Failed to start services" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Done!" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
