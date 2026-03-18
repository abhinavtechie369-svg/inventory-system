import streamlit as st # type: ignore
import requests

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide"
)

BASE_URL = "http://127.0.0.1:5000"

# -------------------------------
# Session State Initialization
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

USERNAME = "admin"
PASSWORD = "1234"

# -------------------------------
# Login Page
# -------------------------------
if not st.session_state["logged_in"]:

    st.title("🔐 Login to Inventory System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username == USERNAME and password == PASSWORD:
            st.session_state["logged_in"] = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# -------------------------------
# Dashboard Header
# -------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>
        📦 Inventory Management Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Daily Overview Metrics
# -------------------------------
response = requests.get(f"{BASE_URL}/report/daily")
if response.status_code == 200:
    report = response.json()

    col1, col2, col3 = st.columns(3)
    col1.metric("Today's Revenue (₹)", report["total_revenue_today"])
    col2.metric("Transactions Today", report["total_transactions_today"])
    col3.metric("Items Sold Today", report["total_items_sold_today"])

st.divider()

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", [
    "View Products",
    "Add Product",
    "Record Sale",
    "Sales History",
    "Daily Report",
    "Monthly Report",
    "Low Stock"
])

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

# -------------------------------
# View Products
# -------------------------------
if page == "View Products":
    st.subheader("📋 Product List")

    response = requests.get(f"{BASE_URL}/products")

    if response.status_code == 200:
        products = response.json()

        if products:
            st.dataframe(products, use_container_width=True)
        else:
            st.info("No products available.")
    else:
        st.error("Failed to fetch products.")

# -------------------------------
# Add Product
# -------------------------------
elif page == "Add Product":
    st.subheader("➕ Add New Product")

    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, step=1.0)
    quantity = st.number_input("Quantity", min_value=0, step=1)

    if st.button("Add Product", use_container_width=True):
        data = {
            "name": name,
            "price": price,
            "quantity": quantity
        }

        response = requests.post(f"{BASE_URL}/add_product", json=data)

        if response.status_code == 200:
            st.success("Product added successfully!")
        else:
            st.error(response.json().get("error", "Something went wrong"))

# -------------------------------
# Record Sale
# -------------------------------
elif page == "Record Sale":
    st.subheader("💰 Record Sale")

    response = requests.get(f"{BASE_URL}/products")

    if response.status_code == 200:
        products = response.json()

        if products:
            product_options = {
                f"{p['name']} (Stock: {p['quantity']})": p['id']
                for p in products
            }

            selected_product = st.selectbox("Select Product", list(product_options.keys()))
            quantity = st.number_input("Quantity Sold", min_value=1, step=1)

            if st.button("Record Sale", use_container_width=True):
                product_id = product_options[selected_product]

                data = {"quantity": quantity}

                sale_response = requests.post(
                    f"{BASE_URL}/add_sale/{product_id}",
                    json=data
                )

                if sale_response.status_code == 200:
                    st.success("Sale recorded successfully!")
                else:
                    st.error(sale_response.json().get("error", "Error recording sale"))

        else:
            st.info("No products available to sell.")
    else:
        st.error("Failed to fetch products.")

# -------------------------------
# Sales History
# -------------------------------
elif page == "Sales History":
    st.subheader("📜 Sales History")

    response = requests.get(f"{BASE_URL}/sales")

    if response.status_code == 200:
        sales = response.json()

        if sales:
            st.dataframe(sales, use_container_width=True)
        else:
            st.info("No sales recorded yet.")
    else:
        st.error("Failed to fetch sales history.")

# -------------------------------
# Daily Report
# -------------------------------
elif page == "Daily Report":
    st.subheader("📊 Daily Sales Report")

    response = requests.get(f"{BASE_URL}/report/daily")

    if response.status_code == 200:
        report = response.json()

        col1, col2, col3 = st.columns(3)

        col1.metric("Transactions Today", report["total_transactions_today"])
        col2.metric("Items Sold Today", report["total_items_sold_today"])
        col3.metric("Revenue Today (₹)", report["total_revenue_today"])

    else:
        st.error("Failed to fetch daily report.")

# -------------------------------
# Monthly Report
# -------------------------------
elif page == "Monthly Report":
    st.subheader("📅 Monthly Sales Report")

    response = requests.get(f"{BASE_URL}/report/monthly")

    if response.status_code == 200:
        report = response.json()

        col1, col2, col3 = st.columns(3)

        col1.metric("Transactions This Month", report["total_transactions_this_month"])
        col2.metric("Items Sold This Month", report["total_items_sold_this_month"])
        col3.metric("Revenue This Month (₹)", report["total_revenue_this_month"])

    else:
        st.error("Failed to fetch monthly report.")

# -------------------------------
# Low Stock
# -------------------------------
elif page == "Low Stock":
    st.subheader("⚠️ Low Stock Alert")

    response = requests.get(f"{BASE_URL}/low_stock")

    if response.status_code == 200:
        low_stock_products = response.json()

        if low_stock_products:
            st.warning("Some products are running low!")

            for product in low_stock_products:
                st.error(
                    f"🚨 {product['name']} — Only {product['quantity']} left in stock!"
                )
        else:
            st.success("All products are sufficiently stocked.")

    else:
        st.error("Failed to fetch low stock data.")
