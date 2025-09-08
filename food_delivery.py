import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import random
import csv

# ---------------------- Sample Menu Data ----------------------
menu_data = {
    "Domino's": {
        "Pizza": {"Margherita": 250, "Farmhouse": 350, "Peppy Paneer": 300},
        "Sides": {"Garlic Bread": 120, "Cheesy Dip": 60}
    },
    "Cafe Coffee Day": {
        "Coffee": {"Espresso": 80, "Cappuccino": 120, "Latte": 150},
        "Snacks": {"Sandwich": 100, "Brownie": 90}
    },
    "Burger King": {
        "Burgers": {"Veg Whopper": 150, "Paneer King": 180, "Crispy Veg": 120},
        "Fries": {"Regular Fries": 70, "Peri Peri Fries": 90}
    }
}

# ---------------------- Data Structures ----------------------
order_queue = deque()
order_history = []
total_revenue = 0
cart = {}

# ---------------------- Functions ----------------------
def update_categories(*args):
    restaurant = restaurant_var.get()
    if restaurant in menu_data:
        category_menu['menu'].delete(0, 'end')
        for category in menu_data[restaurant]:
            category_menu['menu'].add_command(label=category, command=tk._setit(category_var, category))
        first_cat = list(menu_data[restaurant].keys())[0]
        category_var.set(first_cat)
        update_items()

def update_items(*args):
    items_list.delete(*items_list.get_children())
    restaurant = restaurant_var.get()
    category = category_var.get()
    search_term = search_var.get().lower()

    if restaurant in menu_data and category in menu_data[restaurant]:
        items = list(menu_data[restaurant][category].items())

        if sort_var.get() == "Low to High":
            items.sort(key=lambda x: x[1])
        elif sort_var.get() == "High to Low":
            items.sort(key=lambda x: x[1], reverse=True)

        for item, price in items:
            if search_term in item.lower():
                items_list.insert("", "end", values=(item, f"₹{price}"))

def add_to_cart():
    selected = items_list.selection()
    if not selected:
        messagebox.showerror("Error", "Select an item first")
        return
    item_name, price_str = items_list.item(selected[0])['values']
    price = int(price_str.replace("₹", ""))
    qty = qty_var.get()
    if qty <= 0:
        messagebox.showerror("Error", "Quantity must be at least 1")
        return
    if item_name in cart:
        cart[item_name]['qty'] += qty
    else:
        cart[item_name] = {"price": price, "qty": qty}
    update_cart_display()

def update_cart_display():
    cart_list.delete(*cart_list.get_children())
    for item, details in cart.items():
        cart_list.insert("", "end", values=(item, details['qty'], f"₹{details['price']}"))

def view_bill():
    if not cart:
        messagebox.showinfo("Cart Empty", "No items in the cart.")
        return
    bill_text = ""
    subtotal = 0
    for item, details in cart.items():
        line_total = details['price'] * details['qty']
        bill_text += f"{item} x {details['qty']} = ₹{line_total}\n"
        subtotal += line_total
    gst = subtotal * 0.05
    total = subtotal + gst
    bill_text += f"\nSubtotal: ₹{subtotal}\nGST (5%): ₹{gst:.2f}\nTotal: ₹{total:.2f}"
    messagebox.showinfo("Bill", bill_text)

def place_order():
    global total_revenue
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return
    subtotal = sum(details['price'] * details['qty'] for details in cart.values())
    gst = subtotal * 0.05
    total = subtotal + gst
    order_id = f"ORD{random.randint(1000,9999)}"
    order_queue.append({"id": order_id, "items": cart.copy(), "total": total})
    total_revenue += total
    cart.clear()
    update_cart_display()
    update_revenue_label()
    messagebox.showinfo("Order Placed", f"Order {order_id} placed successfully.\nTotal: ₹{total:.2f}")

def process_order():
    if not order_queue:
        messagebox.showinfo("No Orders", "No pending orders to process.")
        return
    current_order = order_queue.popleft()
    track_order_status(current_order)

