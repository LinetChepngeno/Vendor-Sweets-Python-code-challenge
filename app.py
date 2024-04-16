#!/usr/bin/env python3
from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from faker import Faker
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_404_ERRORS'] = True
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Define route to retrieve sweets
@app.route('/sweets', methods=['GET'])
def get_sweets():
    sweets = Sweet.query.all()
    sweets_data = [{'id': sweet.id, 'name': sweet.name} for sweet in sweets]
    return jsonify(sweets_data)

# Define route to retrieve a specific sweet
@app.route('/sweets/<int:sweet_id>', methods=['GET'])
def get_sweet(sweet_id):
    sweet = db.session.get(Sweet, sweet_id)
    if sweet:
        sweet_data = {
            'id': sweet.id,
            'name': sweet.name
        }
        return jsonify(sweet_data)
    else:
        return jsonify({'error': 'Sweet not found'}), 404

# Define route to retrieve vendors
@app.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = Vendor.query.all()
    vendors_data = [{'id': vendor.id, 'name': vendor.name} for vendor in vendors]
    return jsonify(vendors_data)

# Define route to retrieve a specific vendor
@app.route('/vendors/<int:vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    vendor = db.session.get(Vendor, vendor_id)
    if vendor:
        vendor_data = {
            'id': vendor.id,
            'name': vendor.name,
            'vendor_sweets': [{'sweet_id': vs.sweet_id, 'price': vs.price} for vs in vendor.vendor_sweets]
        }
        return jsonify(vendor_data)
    else:
        return jsonify({'error': 'Vendor not found'}), 404

# Define route to create a new VendorSweet
@app.route('/vendor_sweets', methods=['POST'])
def create_vendor_sweet():
    data = request.get_json()
    price = data.get('price')
    vendor_id = data.get('vendor_id')
    sweet_id = data.get('sweet_id')

    if price is None or price < 0:
        return jsonify({'errors': 'Price must be a non-negative number'}), 400

    vendor = db.session.get(Vendor, vendor_id)
    sweet = db.session.get(Sweet, sweet_id)

    if not vendor or not sweet:
        return jsonify({'error': 'Invalid vendor or sweet ID'}), 400

    vendor_sweet = VendorSweet(price=price, vendor_id=vendor_id, sweet_id=sweet_id)
    db.session.add(vendor_sweet)
    db.session.commit()

    vendor_sweet_data = {
        'id': vendor_sweet.id,
        'price': vendor_sweet.price,
        'vendor_id': vendor_sweet.vendor_id,
        'sweet_id': vendor_sweet.sweet_id,
        'sweet': {'id': sweet.id, 'name': sweet.name},
        'vendor': {'id': vendor.id, 'name': vendor.name}
    }

    return jsonify(vendor_sweet_data), 201

# Define route to delete a VendorSweet
@app.route('/vendor_sweets/<int:vendor_sweet_id>', methods=['DELETE'])
def delete_vendor_sweet(vendor_sweet_id):
    vendor_sweet = db.session.get(VendorSweet, vendor_sweet_id)
    if vendor_sweet:
        db.session.delete(vendor_sweet)
        db.session.commit()
        return jsonify({}), 204
    else:
        return jsonify({'error': 'VendorSweet not found'}), 404

def test_400_for_validation_error(self):
    '''returns a 400 status code and error message if a POST request to /vendor_sweets fails.'''
    with app.app_context():
        fake = Faker()
        sweet = Sweet(name=fake.name())
        vendor = Vendor(name=fake.name())

        db.session.add(sweet)
        db.session.add(vendor)
        db.session.commit()

        response = app.test_client().post(
            '/vendor_sweets',
            json={
                "price": -1,
                "vendor_id": vendor.id,
                "sweet_id": sweet.id,
            }
        )
        assert response.status_code == 400
        assert response.json['errors'] == ["validation errors"]
        assert response.json['errors'] == 'Price must be a non-negative number'

@app.route('/')
def home(): 
    return '<h1>Code challenge</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)