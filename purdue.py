import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from prices import target_prices

# Connect to SQLite database
conn = sqlite3.connect('roomshare.db')
cursor = conn.cursor()

# Function to create tables
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
    conn.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        roommate TEXT,
                        room_name TEXT,
                        amount REAL,
                        item TEXT
                    )''')
    conn.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        owner TEXT,
                        roommate TEXT,
                        room_name TEXT
                    )''')
    conn.commit()

create_tables()

# Initialize current user
current_user = None

# Function to show welcome screen
def show_welcome():
    welcome_screen = tk.Tk()
    welcome_screen.title("Purdue RoomShare")
    welcome_screen.configure(bg="#F0F8FF")
    welcome_screen.geometry("1000x1000")

    tk.Label(welcome_screen, text="Welcome to RoomShare, Boiler!", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=40)

    tk.Button(welcome_screen, text="Log In With Your RoomShare Account", command=lambda: [welcome_screen.destroy(), show_login()],
              bg="#5F9EA0", fg="white", font=("Garamond", 14), width=60).pack(pady=30)
    tk.Button(welcome_screen, text="Sign Up", command=lambda: [welcome_screen.destroy(), show_signup()],
              bg="#20B2AA", fg="white", font=("Garamond", 14), width=60).pack(pady=30)

    welcome_screen.mainloop()
    


