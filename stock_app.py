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
    stock = request.form['stock']
    conn = get_db_connection()
    conn.execute('UPDATE growkits SET stock = ? WHERE id = ?', (stock, id))
    conn.commit()
    conn.close()
    return redirect('/')

app.run()
