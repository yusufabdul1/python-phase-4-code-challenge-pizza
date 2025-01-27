#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Route: GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([
        {
            "id": r.id,
            "name": r.name,
            "address": r.address
        }
        for r in restaurants
    ]), 200

# Route: GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            }
            for rp in restaurant.restaurant_pizzas
        ]
    }), 200

# Route: DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return "", 204

# Route: GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "ingredients": p.ingredients
        }
        for p in pizzas
    ]), 200

# Route: POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Validation: Price between 1 and 30
    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"errors": ["validation errors"]}), 400

    restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify({
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "pizza_id": restaurant_pizza.pizza_id,
        "restaurant_id": restaurant_pizza.restaurant_id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
    }), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)