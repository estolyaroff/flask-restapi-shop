from app import db
from datetime import datetime
from flask_bcrypt import (
    generate_password_hash,
    check_password_hash
)


category_product = db.Table(
    "category_product",
    db.Column(
        "category_id",
        db.Integer,
        db.ForeignKey('category.id', ondelete='CASCADE')
    ),
    db.Column(
        "product_id",
        db.Integer,
        db.ForeignKey('product.id', ondelete='CASCADE')
    ),
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.String(length=500))
    products = db.relationship(
        "Product",
        secondary=category_product,
        backref=db.backref(
            "categories",
            lazy="dynamic",
        ), passive_deletes=True
    )

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    description = db.Column(db.String(length=500))
    price = db.Column(db.DECIMAL(precision=10, scale=2, asdecimal=False))
    qty = db.Column(db.Integer)
    changelog = db.relationship("ChangeLog", back_populates="product", passive_deletes=True)

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Product {self.name}>"


class ChangeLog(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    value = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'))
    product = db.relationship("Product", back_populates="changelog")

    def __init__(self, value, product_id):
        self.value = value
        self.product = product_id


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<{self.id}:{self.email}>"

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)
