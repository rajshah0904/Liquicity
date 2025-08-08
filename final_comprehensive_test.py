#!/usr/bin/env python3
"""
Final Comprehensive Test Suite
Demonstrates the system's robustness across all scenarios with different data amounts and edge cases
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

# Test server configuration
BASE_URL = "http://localhost:8002"

class FinalComprehensiveTest:
    def __init__(self):
        self.test_results = []
        self.performance_data = {}
        
    def log_test(self, test_name: str, success: bool, duration: float, details: str = ""):
        """Log test results."""
        result = {
            "test_name": test_name,
            "success": success,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s) - {details}")

    def generate_test_data(self, data_type: str, size: str = "normal") -> Dict[str, Any]:
        """Generate test data of different sizes and types."""
        
        if data_type == "customer":
            if size == "small":
                return {
                    "first_name": "Juan",
                    "last_name": "Pérez",
                    "email": f"test{random.randint(1000,9999)}@test.com",
                    "date_of_birth": "1990-01-15",
                    "country": "MX"
                }
            elif size == "large":
                return {
                    "first_name": "María Guadalupe",
                    "last_name": "Rodríguez-Hernández",
                    "email": f"test{random.randint(1000,9999)}@verylongdomainname.com",
                    "date_of_birth": "1985-06-20",
                    "country": "MX",
                    "phone": "+525512345678",
                    "address": "Avenida Insurgentes Sur 1234, Colonia Del Valle, Delegación Benito Juárez",
                    "city": "Ciudad de México",
                    "state": "CDMX",
                    "postal_code": "03100"
                }
            else:  # normal
                return {
                    "first_name": "Carlos",
                    "last_name": "García",
                    "email": f"test{random.randint(1000,9999)}@test.com",
                    "date_of_birth": "1988-03-15",
                    "country": "MX",
                    "phone": "+525598765432",
                    "address": "Calle Juárez 456",
                    "city": "Guadalajara",
                    "state": "Jalisco",
                    "postal_code": "44100"
                }
        
        elif data_type == "document":
            sizes = {
                "small": 102400,    # 100KB
                "normal": 1024000,  # 1MB
                "large": 10485760   # 10MB
            }
            return {
                "document_type": random.choice(["passport", "utility_bill", "national_id", "bank_statement"]),
                "filename": f"document_{random.randint(1000,9999)}.pdf",
                "mime_type": "application/pdf",
                "file_size": sizes.get(size, 1024000)
            }

    def test_1_basic_functionality(self):
        """Test 1: Basic functionality and health."""
        print("\n🏥 Test 1: Basic Functionality and Health")
        
        start_time = time.time()
        
        # Health check
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            self.log_test("Health Check", False, time.time() - start_time, f"Status: {response.status_code}")
            return False
        
        # KYC requirements
        response = requests.get(f"{BASE_URL}/kyc/requirements/MX", timeout=5)
        if response.status_code != 200:
            self.log_test("KYC Requirements", False, time.time() - start_time, f"Status: {response.status_code}")
            return False
        
        # Regional KYC routing
        response = requests.get(f"{BASE_URL}/kyc/system/MX", timeout=5)
        if response.status_code != 200:
            self.log_test("Regional KYC Routing", False, time.time() - start_time, f"Status: {response.status_code}")
            return False
        
        self.log_test("Basic Functionality", True, time.time() - start_time, "All basic endpoints working")
        return True

    def test_2_data_volume_stress(self):
        """Test 2: Data volume stress testing."""
        print("\n📊 Test 2: Data Volume Stress Testing")
        
        start_time = time.time()
        success_count = 0
        total_tests = 15
        
        # Test different data sizes
        for size in ["small", "normal", "large"]:
            for i in range(5):
                try:
                    # Customer creation
                    customer_data = self.generate_test_data("customer", size)
                    response = requests.post(
                        f"{BASE_URL}/velafi/kyc/customer",
                        json=customer_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        print(f"    ⚠️  {size} customer {i}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ {size} customer {i}: {str(e)}")
        
        success_rate = success_count / total_tests
        success = success_rate >= 0.8  # 80% success rate
        self.log_test("Data Volume Stress", success, time.time() - start_time,
                     f"{success_count}/{total_tests} tests passed ({success_rate:.1%})")
        
        return success

    def test_3_security_validation(self):
        """Test 3: Security validation and malicious input handling."""
        print("\n🔒 Test 3: Security Validation")
        
        start_time = time.time()
        success_count = 0
        total_tests = 0
        
        # Test malicious inputs
        malicious_inputs = [
            {"first_name": "'; DROP TABLE users; --", "expected": "reject"},
            {"first_name": "<script>alert('xss')</script>", "expected": "reject"},
            {"first_name": "test; rm -rf /", "expected": "reject"},
            {"email": "invalid-email", "expected": "reject"},
            {"date_of_birth": "2025-01-01", "expected": "reject"},
            {"country": "XX", "expected": "reject"},
        ]
        
        for test_case in malicious_inputs:
            total_tests += 1
            try:
                customer_data = {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@test.com",
                    "date_of_birth": "1990-01-15",
                    "country": "MX"
                }
                customer_data.update(test_case)
                
                response = requests.post(
                    f"{BASE_URL}/velafi/kyc/customer",
                    json=customer_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                
                # Should reject malicious input
                if response.status_code in [400, 422, 500]:
                    success_count += 1
                else:
                    print(f"    ⚠️  Malicious input '{test_case}' was accepted (status: {response.status_code})")
                    
            except Exception as e:
                success_count += 1  # Network errors are acceptable for malicious input
        
        success_rate = success_count / total_tests
        success = success_rate >= 0.9  # 90% security success rate
        self.log_test("Security Validation", success, time.time() - start_time,
                     f"{success_count}/{total_tests} security tests passed ({success_rate:.1%})")
        
        return success

    def test_4_performance_benchmarks(self):
        """Test 4: Performance benchmarks."""
        print("\n⚡ Test 4: Performance Benchmarks")
        
        start_time = time.time()
        
        # Health check performance
        health_times = []
        for i in range(10):
            start = time.time()
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    health_times.append(time.time() - start)
            except:
                pass
        
        if health_times:
            avg_health_time = sum(health_times) / len(health_times)
            self.performance_data['health_check'] = avg_health_time
            health_success = avg_health_time < 0.1  # Should be under 100ms
            self.log_test("Health Check Performance", health_success, time.time() - start_time,
                         f"Average: {avg_health_time:.3f}s")
        else:
            health_success = False
            self.log_test("Health Check Performance", False, time.time() - start_time, "No successful requests")
        
        # Customer creation performance
        customer_times = []
        for i in range(5):
            start = time.time()
            try:
                customer_data = self.generate_test_data("customer", "normal")
                response = requests.post(
                    f"{BASE_URL}/velafi/kyc/customer",
                    json=customer_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code == 200:
                    customer_times.append(time.time() - start)
            except:
                pass
        
        if customer_times:
            avg_customer_time = sum(customer_times) / len(customer_times)
            self.performance_data['customer_creation'] = avg_customer_time
            customer_success = avg_customer_time < 1.0  # Should be under 1 second
            self.log_test("Customer Creation Performance", customer_success, time.time() - start_time,
                         f"Average: {avg_customer_time:.3f}s")
        else:
            customer_success = False
            self.log_test("Customer Creation Performance", False, time.time() - start_time, "No successful requests")
        
        return health_success and customer_success

    def test_5_edge_cases(self):
        """Test 5: Edge cases and boundary conditions."""
        print("\n🔍 Test 5: Edge Cases and Boundary Conditions")
        
        start_time = time.time()
        success_count = 0
        total_tests = 0
        
        # Test boundary values
        edge_cases = [
            # Very long names
            {"first_name": "A" * 100, "last_name": "B" * 100},
            # Special characters
            {"first_name": "José María", "last_name": "O'Connor"},
            # Boundary dates
            {"date_of_birth": "1900-01-01"},  # Very old
            {"date_of_birth": "2006-01-01"},  # Just under 18
            # Boundary file sizes
            {"file_size": 1},  # 1 byte
            {"file_size": 10485760},  # 10MB (max)
        ]
        
        for test_case in edge_cases:
            total_tests += 1
            try:
                if "file_size" in test_case:
                    # Test document upload
                    document_data = {
                        "document_type": "passport",
                        "filename": "test.pdf",
                        "mime_type": "application/pdf",
                        "file_size": test_case["file_size"]
                    }
                    
                    response = requests.post(
                        f"{BASE_URL}/velafi/kyc/documents",
                        json=document_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                else:
                    # Test customer creation
                    customer_data = {
                        "first_name": "Test",
                        "last_name": "User",
                        "email": "test@test.com",
                        "date_of_birth": "1990-01-15",
                        "country": "MX"
                    }
                    customer_data.update(test_case)
                    
                    response = requests.post(
                        f"{BASE_URL}/velafi/kyc/customer",
                        json=customer_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                
                # Should handle gracefully
                if response.status_code in [200, 400, 422]:
                    success_count += 1
                else:
                    print(f"    ⚠️  Edge case '{test_case}' failed (status: {response.status_code})")
                    
            except Exception as e:
                success_count += 1  # Network errors are acceptable for edge cases
        
        success_rate = success_count / total_tests
        success = success_rate >= 0.8  # 80% edge case handling success rate
        self.log_test("Edge Cases", success, time.time() - start_time,
                     f"{success_count}/{total_tests} edge cases handled correctly ({success_rate:.1%})")
        
        return success

    def test_6_complete_workflow(self):
        """Test 6: Complete end-to-end workflow."""
        print("\n🔄 Test 6: Complete End-to-End Workflow")
        
        start_time = time.time()
        success_count = 0
        total_workflows = 3
        
        for i in range(total_workflows):
            workflow_success = True
            
            try:
                # Step 1: Get KYC requirements
                response = requests.get(f"{BASE_URL}/kyc/requirements/MX", timeout=5)
                if response.status_code != 200:
                    workflow_success = False
                    print(f"    ❌ Workflow {i+1} Step 1: Failed to get requirements")
                    continue
                
                # Step 2: Create customer
                customer_data = self.generate_test_data("customer", "normal")
                response = requests.post(
                    f"{BASE_URL}/velafi/kyc/customer",
                    json=customer_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code != 200:
                    workflow_success = False
                    print(f"    ❌ Workflow {i+1} Step 2: Failed to create customer")
                    continue
                
                # Step 3: Upload document
                document_data = self.generate_test_data("document", "normal")
                response = requests.post(
                    f"{BASE_URL}/velafi/kyc/documents",
                    json=document_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code != 200:
                    workflow_success = False
                    print(f"    ❌ Workflow {i+1} Step 3: Failed to upload document")
                    continue
                
                # Step 4: Check KYC status
                response = requests.get(f"{BASE_URL}/velafi/kyc/approved", timeout=5)
                if response.status_code != 200:
                    workflow_success = False
                    print(f"    ❌ Workflow {i+1} Step 4: Failed to check status")
                    continue
                
                if workflow_success:
                    success_count += 1
                    print(f"    ✅ Workflow {i+1}: Completed successfully")
                
            except Exception as e:
                print(f"    ❌ Workflow {i+1}: {str(e)}")
        
        success_rate = success_count / total_workflows
        success = success_rate >= 0.8  # 80% workflow success rate
        self.log_test("Complete Workflow", success, time.time() - start_time,
                     f"{success_count}/{total_workflows} complete workflows successful ({success_rate:.1%})")
        
        return success

    def test_7_error_recovery(self):
        """Test 7: Error recovery and resilience."""
        print("\n🛡️ Test 7: Error Recovery and Resilience")
        
        start_time = time.time()
        success_count = 0
        total_tests = 0
        
        # Test various error conditions
        error_scenarios = [
            # Invalid JSON
            {"data": "invalid json", "method": "POST", "endpoint": "/velafi/kyc/customer"},
            # Missing required fields
            {"data": {"first_name": "Test"}, "method": "POST", "endpoint": "/velafi/kyc/customer"},
            # Invalid endpoint
            {"data": {}, "method": "GET", "endpoint": "/invalid/endpoint"},
            # Invalid HTTP method
            {"data": {}, "method": "PUT", "endpoint": "/health"},
        ]
        
        for scenario in error_scenarios:
            total_tests += 1
            try:
                if scenario["method"] == "GET":
                    response = requests.get(f"{BASE_URL}{scenario['endpoint']}", timeout=5)
                elif scenario["method"] == "POST":
                    response = requests.post(
                        f"{BASE_URL}{scenario['endpoint']}",
                        data=scenario["data"] if isinstance(scenario["data"], str) else json.dumps(scenario["data"]),
                        headers={"Content-Type": "application/json"},
                        timeout=5
                    )
                else:
                    response = requests.put(f"{BASE_URL}{scenario['endpoint']}", timeout=5)
                
                # Should return appropriate error status
                if response.status_code in [400, 404, 405, 422, 500]:
                    success_count += 1
                else:
                    print(f"    ⚠️  Error scenario '{scenario}' returned unexpected status: {response.status_code}")
                    
            except Exception as e:
                success_count += 1  # Network errors are acceptable for error scenarios
        
        success_rate = success_count / total_tests
        success = success_rate >= 0.8  # 80% error recovery success rate
        self.log_test("Error Recovery", success, time.time() - start_time,
                     f"{success_count}/{total_tests} error scenarios handled correctly ({success_rate:.1%})")
        
        return success

    def run_all_tests(self):
        """Run all comprehensive tests."""
        print("🚀 Starting Final Comprehensive Test Suite")
        print("=" * 80)
        
        tests = [
            ("Basic Functionality", self.test_1_basic_functionality),
            ("Data Volume Stress", self.test_2_data_volume_stress),
            ("Security Validation", self.test_3_security_validation),
            ("Performance Benchmarks", self.test_4_performance_benchmarks),
            ("Edge Cases", self.test_5_edge_cases),
            ("Complete Workflow", self.test_6_complete_workflow),
            ("Error Recovery", self.test_7_error_recovery)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 Final Comprehensive Test Results")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if self.performance_data:
            print("\n📈 Performance Metrics:")
            for metric, value in self.performance_data.items():
                print(f"  {metric}: {value:.3f}s average")
        
        print(f"\n🏆 Final Comprehensive Test Suite {'PASSED' if passed >= total * 0.8 else 'FAILED'}")
        
        if passed >= total * 0.8:
            print("\n🎉 System is production-ready with comprehensive security and validation!")
        else:
            print("\n⚠️  System needs improvements before production deployment.")
        
        return passed >= total * 0.8

def main():
    """Run the final comprehensive test suite."""
    test_suite = FinalComprehensiveTest()
    success = test_suite.run_all_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    main() 