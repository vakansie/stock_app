from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('growkit_inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def inventory():
    conn = get_db_connection()
    products_raw = conn.execute('SELECT * FROM growkits ORDER BY name, size').fetchall()
    conn.close()
    # Grouping products by name
    products_grouped = {}
    for product in products_raw:
        if product['name'] in products_grouped:
            products_grouped[product['name']].append(product)
        else:
            products_grouped[product['name']] = [product]
    return render_template('inventory.html', products_grouped=products_grouped)

@app.route('/update_stock/<int:id>', methods=['POST'])
def update_stock(id):
    last_refresh_stock = int(request.form['last_refresh_stock'])
    submitted_stock = int(request.form['submitted_stock'])
    # if not submitted_stock.isdecimal(): return
    conn = get_db_connection()
    # Calculate the difference based on the last refresh stock value
    stock_difference = submitted_stock - last_refresh_stock    # Calculate the difference
    # Update the stock in the database using the difference
    conn.execute('UPDATE growkits SET stock = stock + ? WHERE id = ?', (stock_difference, id))
    conn.commit()
    conn.close()
    return redirect('/')

app.run(debug=True)