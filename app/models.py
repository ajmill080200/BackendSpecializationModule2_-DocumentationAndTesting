from app.extensions import db

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    password = db.Column(db.String(128), nullable=False)

    service_tickets = db.relationship('ServiceTicket', backref='customer', cascade="all, delete-orphan")


class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    salary = db.Column(db.Float)
    specialty = db.Column(db.String(100))

    tickets = db.relationship('ServiceMechanic', backref='mechanic', cascade="all, delete-orphan")


class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    id = db.Column(db.Integer, primary_key=True)
    VIN = db.Column(db.String(50))
    service_date = db.Column(db.String(50))
    service_desc = db.Column(db.String(255))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

    mechanics = db.relationship('ServiceMechanic', backref='ticket', cascade="all, delete-orphan")


class ServiceMechanic(db.Model):
    __tablename__ = 'service_mechanics'
    ticket_id = db.Column(db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)


class ServiceInventory(db.Model):
    __tablename__ = 'service_inventory'
    ticket_id = db.Column(db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    ticket = db.relationship("ServiceTicket", backref="service_parts")
    inventory = db.relationship("Inventory", backref="used_in_tickets")


class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
