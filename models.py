from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Sweet(db.Model, SerializerMixin):
    __tablename__ = 'sweets'

    # Add serialization
    serialize_rules = ('-vendor_sweets.sweet',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationship
    vendor_sweets = db.relationship(
            'VendorSweet', back_populates='sweet', cascade='all, delete-orphan')
    
    vendors = association_proxy('vendor_sweets', 'vendor',
            creator=lambda vendor_obj: VendorSweet(vendor=vendor_obj))
    
    def __repr__(self):
        return f'<Sweet {self.id}>'


class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'

    # Add serialization
    serialize_rules = ('-vendor_sweets.vendor',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationship
    vendor_sweets = db.relationship(
            'VendorSweet', back_populates='vendor', cascade='all, delete-orphan')
    
    sweets = association_proxy('vendor_sweets', 'sweet',
            creator=lambda sweet_obj: VendorSweet(sweet=sweet_obj))
    
    def __repr__(self):
        return f'<Vendor {self.id}>'


class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = 'vendor_sweets'

    # Add serialization
    serialize_rules = ('-sweet.vendor_sweets', '-vendor.vendor_sweets',)

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    sweet_id = db.Column(db.Integer, db.ForeignKey('sweets.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))  
    
      # Add relationships
    sweet = db.relationship('Sweet', back_populates='vendor_sweets')
    vendor = db.relationship('Vendor', back_populates='vendor_sweets')
    
    # Add validation
    @validates('price')
    def validate_price(self, key, price):
        if not isinstance(price, int) or price < 0:
            raise ValueError('Price must be a positive integer.')
        return price
    def __repr__(self):
        return f'<VendorSweet {self.id}>'
