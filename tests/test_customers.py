import unittest
from app import create_app, db
from app.models import Customer
from werkzeug.security import generate_password_hash

class CustomerTests(unittest.TestCase):
 def setUp(self):
    self.app = create_app('TestingConfig')
    self.client = self.app.test_client()

    with self.app.app_context():
        db.create_all()
        self.customer = Customer(name="Test Customer", email="test@customer.com", phone='456-7890', password="testpass")
        db.session.add(self.customer)
        db.session.commit()

    res = self.client.post('/login', json={
        "email": "test@customer.com",
        "password": "testpass"
    })

    if res.status_code != 200:
        print(f"Login failed: {res.status_code}, {res.data}")
        raise Exception("Login failed in test setup")

    self.token = res.get_json().get("token")

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_customers(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = self.client.get('/users/', headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_my_tickets(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = self.client.get('/users/my-tickets', headers=headers)
        self.assertIn(res.status_code, [200, 404])  # allow 404 if no tickets exist yet

    def test_customer_update_unauthorized(self):
        res = self.client.put(f'/users/{self.customer.id}', json={"name": "Hacker"})
        self.assertEqual(res.status_code, 401)  # no token passed
