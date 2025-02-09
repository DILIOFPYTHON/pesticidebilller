import streamlit as st
import pandas as pd
from datetime import datetime
from utils.excel_data import get_excel_data
from utils.bill_manager import BillManager
from styles.styles import load_css

# Initialize session state
if 'current_items' not in st.session_state:
    st.session_state.current_items = []
if 'total_amount' not in st.session_state:
    st.session_state.total_amount = 0
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Load CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Initialize bill manager
bill_manager = BillManager()

def main():
    # Add dark mode toggle in navbar
    with st.container():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.title("🌿 Pesticide Billing System")
        with col2:
            if st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_mode_toggle"):
                st.session_state.dark_mode = True
                st.markdown("""
                    <style>
                        :root {
                            --background-color: #0e1117;
                            --secondary-background-color: #262730;
                            --text-color: #fafafa;
                        }
                    </style>
                """, unsafe_allow_html=True)
            else:
                st.session_state.dark_mode = False
                st.markdown("""
                    <style>
                        :root {
                            --background-color: #ffffff;
                            --secondary-background-color: #f0f2f6;
                            --text-color: #262730;
                        }
                    </style>
                """, unsafe_allow_html=True)

    # Sidebar for bill history
    with st.sidebar:
        st.header("📋 Saved Bills")
        view_saved_bills()

    # Main billing interface
    tab1, tab2 = st.tabs(["New Bill", "View Bills"])

    with tab1:
        create_new_bill()

    with tab2:
        view_all_bills()

def create_new_bill():
    # Date and customer input
    col1, col2 = st.columns(2)
    with col1:
        bill_date = st.date_input("Select Date", datetime.now())
    with col2:
        customer_name = st.text_input("Customer Name")

    # Load pesticide data from Excel
    products_df = get_excel_data()

    # Search and add items
    st.subheader("Add Items")
    search_term = st.text_input("🔍 Search Pesticide", key="search_box", placeholder="Type to search...")

    if search_term:
        filtered_products = products_df[
            products_df['Item Name'].str.lower().str.contains(search_term.lower(), na=False)
        ]

        if len(filtered_products) > 0:
            st.markdown("<div class='search-results'>", unsafe_allow_html=True)
            for _, product in filtered_products.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{product['Item Name']}**")
                    with col2:
                        st.write(f"₹{product['Price']:.2f}")
                    with col3:
                        if st.button("➕ Add", key=f"add_{product['Item Name']}"):
                            add_item(product['Item Name'], float(product['Price']))
        else:
            st.info("No matching items found")

    # Display current bill items
    if st.session_state.current_items:
        st.markdown("<div class='current-bill'>", unsafe_allow_html=True)
        st.subheader("Current Bill")

        for idx, item in enumerate(st.session_state.current_items):
            with st.container():
                col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1, 0.5, 0.5, 0.5, 0.5, 1.5])
                item_total = item['price'] * item['quantity']
                with col1:
                    st.write(f"**{item['name']}**")
                with col2:
                    st.write(f"₹{item['price']:.2f}")
                with col3:
                    if st.button("➖", key=f"minus_{idx}", help="Decrease quantity"):
                        update_quantity(idx, -1)
                with col4:
                    st.write(f"{item['quantity']}")
                with col5:
                    if st.button("➕", key=f"plus_{idx}", help="Increase quantity"):
                        update_quantity(idx, 1)
                with col6:
                    if st.button("🗑️", key=f"delete_{idx}", help="Remove item"):
                        delete_item(idx)
                with col7:
                    st.write(f"Total: ₹{item_total:.2f}")

        # Total amount
        st.markdown(
            f"""<div class='total-section'>
                Total Amount: ₹{st.session_state.total_amount:.2f}
            </div>""",
            unsafe_allow_html=True
        )

        # Save bill button
        if st.button("💾 Save Bill"):
            save_current_bill(customer_name, bill_date)

def add_item(name, price):
    # Check if item already exists
    for item in st.session_state.current_items:
        if item['name'] == name:
            item['quantity'] += 1
            calculate_total()
            st.rerun()
            return

    # Add new item with initial quantity of 1
    st.session_state.current_items.append({
        'name': name,
        'price': price,
        'quantity': 1
    })
    calculate_total()
    st.rerun()

def update_quantity(idx, change):
    item = st.session_state.current_items[idx]
    new_quantity = item['quantity'] + change

    if new_quantity > 0:
        item['quantity'] = new_quantity
        calculate_total()
        st.rerun()
    elif new_quantity == 0:
        delete_item(idx)

def delete_item(idx):
    st.session_state.current_items.pop(idx)
    calculate_total()
    st.rerun()

def calculate_total():
    st.session_state.total_amount = sum(
        item['price'] * item['quantity']
        for item in st.session_state.current_items
    )

def save_current_bill(customer_name, date):
    if not customer_name:
        st.error("Please enter customer name")
        return

    if not st.session_state.current_items:
        st.error("Please add items to the bill")
        return

    success = bill_manager.save_bill(
        customer_name,
        date.strftime("%Y-%m-%d"),
        st.session_state.current_items,
        st.session_state.total_amount
    )

    if success:
        st.success("Bill saved successfully!")
        # Clear current bill
        st.session_state.current_items = []
        st.session_state.total_amount = 0
        st.rerun()

def view_saved_bills():
    bills = bill_manager.get_all_bills()
    for bill in bills[-5:]:  # Show last 5 bills
        st.write(f"Bill #{bill['id']} - {bill['customer_name']}")
        st.write(f"Date: {bill['date']}")
        st.write(f"Amount: ₹{bill['total_amount']:.2f}")
        st.divider()

def view_all_bills():
    st.header("All Bills")

    # Add search box
    search_term = st.text_input("🔍 Search bills by customer name", key="bill_search", placeholder="Enter customer name...")

    bills = bill_manager.get_all_bills()

    # Filter bills if search term is provided
    if search_term:
        filtered_bills = [
            bill for bill in bills 
            if search_term.lower() in bill['customer_name'].lower()
        ]
    else:
        filtered_bills = bills

    if not filtered_bills:
        st.info("No bills found matching your search.")
        return

    for bill in filtered_bills:
        with st.expander(f"Bill #{bill['id']} - {bill['customer_name']} ({bill['date']})"):
            st.write(f"Customer: {bill['customer_name']}")
            st.write(f"Date: {bill['date']}")

            for item in bill['items']:
                item_total = item['price'] * item['quantity']
                st.write(f"- {item['name']}: {item['quantity']} x ₹{item['price']} = ₹{item_total:.2f}")

            st.write(f"Total Amount: ₹{bill['total_amount']:.2f}")

if __name__ == "__main__":
    main()