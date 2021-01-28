from flask import jsonify, Blueprint, request
from app import db, app
from app.catalog.models import Product, Category, User, ChangeLog
from flask_restful import Resource, reqparse
import textwrap
from flask_jwt_extended import create_access_token, jwt_required
import datetime


catalog = Blueprint("catalog", __name__)

parser = reqparse.RequestParser()
parser.add_argument("name", type=str)
parser.add_argument("description", type=str)
parser.add_argument("qty", type=int)
parser.add_argument("price", type=float)
parser.add_argument("category_id", type=int)


class SignupApi(Resource):
    def post(self):
        body = request.get_json()
        user = User(**body)
        user.hash_password()
        db.session.add(user)
        try:
            db.session.commit()
        except:
            return {'error': 'Email already exists'}, 401
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        return {'token': access_token}, 200


class LoginApi(Resource):
    def post(self):
        body = request.get_json()
        email = body.get("email")
        user = User.query.filter_by(email=email).first()
        authorized = user.check_password(body.get('password'))
        if not authorized:
            return {'error': 'Email or password invalid'}, 401
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        return {'token': access_token}, 200


# Output of the product catalog with a breakdown by pages
class CatalogView(Resource):
    def get(self, page=1):
        try:
            products = Product.query.paginate(page, 10).items
        except:
            products = Product.query.paginate(1, 10).items
        res = {}
        for product in products:
            if product.categories.first():
                category = product.categories.first().name
            else:
                category = None
            res[product.id] = {
                "name": product.name,
                "category": category,
                "price": str(product.price),
                "quantity": product.qty,
            }
        return jsonify(res)


class ProductView(Resource):
    @jwt_required
    def get(self, id=None, page=1):
        if not id:
            products = Product.query.paginate(page, 10).items
            res = {}
            for product in products:
                if product.categories.first():
                    category = product.categories.first().name
                else:
                    category = None
                res[product.id] = {
                    "category": category,
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price),
                    "quantity": product.qty,
                }
        else:
            product = Product.query.filter_by(id=id).first()
            if not product:
                return {"error": "Not found"}, 404
            log = []
            for l in product.changelog:
                log.append({str(l.date): l.value})
            res = {
                "id": product.id,
                "category": product.categories.first().name,
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "quantity": product.qty,
                "changelog": log
            }
        return jsonify(res)

    @jwt_required
    def post(self):
        args = parser.parse_args()
        name = args["name"]
        description = args["description"]
        price = args["price"]
        qty = args["qty"]
        category_id = args["category_id"]
        product = Product(name=name, description=description, price=price, qty=qty)
        c = Category.query.filter_by(id=category_id).first()
        if c is None:
            return {"error": "Category not found"}, 404
        l = ChangeLog(value=product.qty, product_id=product)
        product.changelog.append(l)
        product.categories.append(c)
        db.session.add(product)
        try:
            db.session.commit()
        except:
            return {"error": "Not modified"}, 304
        return {product.id: {product.name: product.description}}, 201


    @jwt_required
    def put(self, id):
        args = parser.parse_args()
        name = args["name"]
        description = args["description"]
        category_id = args["category_id"]
        qty = args["qty"]
        product = Product.query.filter_by(id=id).first()
        if product:
            product.name = name
            product.description = description
            product.categories.id = category_id
            product.qty = qty
            l = ChangeLog(value=product.qty, product_id=product)
            product.changelog.append(l)
            db.session.commit()
            return {'id': product.id}, 200

        return {"error": "Not found"}, 404

    @jwt_required
    def delete(self, id):
        product = Product.query.filter_by(id=id)
        if product.first():
            product.delete()
            db.session.commit()
            return {'id': id}, 200

        return {"error": "Not found"}, 404


class CategoryView(Resource):
    @jwt_required
    def get(self, id=None):
        if not id:
            categories = Category.query.all()
            res = {}
            for category in categories:
                description = textwrap.shorten(category.description, 100)
                res[category.id] = {
                    "id": category.id,
                    "name": category.name,
                    "description": description,
                    "products": len(category.products)
                }
        else:
            category = Category.query.filter_by(id=id).first()
            if not category:
                return {"error": "Not found"}, 404
            all_products = []
            p = category.products
            prod = {}
            for product in p:
                prod[product.id] = {
                    "name": product.name,
                    "price": str(product.price),
                }
                all_products.append(prod)
            res = {
                "id": category.id,
                "name": category.name,
                "products": all_products
            }

        return jsonify(res)

    @jwt_required
    def post(self):
        args = parser.parse_args()
        name = args["name"]
        description = args["description"]
        category = Category(name=name, description=description)
        db.session.add(category)
        try:
            db.session.commit()
        except:
            return {"error": "Not modified"}, 304
        return {category.id: {category.name: category.description}}, 201

    @jwt_required
    def put(self, id):
        args = parser.parse_args()
        name = args["name"]
        description = args["description"]
        category = Category.query.filter_by(id=id).first()
        if category:
            category.name = name
            category.description = description
            db.session.commit()
            return {'id': category.id}, 200
        return {"error": "Not found"}, 404

    @jwt_required
    def delete(self, id):
        category = Category.query.filter_by(id=id)
        if category.first():
            category.delete()
            db.session.commit()
            return {'id': id}, 200
        return {"error": "Not found"}, 404


# Auth
signup_view = SignupApi.as_view("signup")
app.add_url_rule("/api/signup/", view_func=signup_view, methods=["POST"])

# Login
login_view = LoginApi.as_view("login")
app.add_url_rule("/api/login/", view_func=login_view, methods=["POST"])

# Catalog
catalog_view = CatalogView.as_view("catalog_view")
app.add_url_rule("/api/catalog/", view_func=catalog_view, methods=["GET"])
app.add_url_rule("/api/catalog/<int:page>", view_func=catalog_view, methods=["GET"])

# Products
product_view = ProductView.as_view("product_view")
app.add_url_rule("/api/product/", view_func=product_view, methods=["GET", "POST"])
app.add_url_rule("/api/product/<int:id>", view_func=product_view, methods=["DELETE", "PUT", "GET"])

# Category
category_view = CategoryView.as_view("category_view")
app.add_url_rule("/api/category/", view_func=category_view, methods=["GET", "POST"])
app.add_url_rule("/api/category/<int:id>", view_func=category_view, methods=["GET", "DELETE", "PUT"])
