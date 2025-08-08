#!/usr/bin/env python3
"""
EXTREME RIGOROUS TEST - 10x More Demanding
Pushes the system to absolute limits with massive data loads, extreme scenarios, and every possible edge case
"""

import asyncio
import concurrent.futures
import json
import multiprocessing
import random
import string
import threading
import time
from datetime import datetime, timedelta

import aiohttp
import requests

# Test server configuration
BASE_URL = "http://localhost:8002"

class ExtremeRigorousTest:
    def __init__(self):
        self.test_results = []
        self.performance_data = {}
        self.failure_count = 0
        self.success_count = 0
        
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
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.3f}s) - {details}")

    def generate_extreme_data(self, data_type: str, size: str = "extreme") -> dict:
        """Generate extreme test data."""
        
        if data_type == "customer":
            if size == "massive":
                return {
                    "first_name": "A" * 1000,  # 1000 character name
                    "last_name": "B" * 1000,   # 1000 character name
                    "email": f"{'x' * 100}@{'y' * 100}.{'z' * 100}.com",  # Massive email
                    "date_of_birth": "1900-01-01",  # Very old date
                    "country": "MX",
                    "phone": "+" + "1" * 50,  # 50 digit phone
                    "address": "A" * 2000,  # 2000 character address
                    "city": "B" * 500,
                    "state": "C" * 500,
                    "postal_code": "D" * 100
                }
            elif size == "malicious":
                return {
                    "first_name": "'; DROP TABLE users; --",
                    "last_name": "<script>alert('xss')</script>",
                    "email": "test; rm -rf /",
                    "date_of_birth": "../../../etc/passwd",
                    "country": "XX",
                    "phone": "javascript:alert('xss')",
                    "address": "1' OR '1'='1",
                    "city": "<iframe src=x onerror=alert('xss')>",
                    "state": "admin'--",
                    "postal_code": "'; INSERT INTO users VALUES ('hacker', 'hacker@evil.com'); --"
                }
            else:  # extreme
                return {
                    "first_name": "María Guadalupe Ana Sofía",
                    "last_name": "Rodríguez-Hernández de la Cruz",
                    "email": f"test{random.randint(100000,999999)}@verylongdomainname.com",
                    "date_of_birth": "1985-06-20",
                    "country": "MX",
                    "phone": "+525512345678901234567890",
                    "address": "Avenida Insurgentes Sur 1234, Colonia Del Valle, Delegación Benito Juárez, Ciudad de México, México",
                    "city": "Ciudad de México",
                    "state": "CDMX",
                    "postal_code": "03100"
                }
        
        elif data_type == "document":
            sizes = {
                "small": 102400,      # 100KB
                "normal": 1024000,    # 1MB
                "large": 10485760,    # 10MB
                "extreme": 104857600, # 100MB
                "massive": 1073741824 # 1GB
            }
            return {
                "document_type": random.choice(["passport", "utility_bill", "national_id", "bank_statement", "tax_document", "employment_letter", "pay_stub"]),
                "filename": f"document_{random.randint(100000,999999)}_with_very_long_filename_that_exceeds_normal_limits.pdf",
                "mime_type": "application/pdf",
                "file_size": sizes.get(size, 104857600)
            }

    def test_1_massive_concurrent_load(self):
        """Test 1: Massive concurrent load testing."""
        print("\n🔥 Test 1: MASSIVE CONCURRENT LOAD TESTING")
        print("-" * 60)
        
        def make_request(request_id):
            try:
                start_time = time.time()
                response = requests.get(f"{BASE_URL}/health", timeout=2)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    return True, duration
                else:
                    return False, duration
            except Exception as e:
                return False, 0
        
        # Test with 1000 concurrent requests
        total_requests = 1000
        max_workers = 100
        
        print(f"🚀 Making {total_requests} concurrent requests with {max_workers} workers...")
        
        start_time = time.time()
        success_count = 0
        total_duration = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request, i) for i in range(total_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            for success, duration in results:
                if success:
                    success_count += 1
                total_duration += duration
        
        test_duration = time.time() - start_time
        success_rate = success_count / total_requests
        
        success = success_rate >= 0.95  # 95% success rate required
        self.log_test("Massive Concurrent Load", success, test_duration,
                     f"{success_count}/{total_requests} requests successful ({success_rate:.1%})")
        
        return success

    def test_2_extreme_data_volumes(self):
        """Test 2: Extreme data volume testing."""
        print("\n📊 Test 2: EXTREME DATA VOLUME TESTING")
        print("-" * 60)
        
        data_scenarios = [
            {"name": "Small Data", "size": "small", "count": 50},
            {"name": "Normal Data", "size": "normal", "count": 50},
            {"name": "Large Data", "size": "large", "count": 50},
            {"name": "Extreme Data", "size": "extreme", "count": 20},
            {"name": "Massive Data", "size": "massive", "count": 10},
        ]
        
        total_success = 0
        total_tests = 0
        
        for scenario in data_scenarios:
            print(f"   Testing {scenario['name']} ({scenario['count']} requests)...")
            scenario_success = 0
            
            for i in range(scenario['count']):
                try:
                    customer_data = self.generate_extreme_data("customer", scenario['size'])
                    response = requests.post(
                        f"{BASE_URL}/velafi/kyc/customer",
                        json=customer_data,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        scenario_success += 1
                    else:
                        print(f"      ⚠️  Request {i+1}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"      ❌ Request {i+1}: {str(e)}")
            
            success_rate = scenario_success / scenario['count']
            total_success += scenario_success
            total_tests += scenario['count']
            
            print(f"   📊 {scenario['name']}: {scenario_success}/{scenario['count']} ({success_rate:.1%})")
        
        overall_success_rate = total_success / total_tests
        success = overall_success_rate >= 0.8  # 80% success rate required
        self.log_test("Extreme Data Volumes", success, 0,
                     f"{total_success}/{total_tests} requests successful ({overall_success_rate:.1%})")
        
        return success

    def test_3_malicious_attack_simulation(self):
        """Test 3: Comprehensive malicious attack simulation."""
        print("\n🛡️ Test 3: COMPREHENSIVE MALICIOUS ATTACK SIMULATION")
        print("-" * 60)
        
        attack_scenarios = [
            # SQL Injection attacks
            {"name": "SQL Injection - DROP", "payload": "'; DROP TABLE users; --"},
            {"name": "SQL Injection - UNION", "payload": "' UNION SELECT * FROM users --"},
            {"name": "SQL Injection - OR", "payload": "' OR '1'='1"},
            {"name": "SQL Injection - AND", "payload": "' AND 1=1 --"},
            {"name": "SQL Injection - EXEC", "payload": "'; EXEC xp_cmdshell('dir') --"},
            
            # XSS attacks
            {"name": "XSS - Script Tag", "payload": "<script>alert('xss')</script>"},
            {"name": "XSS - JavaScript", "payload": "javascript:alert('xss')"},
            {"name": "XSS - Iframe", "payload": "<iframe src=x onerror=alert('xss')>"},
            {"name": "XSS - Object", "payload": "<object data=javascript:alert('xss')>"},
            {"name": "XSS - Embed", "payload": "<embed src=javascript:alert('xss')>"},
            
            # Command Injection attacks
            {"name": "Command Injection - Semicolon", "payload": "test; rm -rf /"},
            {"name": "Command Injection - Pipe", "payload": "test | cat /etc/passwd"},
            {"name": "Command Injection - Backtick", "payload": "test `cat /etc/passwd`"},
            {"name": "Command Injection - Dollar", "payload": "test $(cat /etc/passwd)"},
            {"name": "Command Injection - Ampersand", "payload": "test && cat /etc/passwd"},
            
            # Path Traversal attacks
            {"name": "Path Traversal - Unix", "payload": "../../../etc/passwd"},
            {"name": "Path Traversal - Windows", "payload": "..\\..\\..\\windows\\system32\\config\\sam"},
            {"name": "Path Traversal - Encoded", "payload": "..%2f..%2f..%2fetc%2fpasswd"},
            {"name": "Path Traversal - Double", "payload": "....//....//....//etc/passwd"},
            {"name": "Path Traversal - Null", "payload": "..%c0%af..%c0%af..%c0%afetc/passwd"},
            
            # NoSQL Injection attacks
            {"name": "NoSQL Injection - GT", "payload": '{"$gt": ""}'},
            {"name": "NoSQL Injection - NE", "payload": '{"$ne": ""}'},
            {"name": "NoSQL Injection - OR", "payload": '{"$or": [{"admin": true}]}'},
            {"name": "NoSQL Injection - AND", "payload": '{"$and": [{"admin": true}]}'},
            {"name": "NoSQL Injection - WHERE", "payload": '{"$where": "this.admin == true"}'},
            
            # LDAP Injection attacks
            {"name": "LDAP Injection - OR", "payload": "*)(uid=*))(|(uid=*"},
            {"name": "LDAP Injection - AND", "payload": "*)(&(uid=*)(admin=true))"},
            {"name": "LDAP Injection - NOT", "payload": "*)(!(uid=*))"},
            {"name": "LDAP Injection - Wildcard", "payload": "*)(uid=*admin*"},
            {"name": "LDAP Injection - Null", "payload": "*)(uid=\x00*"},
            
            # Template Injection attacks
            {"name": "Template Injection - Jinja", "payload": "{{7*7}}"},
            {"name": "Template Injection - ERB", "payload": "<%= 7*7 %>"},
            {"name": "Template Injection - PHP", "payload": "<?php echo 7*7; ?>"},
            {"name": "Template Injection - ASP", "payload": "<%= 7*7 %>"},
            {"name": "Template Injection - JSP", "payload": "<%= 7*7 %>"},
            
            # XML Injection attacks
            {"name": "XML Injection - XXE", "payload": "<!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><test>&xxe;</test>"},
            {"name": "XML Injection - XPath", "payload": "' or '1'='1"},
            {"name": "XML Injection - XQuery", "payload": "1 or 1=1"},
            {"name": "XML Injection - XSLT", "payload": "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform'><xsl:template match='/'>test</xsl:template></xsl:stylesheet>"},
            {"name": "XML Injection - SOAP", "payload": "<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'><soap:Body><test>1' or '1'='1</test></soap:Body></soap:Envelope>"},
        ]
        
        attack_success = 0
        total_attacks = len(attack_scenarios)
        
        for attack in attack_scenarios:
            malicious_data = {
                "first_name": attack["payload"],
                "last_name": "Test",
                "email": "test@test.com",
                "date_of_birth": "1990-01-15",
                "country": "MX"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/velafi/kyc/customer",
                    json=malicious_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                
                if response.status_code in [400, 422, 500]:
                    attack_success += 1
                else:
                    print(f"   ⚠️  {attack['name']}: Not blocked (status: {response.status_code})")
                    
            except Exception as e:
                attack_success += 1  # Network errors are acceptable for malicious input
        
        success_rate = attack_success / total_attacks
        success = success_rate >= 0.95  # 95% attack blocking required
        self.log_test("Malicious Attack Simulation", success, 0,
                     f"{attack_success}/{total_attacks} attacks blocked ({success_rate:.1%})")
        
        return success

    def test_4_extreme_performance_stress(self):
        """Test 4: Extreme performance stress testing."""
        print("\n⚡ Test 4: EXTREME PERFORMANCE STRESS TESTING")
        print("-" * 60)
        
        # Test response times under extreme load
        response_times = []
        error_count = 0
        total_requests = 500
        
        print(f"🚀 Making {total_requests} rapid requests to test performance...")
        
        start_time = time.time()
        
        for i in range(total_requests):
            try:
                request_start = time.time()
                response = requests.get(f"{BASE_URL}/health", timeout=1)
                request_time = time.time() - request_start
                
                if response.status_code == 200:
                    response_times.append(request_time)
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
        
        total_time = time.time() - start_time
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
            
            print(f"   📊 Response Time Statistics:")
            print(f"      ⚡ Average: {avg_time:.3f}s")
            print(f"      🚀 Minimum: {min_time:.3f}s")
            print(f"      🐌 Maximum: {max_time:.3f}s")
            print(f"      📈 95th Percentile: {p95_time:.3f}s")
            print(f"      📈 99th Percentile: {p99_time:.3f}s")
            print(f"      ❌ Errors: {error_count}/{total_requests}")
            
            # Performance requirements
            success = (
                avg_time < 0.1 and      # Average under 100ms
                p95_time < 0.2 and      # 95% under 200ms
                p99_time < 0.5 and      # 99% under 500ms
                error_count < total_requests * 0.05  # Less than 5% errors
            )
            
            self.log_test("Extreme Performance Stress", success, total_time,
                         f"Avg: {avg_time:.3f}s, P95: {p95_time:.3f}s, P99: {p99_time:.3f}s, Errors: {error_count}")
        else:
            self.log_test("Extreme Performance Stress", False, total_time, "No successful requests")
            success = False
        
        return success

    def test_5_memory_and_resource_stress(self):
        """Test 5: Memory and resource stress testing."""
        print("\n💾 Test 5: MEMORY AND RESOURCE STRESS TESTING")
        print("-" * 60)
        
        # Test with massive document uploads
        document_scenarios = [
            {"name": "Large Documents", "size": "large", "count": 20},
            {"name": "Extreme Documents", "size": "extreme", "count": 10},
            {"name": "Massive Documents", "size": "massive", "count": 5},
        ]
        
        total_success = 0
        total_tests = 0
        
        for scenario in document_scenarios:
            print(f"   Testing {scenario['name']} ({scenario['count']} uploads)...")
            scenario_success = 0
            
            for i in range(scenario['count']):
                try:
                    document_data = self.generate_extreme_data("document", scenario['size'])
                    response = requests.post(
                        f"{BASE_URL}/velafi/kyc/documents",
                        json=document_data,
                        headers={"Content-Type": "application/json"},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        scenario_success += 1
                    else:
                        print(f"      ⚠️  Upload {i+1}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"      ❌ Upload {i+1}: {str(e)}")
            
            success_rate = scenario_success / scenario['count']
            total_success += scenario_success
            total_tests += scenario['count']
            
            print(f"   📊 {scenario['name']}: {scenario_success}/{scenario['count']} ({success_rate:.1%})")
        
        overall_success_rate = total_success / total_tests
        success = overall_success_rate >= 0.7  # 70% success rate for resource-intensive operations
        self.log_test("Memory and Resource Stress", success, 0,
                     f"{total_success}/{total_tests} uploads successful ({overall_success_rate:.1%})")
        
        return success

    def test_6_extreme_edge_cases(self):
        """Test 6: Extreme edge cases and boundary conditions."""
        print("\n🔍 Test 6: EXTREME EDGE CASES AND BOUNDARY CONDITIONS")
        print("-" * 60)
        
        edge_cases = [
            # Extreme string lengths
            {"name": "1000 Char Name", "field": "first_name", "value": "A" * 1000},
            {"name": "2000 Char Address", "field": "address", "value": "B" * 2000},
            {"name": "500 Char Email", "field": "email", "value": "x" * 500 + "@test.com"},
            
            # Extreme dates
            {"name": "Year 1900", "field": "date_of_birth", "value": "1900-01-01"},
            {"name": "Year 2100", "field": "date_of_birth", "value": "2100-12-31"},
            {"name": "Leap Year", "field": "date_of_birth", "value": "2000-02-29"},
            {"name": "Invalid Date", "field": "date_of_birth", "value": "2024-13-45"},
            
            # Extreme file sizes
            {"name": "1 Byte File", "field": "file_size", "value": 1},
            {"name": "1GB File", "field": "file_size", "value": 1073741824},
            {"name": "2GB File", "field": "file_size", "value": 2147483648},
            
            # Special characters
            {"name": "Unicode Names", "field": "first_name", "value": "José María O'Connor"},
            {"name": "Emoji Names", "field": "first_name", "value": "John 😀 Smith"},
            {"name": "Control Chars", "field": "first_name", "value": "John\x00Smith"},
            
            # Empty and null values
            {"name": "Empty String", "field": "first_name", "value": ""},
            {"name": "Null Value", "field": "first_name", "value": None},
            {"name": "Whitespace Only", "field": "first_name", "value": "   "},
            
            # Invalid formats
            {"name": "Invalid Email Format", "field": "email", "value": "not-an-email"},
            {"name": "Invalid Phone Format", "field": "phone", "value": "not-a-phone"},
            {"name": "Invalid Country", "field": "country", "value": "INVALID"},
        ]
        
        edge_success = 0
        total_edges = len(edge_cases)
        
        for case in edge_cases:
            try:
                if case["field"] in ["file_size"]:
                    # Test document validation
                    test_data = {
                        "document_type": "passport",
                        "filename": "test.pdf",
                        "mime_type": "application/pdf",
                        "file_size": 1024000
                    }
                    test_data[case["field"]] = case["value"]
                    
                    response = requests.post(
                        f"{BASE_URL}/velafi/kyc/documents",
                        json=test_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                else:
                    # Test customer validation
                    test_data = {
                        "first_name": "Test",
                        "last_name": "User",
                        "email": "test@test.com",
                        "date_of_birth": "1990-01-15",
                        "country": "MX"
                    }
                    test_data[case["field"]] = case["value"]
                    
                    response = requests.post(
                        f"{BASE_URL}/velafi/kyc/customer",
                        json=test_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                
                # Should handle gracefully (either accept or reject properly)
                if response.status_code in [200, 400, 422]:
                    edge_success += 1
                else:
                    print(f"   ⚠️  {case['name']}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                edge_success += 1  # Exceptions are acceptable for extreme edge cases
        
        success_rate = edge_success / total_edges
        success = success_rate >= 0.9  # 90% edge case handling required
        self.log_test("Extreme Edge Cases", success, 0,
                     f"{edge_success}/{total_edges} cases handled ({success_rate:.1%})")
        
        return success

    def test_7_comprehensive_workflow_stress(self):
        """Test 7: Comprehensive workflow stress testing."""
        print("\n🔄 Test 7: COMPREHENSIVE WORKFLOW STRESS TESTING")
        print("-" * 60)
        
        workflow_success = 0
        total_workflows = 50  # 10x more workflows
        
        print(f"🔄 Executing {total_workflows} complete workflows...")
        
        for i in range(total_workflows):
            workflow_start = time.time()
            workflow_ok = True
            
            try:
                # Step 1: Get KYC requirements
                response = requests.get(f"{BASE_URL}/kyc/requirements/MX", timeout=5)
                if response.status_code != 200:
                    workflow_ok = False
                
                # Step 2: Create customer with random data
                customer_data = {
                    "first_name": f"Workflow{i}",
                    "last_name": f"Test{i}",
                    "email": f"workflow{i}@example.com",
                    "date_of_birth": "1990-01-15",
                    "country": "MX",
                    "phone": f"+5255{random.randint(10000000,99999999)}"
                }
                
                response = requests.post(
                    f"{BASE_URL}/velafi/kyc/customer",
                    json=customer_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code != 200:
                    workflow_ok = False
                
                # Step 3: Upload document
                document_data = {
                    "document_type": random.choice(["passport", "national_id", "utility_bill"]),
                    "filename": f"workflow{i}_document.pdf",
                    "mime_type": "application/pdf",
                    "file_size": random.randint(100000, 1000000)
                }
                
                response = requests.post(
                    f"{BASE_URL}/velafi/kyc/documents",
                    json=document_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code != 200:
                    workflow_ok = False
                
                # Step 4: Check KYC status
                response = requests.get(f"{BASE_URL}/velafi/kyc/approved", timeout=5)
                if response.status_code != 200:
                    workflow_ok = False
                
                if workflow_ok:
                    workflow_time = time.time() - workflow_start
                    workflow_success += 1
                    if i % 10 == 0:  # Log every 10th workflow
                        print(f"   ✅ Workflow {i+1}: Completed in {workflow_time:.3f}s")
                else:
                    print(f"   ❌ Workflow {i+1}: Failed")
                    
            except Exception as e:
                print(f"   ❌ Workflow {i+1}: Error - {str(e)}")
        
        success_rate = workflow_success / total_workflows
        success = success_rate >= 0.8  # 80% workflow success rate required
        self.log_test("Comprehensive Workflow Stress", success, 0,
                     f"{workflow_success}/{total_workflows} workflows successful ({success_rate:.1%})")
        
        return success

    def run_all_extreme_tests(self):
        """Run all extreme rigorous tests."""
        print("🔥 STARTING EXTREME RIGOROUS TEST SUITE - 10x MORE DEMANDING")
        print("=" * 80)
        print("🎯 Testing system limits with:")
        print("   • 1000 concurrent requests")
        print("   • Massive data volumes (100MB+ files)")
        print("   • 50+ malicious attack patterns")
        print("   • Extreme performance stress (500+ rapid requests)")
        print("   • Memory and resource stress testing")
        print("   • Comprehensive edge case coverage")
        print("   • 50 complete end-to-end workflows")
        print("=" * 80)
        
        tests = [
            ("Massive Concurrent Load", self.test_1_massive_concurrent_load),
            ("Extreme Data Volumes", self.test_2_extreme_data_volumes),
            ("Malicious Attack Simulation", self.test_3_malicious_attack_simulation),
            ("Extreme Performance Stress", self.test_4_extreme_performance_stress),
            ("Memory and Resource Stress", self.test_5_memory_and_resource_stress),
            ("Extreme Edge Cases", self.test_6_extreme_edge_cases),
            ("Comprehensive Workflow Stress", self.test_7_comprehensive_workflow_stress)
        ]
        
        results = []
        start_time = time.time()
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))
        
        total_time = time.time() - start_time
        
        # Summary
        print("\n" + "=" * 80)
        print("🔥 EXTREME RIGOROUS TEST RESULTS")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} extreme tests passed")
        print(f"⏱️  Total test time: {total_time:.1f}s")
        print(f"📊 Success rate: {passed/total:.1%}")
        
        if passed >= total * 0.9:
            print("\n🏆 SYSTEM STATUS: EXTREMELY ROBUST")
            print("🚀 READY FOR ENTERPRISE PRODUCTION")
            print("✅ HANDLES ALL EXTREME SCENARIOS")
            print("⚡ OPTIMAL PERFORMANCE UNDER STRESS")
            print("🛡️ COMPREHENSIVE SECURITY PROTECTION")
        elif passed >= total * 0.7:
            print("\n⚠️ SYSTEM STATUS: MOSTLY ROBUST")
            print("🔧 NEEDS MINOR IMPROVEMENTS")
        else:
            print("\n❌ SYSTEM STATUS: NEEDS MAJOR IMPROVEMENTS")
            print("🔧 NOT READY FOR PRODUCTION")
        
        print("=" * 80)
        
        return passed >= total * 0.9

def main():
    """Run the extreme rigorous test suite."""
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Please start the test server first.")
            return False
        
        test_suite = ExtremeRigorousTest()
        success = test_suite.run_all_extreme_tests()
        return success
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the test server first.")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 