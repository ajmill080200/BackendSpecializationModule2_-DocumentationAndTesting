import unittest
from app import create_app, db
from app.models import Mechanic

class MechanicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.mechanic = Mechanic(name="Billy Bob Biggs", specialty="Tires")
            db.session.add(self.mechanic)
            db.session.commit()
            self.mechanic_id = self.mechanic.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_mechanics(self):
        res = self.client.get('/mechanics/')
        self.assertEqual(res.status_code, 200)

    def test_get_mechanic_by_id(self):
        res = self.client.get(f'/mechanics/{self.mechanic.id}')
        self.assertEqual(res.status_code, 200)