# Function to show signup screen
def show_signup():
    signup_screen = tk.Tk()
    signup_screen.title("Sign Up")
    signup_screen.configure(bg="#F0F8FF")
    signup_screen.geometry("1000x1000")

    tk.Label(signup_screen, text="Create an Account", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=10)

    tk.Label(signup_screen, text="Username", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    username_entry = tk.Entry(signup_screen)
    username_entry.pack(pady=5)

    tk.Label(signup_screen, text="Password", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    password_entry = tk.Entry(signup_screen, show="*")
    password_entry.pack(pady=5)

    tk.Label(signup_screen, text="Confirm Password", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    confirm_password_entry = tk.Entry(signup_screen, show="*")
    confirm_password_entry.pack(pady=5)

    def handle_signup():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully! Please log in.")
            signup_screen.destroy()
            show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")

    tk.Button(signup_screen, text="Sign Up", command=handle_signup,
              bg="#5F9EA0", fg="white", font=("Garamond", 14)).pack(pady=10)

    signup_screen.mainloop()

# Function to show login screen
def show_login(previous_window=None):
    if previous_window:
        previous_window.destroy()
        
    login_screen = tk.Tk()
    login_screen.title("Log In")
    login_screen.configure(bg="#F0F8FF")
    login_screen.geometry("1000x1000")

    tk.Label(login_screen, text="Log In", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=10)

    tk.Label(login_screen, text="Username", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    username_entry = tk.Entry(login_screen)
    username_entry.pack(pady=5)

    tk.Label(login_screen, text="Password", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    password_entry = tk.Entry(login_screen, show="*")
    password_entry.pack(pady=5)

    def handle_login():
        global current_user
        username = username_entry.get()
        password = password_entry.get()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            current_user = username
            messagebox.showinfo("Success", "Logged in successfully!")
            login_screen.destroy()
            show_user_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    tk.Button(login_screen, text="Log In", command=handle_login,
              bg="#20B2AA", fg="white", font=("Garamond", 14)).pack(pady=10)

    login_screen.mainloop()

# Function to show user dashboard
def show_user_dashboard(previous_window=None):
    if previous_window:
        previous_window.destroy()
    dashboard_screen = tk.Tk()
    dashboard_screen.title("User Dashboard")
    dashboard_screen.configure(bg="#F0F8FF")
    dashboard_screen.geometry("1000x1000")

    tk.Label(dashboard_screen, text=f"Welcome, {current_user}!", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=20)

    tk.Button(dashboard_screen, text="View Transactions", command=view_transactions,
              bg="#5F9EA0", fg="white", font=("Garamond", 14), width=20).pack(pady=20)
    tk.Button(dashboard_screen, text="Add Transactions", command=add_transaction,
              bg="#20B2AA", fg="white", font=("Garamond", 14), width=20).pack(pady=20)
    tk.Button(dashboard_screen, text="Create Room", command=create_room,
              bg="#5F9EA0", fg="white", font=("Garamond", 14), width=20).pack(pady=30)
    tk.Button(dashboard_screen, text="Log Out", command=lambda: [dashboard_screen.destroy(), show_welcome()],
              bg="#FF4500", fg="white", font=("Garamond", 14), width=20).pack(pady=30)

    dashboard_screen.mainloop()

# Function to view transactions
def view_transactions(previous_window=None):
    if previous_window:
        previous_window.destroy()
    transactions_screen = tk.Tk()
    transactions_screen.title("View Transactions")
    transactions_screen.configure(bg="#F0F8FF")
    transactions_screen.geometry("1000x1000")

    cursor.execute("SELECT * FROM transactions WHERE username=? OR roommate=?", (current_user, current_user))
    transactions = cursor.fetchall()

    if transactions:
        tk.Label(transactions_screen, text="Transactions:", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=10)

        for transaction in transactions:
            tk.Label(transactions_screen, text=f"{transaction[1]} is owed ${transaction[4]} for {transaction[5]} by {transaction[2]}", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)

        tk.Button(transactions_screen, text="Settle Transaction", command=lambda: settle_transaction(transactions),
                  bg="#20B2AA", fg="white", font=("Garamond", 14)).pack(pady=10)
    else:
        tk.Label(transactions_screen, text="No transactions found.", bg="#F0F8FF", fg="#2F4F4F").pack(pady=10)

    tk.Button(transactions_screen, text="Back", command=transactions_screen.destroy,
              bg="#FF6347", fg="white", font=("Garamond", 14)).pack(pady=10)
    transactions_screen.mainloop()

# Function to settle a transaction
def settle_transaction(transactions):
    settle_screen = tk.Tk()
    settle_screen.title("Settle Transaction")
    settle_screen.configure(bg="#F0F8FF")
    settle_screen.geometry("1000x1000")

    tk.Label(settle_screen, text="Select a Transaction to Settle:", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=10)

    for transaction in transactions:
        tk.Button(settle_screen, text=f"{transaction[1]} is owed ${transaction[4]} for {transaction[5]} by {transaction[2]}",
                  command=lambda t=transaction: handle_settle(t), bg="#20B2AA", fg="white").pack(pady=5)

    tk.Button(settle_screen, text="Back", command=settle_screen.destroy,
              bg="#FF6347", fg="white").pack(pady=10)
    settle_screen.mainloop()

def handle_settle(transaction):
    cursor.execute("DELETE FROM transactions WHERE id=?", (transaction[0],))
    conn.commit()
    messagebox.showinfo("Success", "Transaction settled successfully!")



def add_transaction(previous_window=None):
    if previous_window:
        previous_window.destroy()
    transaction_screen = tk.Tk()
    transaction_screen.title("Add Transaction")
    transaction_screen.configure(bg="#F0F8FF")
    transaction_screen.geometry("1000x1000")

    tk.Label(transaction_screen, text="Add Transaction", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=10)

    tk.Label(transaction_screen, text="Roommate Name", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    roommate_entry = tk.Entry(transaction_screen)
    roommate_entry.pack(pady=5)

    tk.Label(transaction_screen, text="Room Name (For Verification)", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    room_name_entry = tk.Entry(transaction_screen)
    room_name_entry.pack(pady=5)

    tk.Label(transaction_screen, text="Amount", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    amount_entry = tk.Entry(transaction_screen)
    amount_entry.pack(pady=5)

    tk.Label(transaction_screen, text="Item", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    item_entry = tk.Entry(transaction_screen)
    item_entry.pack(pady=5)
    
    tk.Label(transaction_screen, text="Store: State Street Target, Walmart(Soon), Sam's Club (Soon), or None\nPlease write the brand name before any store-specific items.", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    store_entry = tk.Entry(transaction_screen)
    store_entry.pack(pady=5)
    
    
    def load_target():
        return target_prices

    def handle_add_transaction():
        roommate = roommate_entry.get().lower()
        room_name = room_name_entry.get().lower()
        amount = amount_entry.get()
        item = item_entry.get().lower()
        store = store_entry.get().lower()

        target_prices = load_target()

        if store == "target":
            # Convert amount to float for comparison
            try:
                amount_float = float(amount)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a valid number.")
                return

            # Check if the item is in the fake database and verify amount
            if item in target_prices:
                if amount_float == target_prices[item]:
                    cursor.execute("INSERT INTO transactions (username, roommate, room_name, amount, item) VALUES (?, ?, ?, ?, ?)",
                                (current_user, roommate, room_name, amount, item))
                    conn.commit()
                    messagebox.showinfo("Success", "Transaction added successfully!")
                    transaction_screen.destroy()
                else:
                    messagebox.showerror("Error", "Transaction could not be added. Item and amount do not match Target database.")
            else:
                messagebox.showerror("Error", "Item not found in Target prices database.")
        else:
            cursor.execute("INSERT INTO transactions (username, roommate, room_name, amount, item) VALUES (?, ?, ?, ?, ?)",
                        (current_user, roommate, room_name, amount, item))
            conn.commit()
            messagebox.showinfo("Success", "Transaction added successfully!")
            transaction_screen.destroy()

    tk.Button(transaction_screen, text="Add Transaction", command=handle_add_transaction,
              bg="#5F9EA0", fg="white").pack(pady=10)

    tk.Button(transaction_screen, text="Back", command=transaction_screen.destroy,
              bg="#FF6347", fg="white").pack(pady=10)
    transaction_screen.mainloop()

# Function to create a room
def create_room():
    room_screen = tk.Tk()
    room_screen.title("Create Room")
    room_screen.configure(bg="#F0F8FF")
    room_screen.geometry("1000x1000")

    tk.Label(room_screen, text="Create Room", font=("Garamond", 20, "bold"), bg="#F0F8FF", fg="#2F4F4F").pack(pady=10)

    tk.Label(room_screen, text="Roommate Name", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    roommate_entry = tk.Entry(room_screen)
    roommate_entry.pack(pady=5)

    tk.Label(room_screen, text="Room Name", bg="#F0F8FF", fg="#2F4F4F").pack(pady=5)
    room_name_entry = tk.Entry(room_screen)
    room_name_entry.pack(pady=5)

    def handle_create_room():
        roommate = roommate_entry.get()
        room_name = room_name_entry.get()

        if not roommate or not room_name:
            messagebox.showerror("Error", "Roommate and Room Name cannot be empty!")
            return

        try:
            cursor.execute("INSERT INTO rooms (owner, roommate, room_name) VALUES (?, ?, ?)",
                           (current_user, roommate, room_name))
            conn.commit()
            messagebox.showinfo("Success", "Room created successfully!")
            room_screen.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Room already exists with this name and roommate.")
        
    tk.Button(room_screen, text="Create Room", command=handle_create_room,
              bg="#5F9EA0", fg="white").pack(pady=10)

    tk.Button(room_screen, text="Back", command=room_screen.destroy,
              bg="#FF6347", fg="white").pack(pady=10)
    room_screen.mainloop()

# Show the welcome screen
show_welcome()

# Close the database connection
conn.close()

def on_closing():
    conn.close()
    root.quit()

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the welcome screen
#show_welcome()


