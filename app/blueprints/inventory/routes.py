from flask import request, jsonify
from app.extensions import db
from app.models import Inventory
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema
from app.utils.util import token_required


@inventory_bp.route('/', methods=['POST'])
@token_required
def create_inventory(user_id):
    data = request.get_json()
    part = Inventory(name=data['name'], price=data['price'])
    db.session.add(part)
    db.session.commit()
    return inventory_schema.jsonify(part), 201


@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    parts = Inventory.query.all()
    return inventories_schema.jsonify(parts)


@inventory_bp.route('/<int:id>', methods=['GET'])
def get_inventory_item(id):
    part = Inventory.query.get_or_404(id)
    return inventory_schema.jsonify(part)


@inventory_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_inventory(user_id, id):
    part = Inventory.query.get_or_404(id)
    data = request.get_json()
    part.name = data.get('name', part.name)
    part.price = data.get('price', part.price)
    db.session.commit()
    return inventory_schema.jsonify(part)


@inventory_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_inventory(user_id, id):
    part = Inventory.query.get_or_404(id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({'message': 'Inventory item deleted'})
