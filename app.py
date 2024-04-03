from flask import Flask, render_template, jsonify, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
import datetime
from flask import session
import secrets


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

def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as err:
        print(f"Error: '{err}'")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")
        return result


# Generate a secret key
app.secret_key = secrets.token_hex(16)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    # Check if user exists in the database
    connection = create_server_connection(host_name, user_name, user_password, db_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE Username = %s AND Password = %s AND Role = %s", (username, password, role))
    user = cursor.fetchone()
    connection.close()

    if user:
        # Store user's role in session
        session['role'] = role
        # Redirect user based on role
        return redirect(url_for(role.lower()))  # Dynamic redirection based on role
    else:
        return "Invalid credentials. Please try again."
    

# Routes for different user roles

@app.route('/admin')
def admin():
    return redirect(url_for('purchase'))

@app.route('/customer')
def customer():
    return redirect(url_for('products'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match. Please try again."

        # Add user to the database
        connection = create_server_connection(host_name, user_name, user_password, db_name)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (Username, Password, Role) VALUES (%s, %s, 'Customer')", (username, password))
        connection.commit()
        connection.close()

        return redirect(url_for('login_page'))
    else:
        return render_template('signup.html')


@app.route('/purchase_product', methods=['POST'])
def purchase_product():
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

@app.route('/purchase')
def purchase():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to retrieve purchases data
        select_query = "SELECT * FROM purchases"
        purchases = execute_read_query(connection, select_query)

        # Close the database connection
        connection.close()

        return render_template('purchase.html', purchases=purchases)
    except Error as e:
        return render_template('error.html', error=str(e))
    
    
# Route for removing a purchase
@app.route('/remove_purchase/<int:purchase_id>', methods=['POST'])
def remove_purchase(purchase_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to remove the purchase
        delete_query = "DELETE FROM purchases WHERE PurchaseID = %s"
        execute_query(connection, delete_query, (purchase_id,))

        # Close the database connection
        connection.close()

        return redirect(url_for('purchase'))
    except Error as e:
        return render_template('error.html', error=str(e))

# Route for editing a purchase
@app.route('/edit_purchase/<int:purchase_id>', methods=['POST'])
def edit_purchase(purchase_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Get the new data from the request
        new_data = request.json

        # Query to update the purchase
        update_query = "UPDATE purchases SET Quantity = %s, PurchaseDate = %s WHERE PurchaseID = %s"
        execute_query(connection, update_query, (*new_data, purchase_id))

        # Close the database connection
        connection.close()

        return jsonify({'message': 'Purchase edited successfully'})
    except Error as e:
        return jsonify({'error': str(e)})

# Route for the products screen
@app.route('/products')
def products():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to retrieve products data
        select_query = "SELECT * FROM products"
        products = execute_read_query(connection, select_query)

        # Close the database connection
        connection.close()

        # Get user's role from session
        user_role = session.get('role')

        return render_template('products.html', products=products, user_role=user_role)
    except Error as e:
        return render_template('error.html', error=str(e))
    
 
# Route for removing a product
@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to remove the product
        delete_query = "DELETE FROM products WHERE ProductID = %s"
        execute_query(connection, delete_query, (product_id,))

        # Close the database connection
        connection.close()

        return redirect(url_for('products'))
    except Error as e:
        return render_template('error.html', error=str(e))

# Route for editing a product
@app.route('/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Get the new data from the request
        new_data = request.json

        # Query to update the product
        update_query = "UPDATE products SET Name = %s, Description = %s, Price = %s, Quantity = %s WHERE ProductID = %s"
        execute_query(connection, update_query, (*new_data, product_id))

        # Close the database connection
        connection.close()

        return jsonify({'message': 'Product edited successfully'})
    except Error as e:
        return jsonify({'error': str(e)})

# Route for the users screen
@app.route('/users')
def users():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to retrieve users data
        select_query = "SELECT * FROM users"
        users = execute_read_query(connection, select_query)

        # Close the database connection
        connection.close()

        return render_template('user.html', users=users)
    except Error as e:
        return render_template('error.html', error=str(e))

# Route for removing a user
@app.route('/remove_user/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to remove the user
        delete_query = "DELETE FROM users WHERE UserID = %s"
        execute_query(connection, delete_query, (user_id,))

        # Close the database connection
        connection.close()

        return redirect(url_for('users'))
    except Error as e:
        return render_template('error.html', error=str(e))

# Route for editing a user
@app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Get the new data from the request
        new_data = request.json

        # Query to update the user
        update_query = "UPDATE users SET Username = %s, Password = %s, Role = %s WHERE UserID = %s"
        execute_query(connection, update_query, (*new_data, user_id))

        # Close the database connection
        connection.close()

        return jsonify({'message': 'User edited successfully'})
    except Error as e:
        return jsonify({'error': str(e)})
 

 
# Route for the users screen
@app.route('/sales')
def sales():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to retrieve sales data
        select_query = "SELECT * FROM sales"
        sales_data = execute_read_query(connection, select_query)  # Changed variable name here

        # Close the database connection
        connection.close()

        return render_template('sales.html', sales=sales_data)  # Changed variable name here
    except Error as e:
        return render_template('error.html', error=str(e))

# Route for removing a user
@app.route('/remove_sales/<int:sales_id>', methods=['POST'])
def remove_sales(sale_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to remove the user
        delete_query = "DELETE FROM sales WHERE SaleID = %s"
        execute_query(connection, delete_query, (sale_id,))

        # Close the database connection
        connection.close()

        return redirect(url_for('sales'))
    except Error as e:
        return render_template('error.html', error=str(e))

# Route for editing a user
@app.route('/edit_sales/<int:sale_id>', methods=['POST'])
def edit_sales(sale_id):
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Get the new data from the request
        new_data = request.json

        # Query to update the user
        update_query = "UPDATE sales SET Username = %s, Password = %s, Role = %s WHERE UserID = %s"
        execute_query(connection, update_query, (*new_data, sale_id))

        # Close the database connection
        connection.close()

        return jsonify({'message': 'User edited successfully'})
    except Error as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
