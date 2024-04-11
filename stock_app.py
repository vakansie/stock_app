from flask import Flask, render_template, request, redirect
import sqlite3
import webbrowser

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(r'growkit_inventory.db')
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
    # calculate the difference between what the user thinks the stock value is and what the user says it should be. This allows for concurrent editing.
    last_refresh_stock = int(request.form['last_refresh_stock'])
    submitted_stock = int(request.form['submitted_stock'])
    stock_difference = submitted_stock - last_refresh_stock
    if stock_difference == 0: return redirect('/')
    # Update the stock in the database using the difference
    conn = get_db_connection()
    conn.execute('UPDATE growkits SET stock = stock + ? WHERE id = ?', (stock_difference, id))
    conn.commit()
    conn.close()
    return redirect('/')

def main():
    from waitress import serve
    # replace ip with your machines ipv4 to run on your local network
    ip = '127.0.0.1'
    print(f'\nrunning on http://{ip}:8080/\n')
    webbrowser.open(f'http://{ip}:8080/', new=2)
    serve(app, host=ip, port=8080)

if __name__ == '__main__':
    main()
