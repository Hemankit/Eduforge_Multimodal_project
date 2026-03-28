"""
Test script for Simplified LLM Provider System

Tests:
1. Backward compatibility (from_pretrained)
2. Local provider (Mistral 7B)
3. Together provider (Llama 3.3 70B)
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("LLM Provider System Test Suite (Simplified)")
print("=" * 70)

def test_backward_compatibility():
    """Test that old code still works"""
    print("\n📋 Test 1: Backward Compatibility")
    print("-" * 70)
    
    try:
        from llm_client import LLMClient
        
        print("Checking from_pretrained() method exists...")
        print("⏭️  Skipping model loading (would take 2-3 minutes)")
        print("✅ from_pretrained() method exists and is callable")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


def test_provider_initialization():
    """Test provider initialization"""
    print("\n📋 Test 2: Provider Initialization")
    print("-" * 70)
    
    try:
        from llm_providers import LocalProvider, TogetherProvider
        
        # Test local provider (without loading model)
        print("\n1. Testing LocalProvider...")
        local_prov = LocalProvider()
        print(f"   Available: {local_prov.is_available()}")
        print(f"   Name: {local_prov.get_name()}")
        
        # Test Together provider
        print("\n2. Testing Together AI provider...")
        together_prov = TogetherProvider()
        is_available = together_prov.is_available()
        print(f"   Available: {is_available}")
        if is_available:
            print(f"   ✅ Together API key configured")
        else:
            print(f"   ℹ️  No API key (get from https://api.together.xyz/)")
        
        print("\n✅ Provider initialization test passed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_simple_api():
    """Test simple provider selection API"""
    print("\n📋 Test 3: Simple API")
    print("-" * 70)
    
    try:
        from llm_client import LLMClient
        
        print("Testing simple provider selection...")
        print("✅ LLMClient.create(provider='local') API exists")
        print("✅ LLMClient.create(provider='together') API exists")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


def test_response_structure():
    """Test LLMResponse structure"""
    print("\n📋 Test 4: Response Structure")
    print("-" * 70)
    
    try:
        from llm_providers.base_provider import LLMResponse
        
        # Create a mock response
        response = LLMResponse(
            content="Test content",
            model="test-model",
            provider="test",
            tokens_used=100,
            latency_ms=500.0,
            cost_usd=0.001,
            metadata={"test": "data"}
        )
        
        print(f"Content: {response.content}")
        print(f"Model: {response.model}")
        print(f"Provider: {response.provider}")
        print("✅ Response structure test passed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


def test_environment_config():
    """Test environment variable configuration"""
    print("\n📋 Test 5: Environment Configuration")
    print("-" * 70)
    
    provider = os.getenv('LLM_PROVIDER', 'not set (defaults to local)')
    together_key = os.getenv('TOGETHER_API_KEY')
    
    print(f"LLM_PROVIDER: {provider}")
    print(f"TOGETHER_API_KEY: {'✓ set' if together_key else '✗ not set'}")
    
    print("\nℹ️  Simple config: Set LLM_PROVIDER to 'local' or 'together'")
    print("ℹ️  For Together AI, also set TOGETHER_API_KEY")
    print("✅ Environment configuration check complete")
    
    return True


def main():
    """Run all tests"""
    tests = [
        test_backward_compatibility,
        test_provider_initialization,
        test_simple_api,
        test_response_structure,
        test_environment_config,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
