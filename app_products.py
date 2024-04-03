from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
from mysql.connector import Error
import random

app = Flask(__name__)

# Define the database connection details
host_name = 'localhost'
user_name = 'root'
user_password = 'Kenyan@2003'
db_name = 'system1'

def create_server_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

# Function to generate a random ProductID
def generate_product_id():
    return random.randint(1000, 9999)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    connection = create_server_connection(host_name, user_name, user_password, db_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE Username = %s AND Password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        # Redirect to the products page after successful login
        return redirect('/products')
    else:
        return "Invalid username or password."

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    role = 'customer'  # Only customer accounts can be created from this interface
    connection = create_server_connection(host_name, user_name, user_password, db_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE Username = %s", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        return "Username already exists. Please choose a different username."
    else:
        cursor.execute("INSERT INTO users (Username, Password, Role) VALUES (%s, %s, %s)", (username, password, role))
        connection.commit()
        return f"New customer account created for {username}!"

@app.route('/products')
def products():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)
        cursor = connection.cursor(dictionary=True)

        # Query to fetch products from the database
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        # Close the database connection
        connection.close()

        return render_template('products.html', products=products)
    except Error as e:
        print(f"Error: '{e}'")

@app.route('/purchase')
def purchase():
    # Placeholder for actual logic
    return render_template('purchase.html')



@app.route('/sales')
def sales():
    # Placeholder for actual logic
    return render_template('sales.html')

@app.route('/user')
def user():
    # Placeholder for actual logic
    return render_template('user.html')


@app.route('/make_purchase', methods=['POST'])
def make_purchase():
    if request.method == 'POST':
        try:
            # Retrieve form data
            data = request.json
            purchase_id = data['purchase_id']
            product_id = data['product_id']
            purchase_date = data['purchase_date']
            quantity = data['quantity']
            cost = data['cost']

            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Insert the purchase into the database
            insert_query = "INSERT INTO purchases (PurchaseID, ProductID, PurchaseDate, Quantity, Cost) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (purchase_id, product_id, purchase_date, quantity, cost))

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            return jsonify({'success': True})
        except Error as e:
            return jsonify({'success': False, 'error': str(e)})


@app.route('/purchase_management')
def purchase_management():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)
        cursor = connection.cursor(dictionary=True)

        # Query to fetch purchases from the database
        cursor.execute("SELECT * FROM purchases")
        purchases = cursor.fetchall()

        # Close the database connection
        connection.close()

        return render_template('purchase.html', purchases=purchases)
    except Error as e:
        print(f"Error: '{e}'")

# Route for removing a purchase
@app.route('/remove_purchase', methods=['POST'])
def remove_purchase():
    if request.method == 'POST':
        purchase_id = request.form['purchase_id']
        try:
            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Query to delete a purchase from the database
            delete_query = f"DELETE FROM purchases WHERE PurchaseID = {purchase_id}"
            cursor.execute(delete_query)

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            # Redirect to the purchases page
            return redirect('/purchase')
        except Error as e:
            print(f"Error: '{e}'")
            return "An error occurred while removing the purchase"

# Route for displaying add purchase form
@app.route('/add_purchase', methods=['GET'])
def add_purchase():
    return render_template('add_purchase.html')

# Route for processing add purchase form submission
@app.route('/add_purchase', methods=['POST'])
def add_purchase_submit():
    # Retrieve form data
    product_id = request.form['product_id']
    purchase_date = request.form['purchase_date']
    cost = request.form['cost']
    quantity = request.form['quantity']

    # Generate a random PurchaseID
    purchase_id = random.randint(1000, 9999)

    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)
        cursor = connection.cursor()

        # Query to insert a new purchase into the database
        insert_query = "INSERT INTO purchases (PurchaseID, ProductID, PurchaseDate, Cost, Quantity) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (purchase_id, product_id, purchase_date, cost, quantity))

        # Commit the transaction
        connection.commit()

        # Close the database connection
        connection.close()

        # Redirect to the purchases page
        return redirect('/purchase')
    except Error as e:
        print(f"Error: '{e}'")
        return "An error occurred while adding the purchase"

