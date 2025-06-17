from flask import request, jsonify
from app.extensions import db, limiter, cache
from app.models import ServiceTicket, Mechanic, ServiceMechanic, Inventory
from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema
from app.utils.util import token_required


@service_ticket_bp.route('/', methods=['POST'])
def create_ticket():
    data = request.json
    ticket = ServiceTicket(**data)
    db.session.add(ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 201


@service_ticket_bp.route('/<int:id>', methods=['GET'])
def get_ticket_by_id(id):
    ticket = ServiceTicket.query.get_or_404(id)
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_ticket(user_id, id):
    ticket = ServiceTicket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket deleted'}), 200


@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    already_assigned = ServiceMechanic.query.filter_by(ticket_id=ticket.id, mechanic_id=mechanic.id).first()
    if not already_assigned:
        assignment = ServiceMechanic(ticket_id=ticket.id, mechanic_id=mechanic.id)
        db.session.add(assignment)
        db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    ticket.mechanics = [m for m in ticket.mechanics if m.mechanic_id != mechanic.id]
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route('/', methods=['GET'])
@limiter.limit("3 per minute") #limits 3 per minute
@cache.cached(timeout=45) #stores data in cache for 45 seconds
def get_tickets():
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200


@service_ticket_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@token_required
def edit_ticket_mechanics(user_id, ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json()

    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    ticket.mechanics = [
        m for m in ticket.mechanics if m.mechanic_id not in remove_ids
    ]

    for mechanic_id in add_ids:
        mechanic = Mechanic.query.get(mechanic_id)
        if mechanic:
            exists = any(m.mechanic_id == mechanic.id for m in ticket.mechanics)
            if not exists:
                ticket.mechanics.append(ServiceMechanic(mechanic_id=mechanic.id))

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route('/<int:ticket_id>/add-part/<int:inventory_id>', methods=['PUT'])
@token_required
def add_part_to_ticket(user_id, ticket_id, inventory_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    part = Inventory.query.get_or_404(inventory_id)

    existing = ServiceInventory.query.filter_by(ticket_id=ticket.id, inventory_id=part.id).first()
    if existing:
        existing.quantity += 1
    else:
        link = ServiceInventory(ticket_id=ticket.id, inventory_id=part.id, quantity=1)
        db.session.add(link)

    db.session.commit()
    return jsonify({'message': f'Part {part.name} added to ticket {ticket.id}'})
