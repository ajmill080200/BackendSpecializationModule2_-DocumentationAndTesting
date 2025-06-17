from flask import request, jsonify
from sqlalchemy import func
from app.extensions import db, limiter, cache
from app.models import Mechanic, ServiceMechanic
from . import mechanic_bp
from .schemas import mechanic_schema, mechanics_schema
from app.utils.util import token_required


@mechanic_bp.route('/', methods=['POST'])
def create_mechanic():
    data = request.json
    mechanic = Mechanic(**data)
    db.session.add(mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 201


@mechanic_bp.route('/', methods=['GET'])
@limiter.limit("10 per minute") #limit 10 per minute
@cache.cached(timeout=60) #stores data in cache for 60 seconds
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route('/<int:id>', methods=['GET'])
def get_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    return mechanic_schema.jsonify(mechanic), 200


@mechanic_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    for field in ['name', 'email', 'phone', 'salary', 'specialty']:
        if field in request.json:
            setattr(mechanic, field, request.json[field])
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanic_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': 'Mechanic deleted'}), 200


@mechanic_bp.route('/most-active', methods=['GET'])
def most_active_mechanics():
    results = (
        db.session.query(
            Mechanic,
            func.count(ServiceMechanic.ticket_id).label('ticket_count')
        )
        .join(ServiceMechanic, Mechanic.id == ServiceMechanic.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(ServiceMechanic.ticket_id).desc())
        .all()
    )

    data = [
        {
            "id": mech.id,
            "name": mech.name,
            "email": mech.email,
            "ticket_count": count,
            "specialty": mech.specialty
        }
        for mech, count in results
    ]
    return jsonify(data)

