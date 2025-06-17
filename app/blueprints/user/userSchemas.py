from app.extensions import ma
from app.models import Customer
from marshmallow import Schema, fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
  

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()  