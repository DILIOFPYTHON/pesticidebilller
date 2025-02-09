import json
import os
from datetime import datetime
import streamlit as st

class BillManager:
    def __init__(self):
        self.bills_file = "data/bills.json"
        self.ensure_bills_file_exists()

    def ensure_bills_file_exists(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.bills_file):
            with open(self.bills_file, "w") as f:
                json.dump([], f)

    def save_bill(self, customer_name, date, items, total_amount):
        try:
            with open(self.bills_file, "r") as f:
                bills = json.load(f)

            bill_data = {
                "id": len(bills) + 1,
                "customer_name": customer_name,
                "date": date,
                "items": items,
                "total_amount": total_amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            bills.append(bill_data)

            with open(self.bills_file, "w") as f:
                json.dump(bills, f, indent=4)

            return True
        except Exception as e:
            st.error(f"Error saving bill: {str(e)}")
            return False

    def get_all_bills(self):
        try:
            with open(self.bills_file, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error reading bills: {str(e)}")
            return []