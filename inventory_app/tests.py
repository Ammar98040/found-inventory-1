from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from inventory_app.models import Product, Order, Warehouse, Location
from inventory_app.views import process_excel_data
import json
from unittest.mock import patch, MagicMock

class SystemScenarioTest(TestCase):
    def setUp(self):
        # Setup User
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client = Client()
        self.client.login(username='admin', password='password')
        self.factory = RequestFactory()
        
        # Setup Warehouse
        self.warehouse = Warehouse.objects.create(name='Main Warehouse')

    def test_pages_connectivity(self):
        """Test that key pages load correctly (Connectivity Check)"""
        pages = [
            'inventory_app:dashboard',
            'inventory_app:products_list',
            'inventory_app:orders_list',
            'inventory_app:import_products_excel', # Fixed URL name
            'inventory_app:data_deletion',
        ]
        print("\n--- Testing Page Connectivity ---")
        for page_name in pages:
            url = reverse(page_name)
            response = self.client.get(url)
            print(f"Testing {url}: Status {response.status_code}")
            self.assertEqual(response.status_code, 200, f"Failed to load {page_name}")

    def test_excel_import_optional_fields(self):
        """Test Excel Import with Optional Name and Category"""
        print("\n--- Testing Excel Import (Optional Fields) ---")
        
        # Mock Session Data
        session_data = {
            'headers': ['Model', 'Qty', 'Name', 'Category'],
            'data': [
                ['M1', 10, 'Test Name', 'Test Cat'],
                ['M2', 20, None, None] # Should use defaults
            ]
        }
        
        # Payload with mapping
        payload = {
            'column_mapping': {
                'product_number': 0,
                'total_quantity': 1,
                'name': 2,
                'category': 3,
                'final_model': None, # Optional not used
            },
            'conflict_resolution': 'skip'
        }
        
        # Create Request
        request = self.factory.post(
            reverse('inventory_app:process_excel_data'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        request.user = self.user
        request.session = {'excel_data': session_data}
        
        # Execute View
        response = process_excel_data(request)
        response_data = json.loads(response.content)
        
        # Verify Success
        self.assertTrue(response_data.get('success'), "Excel processing failed")
        
        # Verify Product 1 (With Name/Cat)
        p1 = Product.objects.get(product_number='M1')
        self.assertEqual(p1.name, 'Test Name')
        self.assertEqual(p1.category, 'Test Cat')
        self.assertEqual(p1.quantity, 10)
        
        # Verify Product 2 (Without Name/Cat)
        p2 = Product.objects.get(product_number='M2')
        # Logic says name falls back to product_number if empty
        self.assertEqual(p2.name, 'M2') 
        self.assertIsNone(p2.category)
        self.assertEqual(p2.quantity, 20)
        print("Excel Import Logic Verified: Optional fields working correctly.")

    def test_strict_product_search(self):
        """Test Strict Product Number Search (No Partial Matching for Numbers)"""
        print("\n--- Testing Strict Product Search ---")
        
        # Create Orders with confusing product numbers
        # Order 1: Exact "2388"
        Order.objects.create(
            order_number="ORD-001",
            products_data=[
                {"product_number": "2388", "name": "Exact Match", "quantity": 5}
            ],
            total_products=1,
            total_quantities=5,
            recipient_name="Recipient A"
        )
        
        # Order 2: "2388-1" (Should NOT match "2388")
        Order.objects.create(
            order_number="ORD-002",
            products_data=[
                {"product_number": "2388-1", "name": "Partial Match", "quantity": 3}
            ],
            total_products=1,
            total_quantities=3,
            recipient_name="Recipient B"
        )
        
        # Order 3: " 2388 " (Whitespace - Should Match "2388")
        Order.objects.create(
            order_number="ORD-003",
            products_data=[
                {"product_number": " 2388 ", "name": "Whitespace Match", "quantity": 2}
            ],
            total_products=1,
            total_quantities=2,
            recipient_name="Recipient C"
        )
        
        # Order 4: Multi-product order (2388 is first, something else is second)
        # This catches the bug where loop logic was checking only the last item
        Order.objects.create(
            order_number="ORD-004",
            products_data=[
                {"product_number": "2388", "name": "Exact Match First", "quantity": 10},
                {"product_number": "9999", "name": "Other Product", "quantity": 5}
            ],
            total_products=2,
            total_quantities=15,
            recipient_name="Recipient D"
        )
        
        # Test Search for "2388"
        url = reverse('inventory_app:search_order_history')
        response = self.client.get(url, {'q': '2388'})
        data = response.json()
        
        self.assertTrue(data['success'])
        
        # Calculate expected total: 
        # ORD-001: 5
        # ORD-003: 2
        # ORD-004: 10 (Should be found!)
        # Total = 17
        self.assertEqual(data['stats']['total_withdrawn'], 17, "Search should find '2388' even if it is not the last item in the list")
        
        recipients = {r['name']: r['count'] for r in data['stats']['top_recipients']}
        self.assertIn('Recipient A', recipients)
        self.assertIn('Recipient C', recipients)
        self.assertIn('Recipient D', recipients)
        self.assertNotIn('Recipient B', recipients)
        
        print("Strict Search Logic Verified: '2388-1' excluded when searching '2388'.")

    def test_orders_list_filtering(self):
        """Test Orders List Page Filtering (Whitespace and Strictness)"""
        print("\n--- Testing Orders List Filtering ---")
        
        # Create Orders
        Order.objects.create(
            order_number="ORD-101",
            products_data=[
                {"product_number": " 502 ", "name": "Prod 502", "quantity": 10}
            ],
            recipient_name="User X",
            total_products=1, total_quantities=10
        )
        Order.objects.create(
            order_number="ORD-102",
            products_data=[
                {"product_number": "502-1", "name": "Prod 502-1", "quantity": 5}
            ],
            recipient_name="User X",
            total_products=1, total_quantities=5
        )
        
        # Filter by recipient and product_number "502"
        url = reverse('inventory_app:orders_list')
        response = self.client.get(url, {'recipient': 'User X', 'product_query': '502'})
        
        # Verify context
        recipient_items = response.context['recipient_items']
        
        # Should only find ORD-101 (quantity 10)
        # Should NOT find ORD-102 (quantity 5)
        self.assertEqual(len(recipient_items), 1)
        self.assertEqual(recipient_items[0]['quantity'], 10)
        self.assertEqual(recipient_items[0]['product_number'].strip(), "502")
        
        print("Orders List Filtering Verified: Found ' 502 ' with query '502', ignored '502-1'.")

    @patch('playwright.sync_api.sync_playwright')
    def test_order_pdf_export(self, mock_playwright_func):
        """Test Order PDF Export (Mocking Playwright)"""
        print("\n--- Testing Order PDF Export ---")
        
        # Create Order
        product = Product.objects.create(product_number='P-PDF', name='PDF Product', quantity=100)
        order = Order.objects.create(
            user=self.user,
            recipient_name="Test Client",
            products_data=[{'product_number': 'P-PDF', 'quantity': 5, 'name': 'PDF Product'}]
        )
        
        # Mock Playwright context manager
        mock_playwright_obj = MagicMock()
        mock_playwright_func.return_value.__enter__.return_value = mock_playwright_obj
        
        mock_browser = MagicMock()
        mock_playwright_obj.chromium.launch.return_value = mock_browser
        
        mock_page = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_page.pdf.return_value = b'%PDF-1.4 mock content'
        
        # Call View
        url = reverse('inventory_app:export_order_pdf', args=[order.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.has_header('Content-Disposition'))
        print("PDF Export View Verified (Status 200, PDF Content-Type")

    def test_data_deletion_password(self):
        """Test Data Deletion Password Validation"""
        print("\n--- Testing Data Deletion Security ---")
        
        url = reverse('inventory_app:delete_data')
        
        # 1. Wrong Password
        data_wrong = {
            'password': 'wrong_password',
            'delete_products': True
        }
        response = self.client.post(url, data_wrong, content_type='application/json')
        # Expect 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])
        
        # 2. Correct Password
        # Create a product to delete
        Product.objects.create(product_number='TO_DELETE', quantity=1)
        self.assertEqual(Product.objects.count(), 1)
        
        data_correct = {
            'password': 'Thepest**1',
            'delete_products': True
        }
        response = self.client.post(url, data_correct, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Product.objects.count(), 0)
        print("Data Deletion Logic Verified: Password check and deletion working.")

    def test_compact_row(self):
        """Test Compact Row Functionality"""
        print("\n--- Testing Row Compaction ---")
        
        # Create Warehouse
        warehouse = Warehouse.objects.create(name="Test Warehouse", rows_count=5, columns_count=10)
        
        # Create Locations
        l1 = Location.objects.create(warehouse=warehouse, row=1, column=1)
        l2 = Location.objects.create(warehouse=warehouse, row=1, column=2)
        l3 = Location.objects.create(warehouse=warehouse, row=1, column=3)
        l4 = Location.objects.create(warehouse=warehouse, row=1, column=4)
        l5 = Location.objects.create(warehouse=warehouse, row=1, column=5)
        
        # Create Products with gaps: P1 at C1, P2 at C3, P3 at C5
        p1 = Product.objects.create(product_number='P1', name='P1', location=l1, quantity=10)
        p2 = Product.objects.create(product_number='P2', name='P2', location=l3, quantity=10)
        p3 = Product.objects.create(product_number='P3', name='P3', location=l5, quantity=10)
        
        # Verify initial state
        self.assertEqual(p1.location, l1)
        self.assertEqual(p2.location, l3)
        self.assertEqual(p3.location, l5)
        self.assertEqual(Location.objects.filter(row=1, products__isnull=False).count(), 3)
        
        # Call API
        url = reverse('inventory_app:compact_row')
        data = {
            'row': 1,
            'warehouse_id': warehouse.id
        }
        
        # Assuming we need login, but we are using client which might not be logged in as admin?
        # The view has @login_required.
        # We need to create a user and login.
        user = User.objects.create_user(username='testadmin', password='password')
        self.client.force_login(user)
        
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Refresh products
        p1.refresh_from_db()
        p2.refresh_from_db()
        p3.refresh_from_db()
        
        # Verify new locations
        # Should be C1, C2, C3
        self.assertEqual(p1.location.column, 1)
        self.assertEqual(p2.location.column, 2)
        self.assertEqual(p3.location.column, 3)
        
        # Verify old locations empty
        self.assertFalse(l4.products.exists())
        self.assertFalse(l5.products.exists())
        
        print("Row Compaction Verified: Gaps filled correctly.")
