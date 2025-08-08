#!/usr/bin/env python3
"""
Complete VelaFi KYC Flow Test
Tests the entire VelaFi KYC system end-to-end using the test server
"""

import asyncio
import json
import time
from typing import Any, Dict

import requests

# Test server configuration
BASE_URL = "http://localhost:8002"

def test_health_check():
    """Test server health."""
    print("🔍 Testing server health...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Server healthy: {data}")
        return True
    else:
        print(f"  ❌ Server unhealthy: {response.status_code}")
        return False

def test_regional_kyc_routing():
    """Test regional KYC routing logic."""
    print("\n🌍 Testing Regional KYC Routing...")
    
    # Test LATAM country (should use VelaFi)
    response = requests.get(f"{BASE_URL}/kyc/system/MX")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Mexico KYC system: {data['kyc_system']}")
        assert data['kyc_system'] == 'velafi', "Mexico should use VelaFi KYC"
    else:
        print(f"  ❌ Failed to get Mexico KYC system: {response.status_code}")
        return False
    
    # Test US country (should use Bridge)
    response = requests.get(f"{BASE_URL}/kyc/system/US")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ US KYC system: {data['kyc_system']}")
        assert data['kyc_system'] == 'bridge', "US should use Bridge KYC"
    else:
        print(f"  ❌ Failed to get US KYC system: {response.status_code}")
        return False
    
    return True

def test_kyc_requirements():
    """Test KYC requirements for different countries."""
    print("\n📋 Testing KYC Requirements...")
    
    # Test Mexico requirements
    response = requests.get(f"{BASE_URL}/kyc/requirements/MX")
    if response.status_code == 200:
        data = response.json()
        requirements = data['requirements']
        print(f"  ✅ Mexico requirements:")
        print(f"     System: {requirements['system']}")
        print(f"     Required fields: {len(requirements['required_fields'])}")
        print(f"     Required documents: {requirements['required_documents']}")
        print(f"     ID type: {requirements['country_specific']['MX']['id_type']}")
        print(f"     Tax ID: {requirements['country_specific']['MX']['tax_id']}")
    else:
        print(f"  ❌ Failed to get Mexico requirements: {response.status_code}")
        return False
    
    return True

def test_supported_countries():
    """Test supported countries list."""
    print("\n🌐 Testing Supported Countries...")
    
    response = requests.get(f"{BASE_URL}/kyc/supported-countries")
    if response.status_code == 200:
        data = response.json()
        countries = data['countries']
        bridge_count = len(countries['bridge_regions'])
        velafi_count = len(countries['velafi_regions'])
        print(f"  ✅ Bridge regions: {bridge_count}")
        print(f"  ✅ VelaFi regions: {velafi_count}")
        print(f"  ✅ Total supported countries: {bridge_count + velafi_count}")
    else:
        print(f"  ❌ Failed to get supported countries: {response.status_code}")
        return False
    
    return True

