from flask import Flask, render_template, jsonify, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

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

def calculate_total(purchases):
    totals = []
    for purchase in purchases:
        total = purchase[2] * purchase[4]
        totals.append(total)
    return totals

# Route for the purchase screen, now the default page
@app.route('/')
def purchase():
    try:
        # Create a database connection
        connection = create_server_connection(host_name, user_name, user_password, db_name)

        # Query to retrieve purchases data
        select_query = "SELECT * FROM purchases"
        purchases = execute_read_query(connection, select_query)

        # Calculate totals
        totals = calculate_total(purchases)

        # Close the database connection
        connection.close()

        return render_template('purchase.html', purchases=purchases, totals=totals)
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


# Routes for other pages
@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/user')
def user():
    return render_template('user.html')

if __name__ == "__main__":
    app.run(debug=True)
