from flask import Blueprint, jsonify
from database import connect_db

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/report/daily", methods=["GET"])
def daily_report():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*),
            SUM(quantity_sold),
            SUM(total_price)
        FROM sales
        WHERE DATE(sale_date) = DATE('now')
    """)

    result = cursor.fetchone()
    connection.close()

    report = {
        "total_transactions_today": result[0] or 0,
        "total_items_sold_today": result[1] or 0,
        "total_revenue_today": result[2] or 0
    }

    return jsonify(report)


@reports_bp.route("/report/monthly", methods=["GET"])
def monthly_report():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*),
            SUM(quantity_sold),
            SUM(total_price)
        FROM sales
        WHERE strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now')
    """)

    result = cursor.fetchone()
    connection.close()

    report = {
        "total_transactions_this_month": result[0] or 0,
        "total_items_sold_this_month": result[1] or 0,
        "total_revenue_this_month": result[2] or 0
    }

    return jsonify(report)
