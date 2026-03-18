
from flask import Blueprint, request, jsonify
from database import connect_db

products_bp = Blueprint("products", __name__)


@products_bp.route("/add_product", methods=["POST"])
def add_product():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity")

    if not name or not isinstance(name, str):
        return jsonify({"error": "Product name must be valid"}), 400

    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"error": "Price must be positive"}), 400

    if not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Quantity must be non-negative"}), 400

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products (name, price, quantity)
        VALUES (?, ?, ?)
    """, (name, price, quantity))

    connection.commit()
    connection.close()

    return jsonify({"message": "Product added successfully"})


@products_bp.route("/products", methods=["GET"])
def get_products():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    connection.close()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "quantity": row[3],
            "created_at": row[4]
        })

    return jsonify(products)


@products_bp.route("/update_stock/<int:product_id>", methods=["PUT"])
def update_stock(product_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    additional_quantity = data.get("quantity")

    if not isinstance(additional_quantity, int) or additional_quantity <= 0:
        return jsonify({"error": "Quantity must be positive integer"}), 400

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        connection.close()
        return jsonify({"error": "Product not found"}), 404

    new_quantity = product[0] + additional_quantity

    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))

    connection.commit()
    connection.close()

    return jsonify({"message": "Stock updated successfully"})


@products_bp.route("/delete_product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        connection.close()
        return jsonify({"error": "Product not found"}), 404

    cursor.execute("DELETE FROM sales WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    connection.commit()
    connection.close()

    return jsonify({"message": "Product deleted successfully"})
@products_bp.route("/low_stock", methods=["GET"])
def low_stock():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products WHERE quantity <= 5")
    rows = cursor.fetchall()
    connection.close()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "quantity": row[3],
            "created_at": row[4]
        })

    return jsonify(products)
