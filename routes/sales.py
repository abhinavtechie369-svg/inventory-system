from flask import Blueprint, request, jsonify
from database import connect_db

sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/add_sale/<int:product_id>", methods=["POST"])
def add_sale(product_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    quantity_sold = data.get("quantity")

    if not isinstance(quantity_sold, int) or quantity_sold <= 0:
        return jsonify({"error": "Quantity sold must be positive integer"}), 400

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT price, quantity FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        connection.close()
        return jsonify({"error": "Product not found"}), 404

    price = product[0]
    available_quantity = product[1]

    if quantity_sold > available_quantity:
        connection.close()
        return jsonify({"error": "Not enough stock available"}), 400

    new_quantity = available_quantity - quantity_sold
    total_price = price * quantity_sold

    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))

    cursor.execute("""
        INSERT INTO sales (product_id, quantity_sold, total_price)
        VALUES (?, ?, ?)
    """, (product_id, quantity_sold, total_price))

    connection.commit()
    connection.close()

    return jsonify({"message": "Sale recorded successfully"})


@sales_bp.route("/sales", methods=["GET"])
def get_sales():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT sales.id, products.name, sales.quantity_sold,
               sales.total_price, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
    """)

    rows = cursor.fetchall()
    connection.close()

    sales = []

    for row in rows:
        sales.append({
            "sale_id": row[0],
            "product_name": row[1],
            "quantity_sold": row[2],
            "total_price": row[3],
            "sale_date": row[4]
        })

    return jsonify(sales)
