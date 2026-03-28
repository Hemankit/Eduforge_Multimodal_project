"""
Simple test client for the EduForge API.
Demonstrates how to use the content generation endpoints.
"""
import requests
import json
from pathlib import Path
import time


API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test if the API server is running."""
    print("\n[1/4] Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy")
            print(f"   Model loaded: {data.get('model_loaded')}")
            print(f"   Output dir: {data.get('output_dir')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start with: python main.py")
        return False


def test_generate_content():
    """Test content generation with the API."""
    print("\n[2/4] Testing content generation...")
    
    # Prepare request
    request_data = {
        "topic": "Bubble Sort Algorithm",
        "audience": "beginner",
        "max_duration_sec": 120,
        "example_count": 1,
        "render_formats": ["slides", "diagrams"],
        "optimize_for_format": True,
        "include_few_shot": False
    }
    
    print(f"   Topic: {request_data['topic']}")
    print(f"   Audience: {request_data['audience']}")
    print(f"   Formats: {', '.join(request_data['render_formats'])}")
    print("\n   Generating content (this may take 1-2 minutes)...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=request_data,
            timeout=300  # 5 minute timeout for LLM generation
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content generated in {elapsed_time:.2f}s")
            print(f"   Success: {data['success']}")
            print(f"   Message: {data['message']}")
            
            # Show content details
            if data.get('content_output'):
                content = data['content_output']
                print(f"\n   Content Details:")
                print(f"   - Sections: {len(content.get('sections', []))}")
                print(f"   - Total duration: {content.get('total_duration_sec')}s")
                print(f"   - Learning objectives: {len(content.get('learning_objectives', []))}")
            
            # Show generated files
            if data.get('generated_files'):
                print(f"\n   Generated Files:")
                for file_type, file_path in data['generated_files'].items():
                    if isinstance(file_path, list):
                        print(f"   - {file_type}: {len(file_path)} files")
                        for fp in file_path:
                            print(f"      {API_BASE_URL}{fp}")
                    else:
                        print(f"   - {file_type}: {API_BASE_URL}{file_path}")
            
            # Show validation warnings
            if data.get('validation_warnings'):
                print(f"\n   ⚠️  Validation Warnings:")
                for warning in data['validation_warnings']:
                    print(f"      - {warning}")
            
            return data
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out (LLM generation taking too long)")
        return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None


def test_list_sessions():
    """Test listing all generation sessions."""
    print("\n[3/4] Testing session listing...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/sessions")
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            print(f"✅ Found {len(sessions)} sessions")
            
            for session in sessions[:5]:  # Show first 5
                print(f"   - {session['session_id']}: {session['file_count']} files")
            
            return sessions
        else:
            print(f"❌ Failed to list sessions: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []


def test_download_file(session_id: str, filename: str):
    """Test downloading a generated file."""
    print(f"\n[4/4] Testing file download...")
    print(f"   Session: {session_id}")
    print(f"   File: {filename}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/outputs/{session_id}/{filename}")
        if response.status_code == 200:
            # Save to local file
            output_path = Path("downloaded_outputs") / filename
            output_path.parent.mkdir(exist_ok=True)
            output_path.write_bytes(response.content)
            
            print(f"✅ File downloaded: {output_path}")
            print(f"   Size: {len(response.content):,} bytes")
            return True
        else:
            print(f"❌ Download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("TESTING EDUFORGE API")
    print("=" * 70)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server is not running. Start it with: python main.py")
        return
    
    # Test 2: Generate content
    result = test_generate_content()
    if not result:
        print("\n⚠️  Content generation failed. Check server logs.")
        return
    
    # Test 3: List sessions
    sessions = test_list_sessions()
    
    # Test 4: Download a file (if we have generated files)
    if result and result.get('generated_files'):
        files = result['generated_files']
        if 'slides' in files:
            # Extract session_id and filename from path
            path_parts = files['slides'].split('/')
            if len(path_parts) >= 3:
                session_id = path_parts[-2]
                filename = path_parts[-1]
                test_download_file(session_id, filename)
    
    print("\n" + "=" * 70)
    print("✅ API TESTING COMPLETED")
    print("=" * 70)
    print("\nNext steps:")
    print("  - View API docs: http://localhost:8000/docs")
    print("  - Try custom requests with Postman/curl")
    print("  - Check generated_outputs/ folder for files")


if __name__ == "__main__":
    main()
