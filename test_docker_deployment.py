#!/usr/bin/env python3
"""
Test script for local Docker deployment verification.
Run this after building the Docker image to verify everything works.
"""
import requests
import time
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if using different port
TIMEOUT = 30

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_health() -> bool:
    """Test the /health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            if data.get('provider'):
                print(f"   Provider: {data.get('provider')}")
                print(f"   Model: {data.get('model')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_generate() -> bool:
    """Test the /generate endpoint with a simple request."""
    print("Testing content generation...")
    
    payload = {
        "topic": "Binary Search",
        "audience": "beginner",
        "max_duration_sec": 120,
        "render_formats": ["slides"],
        "include_few_shot": False
    }
    
    try:
        print(f"Sending request with topic: '{payload['topic']}'")
        print("⏳ This may take 30-60 seconds for first request...")
        
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            timeout=120  # Allow up to 2 minutes for generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Content generation successful!")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            if data.get('generation_time_sec'):
                print(f"   Generation time: {data.get('generation_time_sec'):.2f}s")
            if data.get('generated_files'):
                print(f"   Files generated: {len(data.get('generated_files'))}")
                for file_type, path in data.get('generated_files', {}).items():
                    print(f"     - {file_type}: {path}")
            return True
        else:
            print(f"❌ Generation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Generation request timed out (>120s)")
        print("   This might indicate the model needs more time or there's an issue")
        return False
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

def test_sessions() -> bool:
    """Test the /sessions endpoint."""
    print("Testing sessions endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/sessions", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            print(f"✅ Sessions endpoint working!")
            print(f"   Total sessions: {len(sessions)}")
            if sessions:
                latest = sessions[-1]
                print(f"   Latest session: {latest.get('session_id')}")
                print(f"   Files: {latest.get('file_count')}")
            return True
        else:
            print(f"❌ Sessions check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sessions check error: {e}")
        return False

def test_swagger_ui() -> bool:
    """Test that Swagger UI is accessible."""
    print("Testing API documentation (Swagger UI)...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Swagger UI accessible!")
            print(f"   URL: {BASE_URL}/docs")
            return True
        else:
            print(f"❌ Swagger UI check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Swagger UI check error: {e}")
        return False

def main():
    """Run all tests."""
    print_section("🧪 EduForge Docker Deployment Test")
    
    print(f"Testing deployment at: {BASE_URL}")
    print("Make sure Docker container is running!")
    print("\nTo start the container:")
    print("  docker-compose up (OR)")
    print("  docker build -t eduforge . && docker run -p 8000:7860 eduforge")
    
    # Wait for container to be ready
    print("\n⏳ Waiting for container to be ready (5 seconds)...")
    time.sleep(5)
    
    # Track results
    results = {}
    
    # Run tests
    print_section("Test 1: Health Check")
    results['health'] = test_health()
    
    print_section("Test 2: Swagger UI")
    results['swagger'] = test_swagger_ui()
    
    print_section("Test 3: Sessions List")
    results['sessions'] = test_sessions()
    
    print_section("Test 4: Content Generation (This may take a minute)")
    results['generate'] = test_generate()
    
    # Summary
    print_section("📊 Test Summary")
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper()}: {status}")
    
    print(f"\n{passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your Docker deployment is ready!")
        print("\n📝 Next steps:")
        print("   1. Review the deployment checklist: DEPLOYMENT_CHECKLIST.md")
        print("   2. Follow the deployment guide: HF_DEPLOYMENT_GUIDE.md")
        print("   3. Deploy to your cloud platform")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting tips:")
        print("   - Check Docker container logs: docker-compose logs")
        print("   - Verify environment variables are set correctly")
        print("   - Ensure API keys are valid (if using API providers)")
        print("   - Check that all dependencies installed successfully")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
