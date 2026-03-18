from flask import Flask
from database import create_tables
from routes.products import products_bp
from routes.sales import sales_bp
from routes.reports import reports_bp

app = Flask(__name__)

app.register_blueprint(products_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(reports_bp)


@app.route("/")
def home():
    return "Inventory System Running"


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
