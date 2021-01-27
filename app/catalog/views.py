from flask import jsonify, Blueprint, abort, request
from app import db, api, app
from app.catalog.models import Product, Category, User
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


@catalog.route("/")
@catalog.route("/home")
def home():
    return "Welcome to the Catalog Home"


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
        user = User.query.filter_by(email=body.get('email')).first()
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


#
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
                abort(404)
            res = {
                "id": product.id,
                "category": product.categories.first().name,
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "quantity": product.qty,
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
        product.categories.append(c)
        db.session.add(product)
        db.session.commit()
        return jsonify({product.id: {
            "name": product.name,
            "price": product.price,
            "category": category_id
        }})

    @jwt_required
    def put(self, id):
        args = parser.parse_args()
        name = args["name"]
        description = args["description"]
        category_id = args["category_id"]
        product = Product.query.filter_by(id=id).first()
        if product:
            product.name = name
            product.description = description
            product.categories.id = category_id
            db.session.commit()
            return jsonify(f"Product {id} success update")
        return jsonify(f"Product {id} not found")

    @jwt_required
    def delete(self, id):
        product = Product.query.filter_by(id=id)
        if product.first():
            product.delete()
            db.session.commit()
            return jsonify(f"Product {id} success del")
        return jsonify(f"Product {id} not found")


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
                abort(404)
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
        db.session.commit()
        return jsonify({category.id: {
            "name": category.name,
        }})

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
            return jsonify(f"Category {id} success update")
        return jsonify(f"Category {id} not found")

    @jwt_required
    def delete(self, id):
        category = Category.query.filter_by(id=id)
        if category.first():
            category.delete()
            db.session.commit()
            return jsonify(f"Category {id} success del")
        return jsonify(f"Category {id} not found")


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
