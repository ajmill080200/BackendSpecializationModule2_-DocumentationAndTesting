import unittest
from app import create_app, db
from app.models import Customer, Inventory

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

            customer = Customer(email="test@example.com", password="testpass")
            db.session.add(customer)
            db.session.commit()

            res = self.client.post('/login', json={
                "email": "test@example.com",
                "password": "testpass"
            })

            if res.status_code != 200:
                print("Login failed:", res.status_code, res.data)
                raise Exception("Login failed in test setup")

            self.token = res.get_json()["token"]

            part = Inventory(name="Brake Pad", price=25.00)
            db.session.add(part)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_parts(self):
        res = self.client.get('/inventory/')
        self.assertEqual(res.status_code, 200)

    def test_create_part(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = self.client.post('/inventory/', json={"name": "Spark Plug", "price": 10.00}, headers=headers)
        self.assertEqual(res.status_code, 201)

