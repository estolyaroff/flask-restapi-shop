from flask import jsonify, Blueprint, abort
from app import db, api, app
from app.catalog.models import Product
from flask_restful import Resource, reqparse

catalog = Blueprint("catalog", __name__)


parser = reqparse.RequestParser()
parser.add_argument("name", type=str)
parser.add_argument("description", type=str)
parser.add_argument("qty", type=int)
parser.add_argument("price", type=float)


@catalog.route("/")
@catalog.route("/home")
def home():
    return "Welcome to the Catalog Home"


class ProductView(Resource):
    def get(self, id=None, page=1):
        if not id:
            products = Product.query.paginate(page, 10).items
            res = {}
            for product in products:
                res[product.id] = {
                    "id": product.id,
                    "name": product.name,
                    "price": str(product.price),
                }
        else:
            product = Product.query.filter_by(id=id).first()
            if not product:
                abort(404)
            res = {
                "id": product.id,
                "name": product.name,
                "price": str(product.price),
            }
        return jsonify(res)

    def post(self):
        args = parser.parse_args()
        name = args["name"]
        description = args["description"]
        price = args["price"]
        qty = args["qty"]
        product = Product(name=name, description=description, price=price, qty=qty)
        db.session.add(product)
        db.session.commit()
        return jsonify({product.id: {
            "name": product.name,
            "price": product.price,
        }})

    def delete(self, id):
        db.session.query(Product).filter(Product.id == id).delete()
        db.session.commit()
        return jsonify(f"Product {id} success del")


product_view = ProductView.as_view("product_view")
app.add_url_rule("/api/product/", view_func=product_view, methods=["GET", "POST"])
app.add_url_rule("/api/product/<int:id>", view_func=product_view, methods=["DELETE"])
app.add_url_rule("/api/product/<int:page>", view_func=product_view, methods=["GET"])
