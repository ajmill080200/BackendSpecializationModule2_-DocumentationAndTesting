import unittest
from app import create_app, db
from app.models import Customer, Mechanic, ServiceTicket

class TicketTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.customer = Customer(name="Janey Doe", email="jdoe@myemail.com", password="testpassword")
            self.mechanic = Mechanic(name="Johnny Mechanic", specialty="Engines")
            self.ticket = ServiceTicket(service_desc="Check engine", customer=self.customer)
            db.session.add_all([self.customer, self.mechanic, self.ticket])
            db.session.commit()
            self.ticket_id = self.ticket.id
            self.mechanic_id = self.mechanic.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_tickets(self):
        res = self.client.get('/service-tickets/')
        self.assertEqual(res.status_code, 200)

    def test_get_ticket_by_id(self):
        res = self.client.get(f'/service-tickets/{self.ticket_id}')
        self.assertEqual(res.status_code, 200)

    def test_assign_mechanic(self):
        res = self.client.put(f'/service-tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}')
        self.assertEqual(res.status_code, 200)
