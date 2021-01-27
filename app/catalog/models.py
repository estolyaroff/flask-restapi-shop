from app import db
from datetime import datetime


# class Product(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))
#     price = db.Column(db.Float(asdecimal=True))
#
#     def __init__(self, name, price):
#         self.name = name
#         self.price = price
#
#     def __repr__(self):
#         return f"<Product {self.id}>"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.String(length=500))

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Category %r>' % self.name


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    description = db.Column(db.String(length=500))
    image_urls = db.Column(db.Text, nullable=True)
    price = db.Column(db.DECIMAL(precision=10, scale=2, asdecimal=False))
    qty = db.Column(db.Integer)
    # db.relationship(Category)

    def __init__(self, name, price, qty, description=None, image_urls=None):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
        self.image_urls = image_urls

    def __repr__(self):
        return '<Category %r>' % self.name


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<{self.id}:{self.email}>"

    # def hash_password(self):
    #     self.password = generate_password_hash(self.password).decode('utf8')
    #
    # def check_password(self, password):
    #     return check_password_hash(self.password, password)