# Route for updating a purchase
@app.route('/update_purchase', methods=['POST'])
def update_purchase():
    if request.method == 'POST':
        purchase_id = request.form['purchase_id']
        cost = request.form['cost']
        quantity = request.form['quantity']
        try:
            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Query to update the purchase in the database
            update_query = "UPDATE purchases SET Cost = %s, Quantity = %s WHERE PurchaseID = %s"
            cursor.execute(update_query, (cost, quantity, purchase_id))

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            # Redirect to the purchases page
            return redirect('/purchase')
        except Error as e:
            print(f"Error: '{e}'")
            return "An error occurred while updating the purchase"

# Add route for rendering user management page
@app.route('/users')
def users():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)
        cursor = connection.cursor(dictionary=True)

        # Query to fetch users from the database
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        # Close the database connection
        connection.close()

        return render_template('user.html', users=users)
    except Error as e:
        print(f"Error: '{e}'")

# Route for adding a user
@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        try:
            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Query to insert a new user into the database
            insert_query = "INSERT INTO users (Username, Password, Role) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (username, password, role))

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            # Redirect to the users page
            return redirect('/users')
        except Error as e:
            print(f"Error: '{e}'")
            return "An error occurred while adding the user"

# Route for updating a user
@app.route('/update_user', methods=['POST'])
def update_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        try:
            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Query to update the user in the database
            update_query = "UPDATE users SET Username = %s, Password = %s, Role = %s WHERE UserID = %s"
            cursor.execute(update_query, (username, password, role, user_id))

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            # Redirect to the users page
            return redirect('/users')
        except Error as e:
            print(f"Error: '{e}'")
            return "An error occurred while updating the user"

# Route for removing a user
@app.route('/remove_user', methods=['POST'])
def remove_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        try:
            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Query to delete a user from the database
            delete_query = f"DELETE FROM users WHERE UserID = {user_id}"
            cursor.execute(delete_query)

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            # Redirect to the users page
            return redirect('/users')
        except Error as e:
            print(f"Error: '{e}'")
            return "An error occurred while removing the user"





# Route for removing a product
@app.route('/remove_product', methods=['POST'])
def remove_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        try:
            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Query to delete a product from the database
            delete_query = f"DELETE FROM products WHERE ProductID = {product_id}"
            cursor.execute(delete_query)

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            # Redirect to the products page
            return redirect('/products')
        except Error as e:
            print(f"Error: '{e}'")
            return "An error occurred while removing the product"

# Route for displaying add product form
@app.route('/add_product', methods=['GET'])
def add_product():
    return render_template('add_product.html')

# Route for processing add product form submission
@app.route('/add_product', methods=['POST'])
def add_product_submit():
    # Retrieve form data
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    quantity = request.form['quantity']

    # Generate a random ProductID
    product_id = generate_product_id()

    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)
        cursor = connection.cursor()

        # Query to insert a new product into the database
        insert_query = "INSERT INTO products (ProductID, Name, Description, Price, Quantity) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (product_id, name, description, price, quantity))

        # Commit the transaction
        connection.commit()

        # Close the database connection
        connection.close()

        # Redirect to the products page
        return redirect('/products')
    except Error as e:
        print(f"Error: '{e}'")
        return "An error occurred while adding the product"

# Route for updating a product
@app.route('/update_product', methods=['POST'])
def update_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']
        try:
            # Create a database connection
            connection = create_server_connection(host_name, user_name, user_password, db_name)
            cursor = connection.cursor()

            # Query to update the product in the database
            update_query = "UPDATE products SET Name = %s, Description = %s, Price = %s, Quantity = %s WHERE ProductID = %s"
            cursor.execute(update_query, (name, description, price, quantity, product_id))

            # Commit the transaction
            connection.commit()

            # Close the database connection
            connection.close()

            # Redirect to the products page
            return redirect('/products')
        except Error as e:
            print(f"Error: '{e}'")
            return "An error occurred while updating the product"

if __name__ == "__main__":
    app.run(debug=True)
