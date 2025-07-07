#!/usr/bin/env python3
"""
Simple test script to verify the testing setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import pytest
        print("✅ pytest imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pytest: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import aiohttp: {e}")
        return False
    
    try:
        import jwt
        print("✅ PyJWT imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyJWT: {e}")
        return False
    
    try:
        import bcrypt
        print("✅ bcrypt imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import bcrypt: {e}")
        return False
    
    try:
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastAPI: {e}")
        return False
    
    return True

def test_project_structure():
    """Test that the project structure is correct"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "requirements.txt",
        "test_requirements.txt",
        "pytest.ini",
        "run_tests.py",
        "README_TESTING.md",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_security.py",
        "tests/test_bridge_api_client.py",
        "tests/test_usdc_payment_service.py",
        "tests/test_walletconnect_v2_service.py",
        "tests/test_api_routes.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def test_core_modules():
    """Test that core modules can be imported"""
    print("\n🧩 Testing core modules...")
    
    # Add the current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    try:
        from core.security import SecurityContext, SecurityService
        print("✅ core.security imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core.security: {e}")
        return False
    
    try:
        from core.bridge_api_client import BridgeAPIClient, BridgeTransfer
        print("✅ core.bridge_api_client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core.bridge_api_client: {e}")
        return False
    
    try:
        from core.usdc_payment_service import USDCPaymentService, TransferRequest
        print("✅ core.usdc_payment_service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core.usdc_payment_service: {e}")
        return False
    
    try:
        from core.walletconnect_v2_service import WalletConnectV2Service, WalletConnectSession
        print("✅ core.walletconnect_v2_service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core.walletconnect_v2_service: {e}")
        return False
    
    return True

def test_fastapi_app():
    """Test that the FastAPI app can be imported"""
    print("\n🌐 Testing FastAPI app...")
    
    try:
        from fastapi_app import app
        print("✅ FastAPI app imported successfully")
        
        # Test that app has expected attributes
        assert hasattr(app, 'routes'), "App should have routes"
        print("✅ FastAPI app has expected structure")
        
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        return False
    except AssertionError as e:
        print(f"❌ FastAPI app structure issue: {e}")
        return False
    
    return True

def test_pytest_configuration():
    """Test pytest configuration"""
    print("\n⚙️ Testing pytest configuration...")
    
    try:
        import pytest
        from _pytest.config import Config
        
        # Test that pytest can be configured
        config = Config()
        print("✅ Pytest configuration works")
        
    except Exception as e:
        print(f"❌ Pytest configuration issue: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Python Backend Setup")
    print("=" * 50)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Project Structure", test_project_structure),
        ("Core Modules", test_core_modules),
        ("FastAPI App", test_fastapi_app),
        ("Pytest Configuration", test_pytest_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python run_tests.py")
        print("2. Or run: pytest tests/ -v")
        return 0
    else:
        print("⚠️ Some tests failed. Please fix the issues before running tests.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 