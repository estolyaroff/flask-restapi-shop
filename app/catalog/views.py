import json
from flask import request, jsonify, Blueprint, abort
from flask.views import MethodView
from app import db, app
from app.catalog.models import Product

catalog = Blueprint("catalog", __name__)


@catalog.route("/")
@catalog.route("/home")
def home():
    return "Welcome to the Catalog Home"


class ProductView(MethodView):
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
        name = request.form.get("name")
        price = request.form.get("price")
        product = Product(name, price)
        db.session.add(product)
        db.session.commit()
        return jsonify({product.id: {
            "name": product.name,
            "price": str(product.price),
        }})

    def delete(self, id):
        db.session.query(Product).filter(Product.id == id).delete()
        db.session.commit()
        return jsonify(f"Product {id} success del")


product_view = ProductView.as_view("product_view")
app.add_url_rule("/product/", view_func=product_view, methods=["GET", "POST"])
app.add_url_rule("/product/<int:id>", view_func=product_view, methods=["DELETE"])
app.add_url_rule("/product/<int:id>", view_func=product_view, methods=["GET"])