def track_order_status(order):
    status_list = ["Preparing", "On the way", "Delivered"]
    def update_status(index=0):
        if index < len(status_list):
            status_label.config(text=f"Order {order['id']} Status: {status_list[index]}")
            root.after(2000, update_status, index+1)
        else:
            order_history.append(order)
            save_history_to_csv()
            status_label.config(text=f"Order {order['id']} Delivered")
    update_status()

def view_history():
    if not order_history:
        messagebox.showinfo("History Empty", "No orders delivered yet.")
        return
    history_text = ""
    for order in reversed(order_history):
        history_text += f"{order['id']} - ₹{order['total']:.2f}\n"
    messagebox.showinfo("Order History", history_text)

def save_history_to_csv():
    with open("order_history.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Order ID", "Total"])
        for order in order_history:
            writer.writerow([order['id'], f"₹{order['total']:.2f}"])

def update_revenue_label():
    revenue_label.config(text=f"Total Revenue: ₹{total_revenue:.2f}")

# ---------------------- GUI ----------------------
root = tk.Tk()
root.title("Online Food Delivery System")
root.state("zoomed")

# Layout frames
left_frame = tk.Frame(root, padx=10, pady=10)
left_frame.pack(side="left", fill="both", expand=True)

right_frame = tk.Frame(root, padx=10, pady=10)
right_frame.pack(side="right", fill="y")

# Revenue label
revenue_label = tk.Label(left_frame, text=f"Total Revenue: ₹{total_revenue:.2f}", font=("Arial", 14, "bold"))
revenue_label.pack(pady=5)

# Restaurant selection
restaurant_var = tk.StringVar()
restaurant_dropdown = tk.OptionMenu(left_frame, restaurant_var, *menu_data.keys())
restaurant_var.set("Select Restaurant")
restaurant_dropdown.config(font=("Arial", 12))
restaurant_dropdown.pack(pady=5, fill="x")
restaurant_var.trace("w", update_categories)

# Category selection
category_var = tk.StringVar()
category_menu = tk.OptionMenu(left_frame, category_var, "")
category_var.set("Select Category")
category_menu.config(font=("Arial", 12))
category_menu.pack(pady=5, fill="x")
category_var.trace("w", update_items)

# Search
search_var = tk.StringVar()
tk.Entry(left_frame, textvariable=search_var, font=("Arial", 12), width=25).pack(pady=5)
search_var.trace("w", update_items)

# Sort
sort_var = tk.StringVar()
sort_dropdown = tk.OptionMenu(left_frame, sort_var, "None", "Low to High", "High to Low")
sort_var.set("None")
sort_dropdown.config(font=("Arial", 12))
sort_dropdown.pack(pady=5)
sort_var.trace("w", update_items)

# Items list
columns = ("Item", "Price")
items_list = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
items_list.heading("Item", text="Item")
items_list.heading("Price", text="Price")
items_list.column("Item", width=250)
items_list.column("Price", width=100)
items_list.pack(pady=5, fill="both", expand=True)

# Quantity
qty_var = tk.IntVar(value=1)
tk.Spinbox(left_frame, from_=1, to=10, textvariable=qty_var, font=("Arial", 12), width=5).pack(pady=5)

# Add to cart button
tk.Button(left_frame, text="Add to Cart", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=add_to_cart).pack(pady=5)

# ---------------------- Right Panel ----------------------
tk.Label(right_frame, text="Your Cart", font=("Arial", 14, "bold")).pack(pady=5)

cart_list = ttk.Treeview(right_frame, columns=("Item", "Qty", "Price"), show="headings", height=10)
cart_list.heading("Item", text="Item")
cart_list.heading("Qty", text="Qty")
cart_list.heading("Price", text="Price")
cart_list.pack(pady=5)

tk.Button(right_frame, text="View Bill", font=("Arial", 12), command=view_bill).pack(pady=5, fill="x")
tk.Button(right_frame, text="Place Order", font=("Arial", 12), command=place_order).pack(pady=5, fill="x")
tk.Button(right_frame, text="Process Next Order", font=("Arial", 12), command=process_order).pack(pady=5, fill="x")
tk.Button(right_frame, text="View Order History", font=("Arial", 12), command=view_history).pack(pady=5, fill="x")

status_label = tk.Label(right_frame, text="", font=("Arial", 12))
status_label.pack(pady=10)

root.mainloop()