def test_customer_creation():
    """Test VelaFi customer creation."""
    print("\n👤 Testing Customer Creation...")
    
    customer_data = {
        "first_name": "María",
        "last_name": "García",
        "email": "maria.garcia@test.com",
        "date_of_birth": "1985-06-20",
        "country": "MX",
        "phone": "+525598765432",
        "address": "Calle Juárez 456",
        "city": "Guadalajara",
        "state": "Jalisco",
        "postal_code": "44100"
    }
    
    response = requests.post(
        f"{BASE_URL}/velafi/kyc/customer",
        json=customer_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        customer = data['customer']
        print(f"  ✅ Customer created:")
        print(f"     Name: {customer['first_name']} {customer['last_name']}")
        print(f"     Email: {customer['email']}")
        print(f"     VelaFi ID: {customer['velafi_customer_id']}")
        print(f"     KYC Status: {customer['kyc_status']}")
        return customer['velafi_customer_id']
    else:
        print(f"  ❌ Failed to create customer: {response.status_code}")
        return None

def test_document_upload():
    """Test document upload for KYC."""
    print("\n📄 Testing Document Upload...")
    
    # Test passport upload
    passport_data = {
        "document_type": "passport",
        "filename": "passport.pdf",
        "mime_type": "application/pdf",
        "file_size": 1024000
    }
    
    response = requests.post(
        f"{BASE_URL}/velafi/kyc/documents",
        json=passport_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        document = data['document']
        print(f"  ✅ Passport uploaded:")
        print(f"     Document ID: {document['id']}")
        print(f"     VelaFi Doc ID: {document['velafi_document_id']}")
        print(f"     Status: {document['status']}")
    else:
        print(f"  ❌ Failed to upload passport: {response.status_code}")
        return False
    
    # Test utility bill upload
    bill_data = {
        "document_type": "utility_bill",
        "filename": "electricity_bill.pdf",
        "mime_type": "application/pdf",
        "file_size": 512000
    }
    
    response = requests.post(
        f"{BASE_URL}/velafi/kyc/documents",
        json=bill_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        document = data['document']
        print(f"  ✅ Utility bill uploaded:")
        print(f"     Document ID: {document['id']}")
        print(f"     VelaFi Doc ID: {document['velafi_document_id']}")
        print(f"     Status: {document['status']}")
    else:
        print(f"  ❌ Failed to upload utility bill: {response.status_code}")
        return False
    
    return True

def test_kyc_status():
    """Test KYC status checking."""
    print("\n📊 Testing KYC Status...")
    
    response = requests.get(f"{BASE_URL}/velafi/kyc/approved")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ KYC Status:")
        print(f"     Approved: {data['kyc_approved']}")
        print(f"     Status: {data['kyc_status']}")
        print(f"     Message: {data['message']}")
    else:
        print(f"  ❌ Failed to get KYC status: {response.status_code}")
        return False
    
    return True

# ---------------------------------------------------------------------------
# New Phase-2/3 tests – Payment Method & On-Ramp Orders
# ---------------------------------------------------------------------------


def test_payment_method_and_order():
    """Full flow: create PM → create order → wait for settlement → fetch order."""

    print("\n💳 Testing Payment Method + On-Ramp Order flow…")

    # 1. Create payment method
    resp = requests.post(
        f"{BASE_URL}/velafi/payment_method",
        json={"plaid_token": "public-sandbox-abc123"},
        timeout=5,
    )
    assert resp.status_code == 201, f"create PM failed: {resp.text}"
    pm = resp.json()
    pm_id = pm["id"]
    print(f"  ✅ Payment method created: {pm_id}")

    # 2. Create order
    resp = requests.post(
        f"{BASE_URL}/velafi/order",
        json={"payment_method_id": pm_id, "fiat_amount": 100.25},
        timeout=5,
    )
    assert resp.status_code == 201, f"create order failed: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    print(f"  ⏳ Order placed: {order_id} – status={order['status']}")

    # 3. Poll until completed (the test server settles after ~0.2 s)
    for _ in range(10):
        time.sleep(0.1)
        r = requests.get(f"{BASE_URL}/velafi/order/{order_id}")
        if r.status_code == 200 and r.json()["status"] == "completed":
            final = r.json()
            print(f"  ✅ Order settled! usdc_amount={final.get('usdc_amount')}")
            break
    else:
        raise AssertionError("order never settled in time")

    return True

def test_velafi_api_connection():
    """Test VelaFi API connection."""
    print("\n🔗 Testing VelaFi API Connection...")
    
    # Test account endpoint
    response = requests.get(f"{BASE_URL}/velafi/test/account")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Account test: {data['message']}")
    else:
        print(f"  ❌ Account test failed: {response.status_code}")
        return False
    
    # Test countries endpoint
    response = requests.get(f"{BASE_URL}/velafi/test/countries")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Countries test: {data['message']}")
        print(f"     Countries found: {data['countries_count']}")
    else:
        print(f"  ❌ Countries test failed: {response.status_code}")
        return False
    
    # Test quote endpoint
    response = requests.post(f"{BASE_URL}/velafi/test/quote")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Quote test: {data['message']}")
    else:
        print(f"  ❌ Quote test failed: {response.status_code}")
        return False
    
    return True

def test_complete_flow():
    """Test the complete VelaFi KYC flow."""
    print("\n🔄 Testing Complete VelaFi KYC Flow...")
    
    # Step 1: Determine KYC system
    print("  1️⃣ Determining KYC system for Mexico...")
    response = requests.get(f"{BASE_URL}/kyc/system/MX")
    if response.status_code != 200:
        print("     ❌ Failed to determine KYC system")
        return False
    kyc_system = response.json()['kyc_system']
    print(f"     ✅ KYC system: {kyc_system}")
    
    # Step 2: Get KYC requirements
    print("  2️⃣ Getting KYC requirements...")
    response = requests.get(f"{BASE_URL}/kyc/requirements/MX")
    if response.status_code != 200:
        print("     ❌ Failed to get KYC requirements")
        return False
    requirements = response.json()['requirements']
    print(f"     ✅ Requirements: {requirements['description']}")
    
    # Step 3: Create customer
    print("  3️⃣ Creating customer...")
    customer_data = {
        "first_name": "Carlos",
        "last_name": "Rodríguez",
        "email": "carlos.rodriguez@test.com",
        "date_of_birth": "1988-03-15",
        "country": "MX",
        "phone": "+525512345678"
    }
    response = requests.post(f"{BASE_URL}/velafi/kyc/customer", json=customer_data)
    if response.status_code != 200:
        print("     ❌ Failed to create customer")
        return False
    customer = response.json()['customer']
    print(f"     ✅ Customer created: {customer['first_name']} {customer['last_name']}")
    
    # Step 4: Upload documents
    print("  4️⃣ Uploading documents...")
    documents = [
        {"document_type": "passport", "filename": "passport.pdf", "mime_type": "application/pdf", "file_size": 1024000},
        {"document_type": "utility_bill", "filename": "bill.pdf", "mime_type": "application/pdf", "file_size": 512000}
    ]
    
    for doc in documents:
        response = requests.post(f"{BASE_URL}/velafi/kyc/documents", json=doc)
        if response.status_code != 200:
            print(f"     ❌ Failed to upload {doc['document_type']}")
            return False
        document = response.json()['document']
        print(f"     ✅ {doc['document_type']} uploaded: {document['id']}")
    
    # Step 5: Check KYC status
    print("  5️⃣ Checking KYC status...")
    response = requests.get(f"{BASE_URL}/velafi/kyc/approved")
    if response.status_code != 200:
        print("     ❌ Failed to check KYC status")
        return False
    status = response.json()
    print(f"     ✅ KYC status: {status['kyc_status']}")
    
    print("  🎉 Complete flow test passed!")
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Complete VelaFi KYC Flow Tests")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Regional KYC Routing", test_regional_kyc_routing),
        ("KYC Requirements", test_kyc_requirements),
        ("Supported Countries", test_supported_countries),
        ("Customer Creation", test_customer_creation),
        ("Document Upload", test_document_upload),
        ("KYC Status", test_kyc_status),
        ("Payment Method & On-Ramp Order", test_payment_method_and_order),
        ("VelaFi API Connection", test_velafi_api_connection),
        ("Complete Flow", test_complete_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
            if not result:
                print(f"❌ {test_name} failed")
            else:
                print(f"✅ {test_name} passed")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VelaFi KYC system is working perfectly.")
        print("🚀 Ready for production deployment!")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 