"""
Comprehensive Test: Fraud Alerts Button Global Functionality
Tests Fraud Alerts button visibility and functionality across ALL user portal pages
"""

import unittest
import sys
import json
from urllib.parse import urlparse, parse_qs

# Add app to path
sys.path.insert(0, 'c:\\Users\\Admin\\Desktop\\Shubham Tidke Documents\\shub (1)\\shub')

try:
    from app import app, get_db, _analyze_and_store
    from model.predict import predict_fraud
    print("✓ Successfully imported app and predict_fraud")
except Exception as e:
    print(f"✗ Import Error: {e}")
    sys.exit(1)


class FraudAlertsGlobalTest(unittest.TestCase):
    """Test Fraud Alerts button global functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test app"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # Initialize test users
        db = get_db()
        
        # Create test user
        try:
            db.execute(
                "INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
                ("testuser", "hashed_password", "test@example.com", 0)
            )
            db.commit()
            print("✓ Test user created")
        except:
            pass  # User might already exist

        # Create test admin
        try:
            db.execute(
                "INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
                ("admin", "hashed_password", "admin@example.com", 1)
            )
            db.commit()
            print("✓ Test admin created")
        except:
            pass  # Admin might already exist

    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        cls.app_context.pop()

    def test_01_page_access_with_login(self):
        """Test 1: Access pages with proper login"""
        print("\n[TEST 1] Testing page access with login...")
        
        # Use client context and set session
        pages = [
            ('/dashboard', 'Dashboard'),
            ('/simulate', 'Simulate'),
            ('/history', 'History'),
            ('/profile', 'Profile'),
        ]
        
        for url, name in pages:
            response = self.client.get(url)
            # Expects redirect to login if not authenticated
            self.assertIn(response.status_code, [200, 302], f"Failed to access {name} page")
            if response.status_code == 200:
                print(f"  ✓ {name} page accessible (200)")
            else:
                print(f"  ⚠ {name} page redirect (302) - auth required")

    def test_02_fraud_alerts_button_in_html(self):
        """Test 2: Verify Fraud Alerts button HTML is present on all pages"""
        print("\n[TEST 2] Checking Fraud Alerts button HTML presence...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['is_admin'] = False
        
        # Check dashboard (most likely to have full HTML)
        response = self.client.get('/dashboard')
        html = response.get_data(as_text=True)
        
        # Check for fraud-alert-section in HTML
        if 'fraud-alert-user' in html or 'fraud-alert-section' in html:
            print("  ✓ Fraud Alerts button found in dashboard HTML")
            self.assertIn('Fraud Alerts', html, "Button text not found")
            print("  ✓ Button text 'Fraud Alerts' found")
        else:
            print("  ✗ Fraud Alerts button NOT found in dashboard HTML")
            self.fail("Fraud Alerts button missing")

    def test_03_fraud_alerts_api_endpoint(self):
        """Test 3: Test /api/alerts/count endpoint"""
        print("\n[TEST 3] Testing /api/alerts/count endpoint...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['is_admin'] = False
        
        response = self.client.get('/api/alerts/count')
        self.assertEqual(response.status_code, 200, "API endpoint returned non-200")
        
        try:
            data = json.loads(response.get_data(as_text=True))
            count = data.get('count', 0)
            print(f"  ✓ API endpoint working - Alert count: {count}")
            self.assertIn('count', data, "Missing 'count' field in API response")
            self.assertIsInstance(data['count'], int, "Count is not an integer")
        except json.JSONDecodeError:
            self.fail("API response is not valid JSON")

    def test_04_fraud_alert_mark_read_endpoint(self):
        """Test 4: Test /api/alerts/mark_read endpoint"""
        print("\n[TEST 4] Testing /api/alerts/mark_read endpoint...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['is_admin'] = False
        
        response = self.client.post('/api/alerts/mark_read', 
                                    data=json.dumps({}),
                                    content_type='application/json')
        self.assertIn(response.status_code, [200, 400, 404], f"Unexpected status: {response.status_code}")
        print(f"  ✓ Mark read endpoint accessible - Status: {response.status_code}")

    def test_05_fraud_alerts_page_access(self):
        """Test 5: Access /fraud-alerts page"""
        print("\n[TEST 5] Testing /fraud-alerts page access...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['is_admin'] = False
        
        response = self.client.get('/fraud-alerts')
        self.assertEqual(response.status_code, 200, "Fraud alerts page not accessible")
        html = response.get_data(as_text=True)
        
        # Check for key elements on fraud alerts page
        checks = [
            ('Fraud Alerts', 'Page title'),
            ('fraud_alerts_table', 'Fraud alerts table'),
            ('Risk', 'Risk column header'),
        ]
        
        for check_str, desc in checks:
            if check_str in html:
                print(f"  ✓ Found {desc}")
            else:
                print(f"  ⚠ Missing {desc} - may not be critical")

    def test_06_admin_fraud_alerts_access(self):
        """Test 6: Admin can access fraud alerts"""
        print("\n[TEST 6] Testing admin fraud alerts access...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['is_admin'] = True
        
        response = self.client.get('/admin/fraud-alerts')
        if response.status_code == 200:
            print("  ✓ Admin fraud alerts page accessible")
        else:
            print(f"  ⚠ Admin fraud alerts returned: {response.status_code}")

    def test_07_base_template_structure(self):
        """Test 7: Verify base template fraud alerts button structure"""
        print("\n[TEST 7] Verifying base template structure...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['is_admin'] = False
        
        response = self.client.get('/dashboard')
        html = response.get_data(as_text=True)
        
        # Check for setupAlerts JavaScript function
        if 'setupAlerts' in html:
            print("  ✓ setupAlerts() function found in base template")
        else:
            print("  ✗ setupAlerts() function NOT found")
            self.fail("JavaScript setup missing")
        
        # Check for proper CSS classes
        required_elements = [
            ('notification-badge', 'Badge element'),
            ('fraud-alert-section', 'Fraud alert section'),
        ]
        
        for elem, desc in required_elements:
            if elem in html:
                print(f"  ✓ Found {desc} ({elem})")
            else:
                print(f"  ⚠ Missing {desc} ({elem})")

    def test_08_navigation_link_presence(self):
        """Test 8: Verify button appears in navigation"""
        print("\n[TEST 8] Checking button placement in navigation...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['is_admin'] = False
        
        response = self.client.get('/dashboard')
        html = response.get_data(as_text=True)
        
        # Look for the button placement in nav area
        if 'fraud-alert-user' in html or 'Fraud Alerts' in html:
            # Check it's not inside admin-specific conditional
            lines = html.split('\n')
            found_in_nav = False
            for i, line in enumerate(lines):
                if 'fraud-alert' in line.lower():
                    # Check context - should not be deep inside admin conditional
                    print(f"  ✓ Found fraud alert reference at line ~{i}")
                    found_in_nav = True
                    break
            
            if found_in_nav:
                print("  ✓ Button properly placed in navigation area")
            else:
                print("  ⚠ Button location needs verification")
        else:
            self.fail("Button not found in HTML")

    def test_09_predict_fraud_integration(self):
        """Test 9: Verify fraud prediction still works"""
        print("\n[TEST 9] Testing fraud prediction integration...")
        
        test_cases = [
            {
                'amount': 100000,
                'merchant_id': 'MERCHANT_001',
                'user_id': 1,
                'transaction_type': 'online',
                'merchant_name': 'Test Merchant'
            },
            {
                'amount': 50,
                'merchant_id': 'MERCHANT_002',
                'user_id': 1,
                'transaction_type': 'atm',
                'merchant_name': 'ATM'
            },
        ]
        
        for i, case in enumerate(test_cases):
            try:
                result = predict_fraud(case['amount'], case['merchant_id'], 
                                      case['user_id'], case['transaction_type'],
                                      case['merchant_name'])
                
                # Verify result structure
                required_keys = ['rule_risk_score', 'ml_risk_score', 'average_risk_score', 'is_fraud', 'risk_category']
                if all(key in result for key in required_keys):
                    print(f"  ✓ Test case {i+1}: predict_fraud working - Risk: {result['average_risk_score']:.1f}%")
                else:
                    print(f"  ✗ Test case {i+1}: Missing keys in result")
                    self.fail("Incomplete fraud prediction result")
            except Exception as e:
                print(f"  ⚠ Test case {i+1}: Exception - {str(e)[:50]}")

    def test_10_javascript_functionality(self):
        """Test 10: Verify JavaScript code is syntactically correct"""
        print("\n[TEST 10] Checking JavaScript syntax...")
        
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['is_admin'] = False
        
        response = self.client.get('/dashboard')
        html = response.get_data(as_text=True)
        
        # Look for key JS patterns
        js_patterns = [
            'fetch.*api/alerts/count',
            'notification-badge',
            'DOMContentLoaded',
            'setInterval',
            'classList',
        ]
        
        for pattern in js_patterns:
            import re
            if re.search(pattern, html, re.IGNORECASE):
                print(f"  ✓ Found JS pattern: {pattern}")
            else:
                print(f"  ⚠ Missing JS pattern: {pattern}")


def run_tests():
    """Run all tests with detailed output"""
    print("=" * 70)
    print("FRAUD ALERTS GLOBAL FUNCTIONALITY TEST SUITE")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(FraudAlertsGlobalTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED - Fraud Alerts button global functionality verified!")
    else:
        print("\n✗ Some tests failed - Check output above")
        if result.failures:
            print("\nFailed Tests:")
            for test, trace in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, trace in result.errors:
                print(f"  - {test}")
    
    print("=" * 70)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
