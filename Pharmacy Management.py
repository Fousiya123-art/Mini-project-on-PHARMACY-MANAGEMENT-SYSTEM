import sqlite3
import hashlib
from datetime import datetime
def create_db():
    conn = sqlite3.connect("pharmacy11.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT CHECK(role IN ('admin','customer'))
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        company TEXT,
        batch TEXT,
        expiry TEXT,
        price REAL,
        stock INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sold_at TEXT,
        total REAL,
        user_id INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sale_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        medicine_id INTEGER,
        qty INTEGER,
        unit_price REAL
    )''')
    c.execute("SELECT * FROM users")
    if not c.fetchall():
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        cust_pass = hashlib.sha256("cust123".encode()).hexdigest()
        c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", ("admin", admin_pass, "admin"))
        c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", ("customer1", cust_pass, "customer"))
    conn.commit()

    conn.close()
def login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    hashed = hashlib.sha256(password.encode()).hexdigest()

    conn= sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    c.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, hashed))
    user = c.fetchone()
    conn.close()
    if user:
        print(f"\n Login successful! Welcome, {username} ({user[1].capitalize()})")
        return {"id": user[0], "role": user[1], "username": username}
    else:
        print("\n Invalid username or password!")
        return None


def add_medicine():
    conn= sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    name = input("Medicine name: ")
    company = input("Company: ")
    batch = input("Batch number: ")
    expiry = input("Expiry date (YYYY-MM-DD): ")
    price = float(input("Price: "))
    stock = int(input("Stock quantity: "))

    c.execute("INSERT INTO medicines(name,company,batch,expiry,price,stock) VALUES(?,?,?,?,?,?)",
                (name, company, batch, expiry, price, stock))
    conn.commit()
    conn.close()
    print(" Medicine added successfully.\n")

def view_medicines():
    conn= sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    c.execute("SELECT * FROM medicines")
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("No medicines found!")
        return
    print("\n--- Medicine List ---")
    print("{:<5} {:<15} {:<15} {:<10} {:<12} {:<8} {:<6}".format("ID", "Name", "Company", "Batch", "Expiry", "Price",
                                                                 "Stock"))
    for r in rows:
        print("{:<5} {:<15} {:<15} {:<10} {:<12} {:<8} {:<6}".format(r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    print()
def update_stock():
    view_medicines()
    mid=int(input("Enter medicine ID to update: "))
    new_stock = int(input("Enter new stock quantity: "))
    conn= sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    c.execute("update medicines set stock=? where id=?", (new_stock, mid))
    conn.commit()
    conn.close()
    print("\nStock updated successfully.\n")
def delete_medicine():
    view_medicines()
    mid=int(input("Enter medicine ID to delete: "))
    conn= sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    c.execute("delete from medicines where id=?", (mid,))
    conn.commit()
    conn.close()
    print("\nMedicine deleted successfully.\n")
def view_sales():
    conn= sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    c.execute("SELECT * FROM sales")
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("No sales found!")
        return
    print("\n--- Sales Report ---")
    print("{:<5} {:<20} {:<10}".format("ID", "Date", "Total"))
    for r in rows:
        print("{:<5} {:<20} {:<10} ".format(r[0], r[1], r[2]))
    print()
def search_medicines():
    name=input("Enter medicine name: ")
    conn= sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    c.execute("SELECT * FROM medicines WHERE name=?", (name,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("No medicines found!")
        return
    print("\n--- Medicine List Under Search ---")
    print("{:<5} {:<15} {:<15} {:<10} {:<12} {:<8} {:<6}".format("ID", "Name", "Company", "Batch", "Expiry", "Price",
                                                                 "Stock"))
    for r in rows:
        print("{:<5} {:<15} {:<15} {:<10} {:<12} {:<8} {:<6}".format(r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    print()
def buy_medicine(user_id):
    search_medicines()
    mid=int(input("Enter medicine ID to buy: "))
    qty=int(input("Enter quantity: "))
    conn=sqlite3.connect("pharmacy11.db")
    c= conn.cursor()
    c.execute("SELECT  name,price,stock FROM medicines WHERE id=?", (mid,))
    med=c.fetchone()
    if not med:
        print("No medicine found!")
        return
    if med[2] < qty:
        print("You don't have enough medicines!")
        return
    total=med[1]*qty
    print("Total amount:",total)
    confirm=input("Do you want to buy this medicine? (Y/N): ").lower()
    if confirm == "y":
        c.execute("update medicines set stock=stock- ? where id=?", (qty,mid))
        c.execute("insert into sales(sold_at,total) values (?,?)", (datetime.now().strftime("%d/%m/%Y"),total))
        conn.commit()
        print("\nMedicine buy successfully.\n")
    conn.close()
def admin():
    while True:
        print("""
        --- ADMIN MENU ---
        1. Add Medicine
        2. View Medicines
        3. Update Stock
        4. Delete Medicine
        5. View Sales Report
        0. Logout
        """)
        choice=int(input("Enter your choice: "))
        if choice == 1:add_medicine()
        elif choice == 2:view_medicines()
        elif choice == 3:update_stock()
        elif choice == 4:delete_medicine()
        elif choice == 5:view_sales()
        elif choice == 0:break
        else:print("Invalid choice.")
def customer():
    while True:
        print("""
        --- CUSTOMER MENU ---
        1. Search Medicine
        2. Buy Medicine
        0. Logout
        """)
        choice=int(input("Enter your choice: "))
        if choice == 1:search_medicines()
        elif choice == 2:buy_medicine("user_id")
        elif choice == 0:break
        else:print("Invalid choice.")
def main():
    create_db()
    print("Welcome to Pharmacy Management")
    user=login()
    if not user:
        return
    if user["role"]=="admin":
        admin()
    else:
        customer()
    print("\nThank you for using Pharmacy Management")
# if __name__ == "__main__":
#      main()
def run():
    main()
run()











0



