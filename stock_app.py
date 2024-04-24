from flask import Flask, render_template, request, redirect
import sqlite3
import webbrowser
import socket

ALLOWED_TABLES = {'growkits', 'spores', 'cannabis_seeds'}
seeds_grouped = {}
growkits_grouped = {}
spores_grouped = {}

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(r'product_inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def inventory():
    global growkits_grouped
    global spores_grouped
    if not growkits_grouped or not spores_grouped:
        growkits_grouped, spores_grouped = get_mushrooms_grouped()
    return render_template('inventory.html', products_grouped=growkits_grouped, spores_grouped=spores_grouped)

@app.route('/fastbuds')
def fastbuds():
    global seeds_grouped
    if not seeds_grouped:
        seeds_grouped = get_seeds_grouped()
    return render_template('fastbuds.html', seeds_grouped=seeds_grouped)

def get_seeds_grouped():
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT name, pack_size, stock, retail_price, id, storage_location_number
        FROM cannabis_seeds 
        WHERE manufacturer='Fastbuds'
        ORDER BY storage_location_number, name, pack_size
    """)
    seeds = cursor.fetchall()
    grouped = {}
    for seed in seeds:
        key = (seed['storage_location_number'], seed['name'])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(seed)
    conn.close()
    return grouped

def get_mushrooms_grouped():
    conn = get_db_connection()
    # Fetching growkits
    products_raw = conn.execute('SELECT * FROM growkits ORDER BY name, size').fetchall()
    growkits_grouped = {}
    for product in products_raw:
        if product['name'] in growkits_grouped:
            growkits_grouped[product['name']].append(product)
        else:
            growkits_grouped[product['name']] = [product]
    # Fetching spores
    spores_raw = conn.execute('SELECT * FROM spores ORDER BY name, form').fetchall()
    spores_grouped = {}
    for spore in spores_raw:
        if spore['name'] in spores_grouped:
            spores_grouped[spore['name']].append(spore)
        else:
            spores_grouped[spore['name']] = [spore]
    conn.close()
    return growkits_grouped, spores_grouped

@app.route('/update_stock/<table>/<int:id>', methods=["POST"])
def update_stock(table, id):
    if table not in ALLOWED_TABLES:
        return "Invalid table specified.", 400
    # the difference between what the user thinks the stock value is and what the user says it should be. This allows for concurrent editing.
    last_refresh_stock = int(request.form['last_refresh_stock'])
    submitted_stock = int(request.form['submitted_stock']) if 'submitted_stock' in request.form and request.form['submitted_stock'] else 0
    stock_difference = submitted_stock - last_refresh_stock
    conn = get_db_connection()
    query = 'UPDATE {} SET stock = stock + ? WHERE id = ?'.format(table)
    conn.execute(query, (stock_difference, id))
    conn.commit()
    conn.close()
    manufacturer_route = request.form.get('manufacturer_route', '')
    return redirect(f'/{manufacturer_route}')

def main():
    # from waitress import serve
    # hostname = socket.gethostname()
    # ipv4_address = socket.gethostbyname(hostname)
    # print(f'\nrunning on http://{ipv4_address}:8080/\n')
    # webbrowser.open(f'http://{ipv4_address}:8080/', new=2)
    # serve(app, host=f'{ipv4_address}', port=8080)
    app.run(debug=True)

if __name__ == '__main__':
    main()