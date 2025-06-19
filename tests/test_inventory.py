import unittest
from app import create_app, db
from app.models import Customer, Inventory

class InventoryTests(unittest.TestCase):
 def setUp(self):
    self.app = create_app("TestingConfig")
    self.client = self.app.test_client()

    with self.app.app_context():
        db.create_all()

        # Create test customer
        self.email = "test@example.com"
        self.password = "testpass"
        customer = Customer(name="Test User", email=self.email, password=self.password)
        db.session.add(customer)
        db.session.commit()

        # Log in to get token
        res = self.client.post("/login", json={"email": self.email, "password": self.password})
        if res.status_code == 200 and "token" in res.get_json():
            self.token = res.get_json()["token"]
        else:
            raise Exception("Login failed in test setup")


    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_parts(self):
        res = self.client.get("/inventory/")
        self.assertEqual(res.status_code, 200)

    def test_create_part(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = self.client.post("/inventory/", json={
            "name": "Test Part",
            "price": 15.99
        }, headers=headers)
        self.assertEqual(res.status_code, 201)
