from flask import request, jsonify
from app.models import Customer, ServiceTicket
from app.extensions import db, limiter, cache
from . import user_bp
from .userSchemas import customer_schema, customers_schema, login_schema
from app.utils.util import encode_token, token_required
from app.blueprints.service_ticket.schemas import service_tickets_schema


@user_bp.route('', methods=['POST'])
def create_customer():
    name = request.json.get('name')
    email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')

    new_customer = Customer(name=name, email=email, phone=phone , password=password)
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


@user_bp.route('', methods=['GET'])
@limiter.limit("5 per minute")
@cache.cached(timeout=30)
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    paginated = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "customers": customers_schema.dump(paginated.items),
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page
    })


@user_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer), 200


@user_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_customer(user_id, id):
    if int(user_id) != id:
        return jsonify({'message': 'Unauthorized'}), 403

    customer = Customer.query.get_or_404(id)

    customer.name = request.json.get('name', customer.name)
    customer.email = request.json.get('email', customer.email)
    customer.phone = request.json.get('phone', customer.phone)
    customer.password = request.json.get('password', customer.password)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


@user_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(user_id, id):
    if int(user_id) != id:
        return jsonify({'message': 'Unauthorized'}), 403

    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted'}), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    customer = Customer.query.filter_by(email=data['email']).first()

    if not customer or customer.password != data['password']:
        return jsonify({"message": "Invalid credentials"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token})


@user_bp.route('/my-tickets', methods=['GET'])
@token_required
def my_tickets(user_id):
    tickets = ServiceTicket.query.filter_by(customer_id=user_id).all()
    return service_tickets_schema.jsonify(tickets)