from flask import Flask, render_template, request, redirect
import sqlite3
import webbrowser
import socket

ALLOWED_TABLES = {'growkits', 'spores', 'cannabis_seeds'}
manufacturer_routes = {
    'Royal Queen Seeds': 'rqs',
    'Fastbuds': 'fastbuds',
    'Green House Seeds': 'ghs',
    'Barneys Farm': 'barney',
    'Dutch Passion': 'dutch_passion'
}

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(r'product_inventory_adding.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def inventory():
    growkits_grouped, spores_grouped = get_mushrooms_grouped()
    return render_template('inventory.html', products_grouped=growkits_grouped, spores_grouped=spores_grouped)

@app.route('/fastbuds')
def fastbuds():
    seeds_grouped, pack_sizes = get_seeds_grouped('Fastbuds')
    return render_template('seed_inventory.html', seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, title='Fastbuds Seeds', route='fastbuds', page_header='Fastbuds Inventory')

@app.route('/ghs')
def green_house():
    seeds_grouped, pack_sizes = get_seeds_grouped('Green House Seeds')
    return render_template('seed_inventory.html', seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, title='Green House Seeds', route='ghs', page_header='Green House Inventory')

@app.route('/barney')
def barney():
    seeds_grouped, pack_sizes = get_seeds_grouped('Barneys Farm')
    return render_template('seed_inventory.html', seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, page_title='Barneys Farm', route='barney', page_header='Barneys Farm Inventory')

@app.route('/dutch_passion')
def dutch_passion():
    seeds_grouped, pack_sizes = get_seeds_grouped('Dutch Passion')
    return render_template('seed_inventory.html', seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, page_title='Dutch Passion', route='dutch_passion', page_header='Dutch Passion Inventory')

@app.route('/rqs')
def rqs():
    seeds_grouped, pack_sizes = get_seeds_grouped('Royal Queen Seeds')
    return render_template('seed_inventory.html', seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, page_title='Royal Queen Seeds', route='rqs', page_header='Royal Queen Seeds Inventory')

def get_seeds_grouped(manufacturer):
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT name, pack_size, stock, retail_price, id, storage_location_number, seed_type, manufacturer
        FROM cannabis_seeds 
        WHERE manufacturer=?
        ORDER BY seed_type, storage_location_number, name, pack_size
    """, (manufacturer,))
    seeds = cursor.fetchall()
    grouped = {}
    pack_sizes = {}
    for seed in seeds:
        seed_type = seed['seed_type']
        if seed_type not in grouped:
            grouped[seed_type] = {}
            pack_sizes[seed_type] = set()
        key = (seed['storage_location_number'], seed['name'])
        if key not in grouped[seed_type]:
            grouped[seed_type][key] = []
        grouped[seed_type][key].append(seed)
        pack_sizes[seed_type].add(seed['pack_size'])
    conn.close()
    return grouped, pack_sizes

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
    if not stock_difference: return redirect(request.headers.get('Referer', '/'))
    print(f'id: {id}, table: {table}, last_refresh_stock: {last_refresh_stock}, submitted_stock: {submitted_stock}, stock_difference: {stock_difference}')
    conn = get_db_connection()
    query = 'UPDATE {} SET stock = stock + ? WHERE id = ?'.format(table)
    conn.execute(query, (stock_difference, id))
    conn.commit()
    conn.close()
    return redirect(request.headers.get('Referer', '/'))

@app.route('/batch_update_stock', methods=['POST'])
def batch_update_stock():
    updates = request.json
    conn = get_db_connection()
    try:
        for update in updates:
            tables = ['spores', 'growkits'] if request.headers.get('Referer') == 'http://127.0.0.1:5000/' else ['cannabis_seeds']
            for table in tables:
                if table not in ALLOWED_TABLES:
                    continue
                id = int(update['id'])
                stock_difference = int(update['submitted_stock']) - int(update['last_refresh_stock'])
                if stock_difference != 0:
                    query = 'UPDATE {} SET stock = stock + ? WHERE id = ?'.format(table)
                    conn.execute(query, (stock_difference, id))
        conn.commit()
    finally:
        conn.close()
    return redirect(request.headers.get('Referer', '/'))

def get_allowed_fields(table_name):
    # This function will query the database schema to determine allowed fields excluding the primary key
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    # Filtering out the primary key column; assuming it's denoted by pk=1 in the pragma output
    allowed_fields = {col[1] for col in columns if col[5] == 0}  # column name is at index 1, pk flag at index 5
    return allowed_fields

@app.route('/edit_product/<table>/<int:id>', methods=["GET"])
def edit_product(table, id):
    allowed_fields = get_allowed_fields(table)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
    product = cursor.fetchone()
    conn.close()
    if not product:
        return "Product not found", 404
    product_data = {description[0]: product[idx] for idx, description in enumerate(cursor.description)}
    # print("Product Data:", product_data)
    return render_template('edit_product.html', product=product_data, fields=allowed_fields, table=table, manufacturer=product['manufacturer'])

@app.route('/update_product/<table>/<int:id>', methods=["POST"])
def update_product(table, id):
    # Dynamically determine allowed fields by excluding the primary key
    allowed_fields = get_allowed_fields(table)
    # Gather update data from the form, ignoring fields not in allowed_fields
    update_data = {field: request.form[field] for field in allowed_fields if field in request.form}
    print(f'data: {update_data}')
    if not update_data:
        return "No valid fields provided.", 400
    # Create SQL update string based on the fields provided
    set_clause = ', '.join([f"{field} = ?" for field in update_data])
    values = list(update_data.values())
    values.append(id)  # Append id for the where clause
    # Connect to DB and update the data
    conn = get_db_connection()
    # Before inserting the new product, adjust the store locations
    if 'storage_location_number' in update_data:
        adjust_store_locations(conn, table, int(update_data['storage_location_number']), update_data['name'])
    query = f'UPDATE {table} SET {set_clause} WHERE id = ?'
    conn.execute(query, values)
    conn.commit()
    conn.close()
    return redirect(f'/{manufacturer_routes.get(update_data['manufacturer'], '')}')

@app.route('/add_product/<table>', methods=["GET", "POST"])
def add_product(table):
    if request.method == 'POST':
        # Handle form submission for adding a new product
        allowed_fields = get_allowed_fields(table)
        new_product_data = {field: request.form[field] for field in allowed_fields if field in request.form}
        # Check if all necessary data is provided
        if not new_product_data:
            return "All fields are required.", 400
        # Insert data into the database
        conn = get_db_connection()
        # Before inserting the new product, adjust the store locations
        if 'storage_location_number' in new_product_data:
            adjust_store_locations(conn, table, int(new_product_data['storage_location_number']), new_product_data['name'])
        columns = ', '.join(new_product_data.keys())
        placeholders = ', '.join(['?'] * len(new_product_data))
        query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        conn.execute(query, list(new_product_data.values()))
        conn.commit()
        conn.close()
        manufacturer = request.form.get('manufacturer')
        return redirect(f'/{manufacturer_routes.get(manufacturer, '')}')
    # For GET request, display the form
    allowed_fields = get_allowed_fields(table)
    return render_template('add_product.html', fields=allowed_fields, table=table)

@app.route('/delete_product/<table>/<int:id>', methods=["POST"])
def delete_product(table, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # First, fetch the manufacturer's name for redirection purposes
    cursor.execute(f"SELECT manufacturer FROM {table} WHERE id = ?", (id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        return "Product not found", 404
    manufacturer = product[0]
    # Proceed to delete the product
    cursor.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(f'/{manufacturer_routes.get(manufacturer, '')}')

def adjust_store_locations(conn, table, new_location, name):
    print('running adjuster')
    # Query to find products with the same or higher store_location_number
    products_to_adjust = conn.execute(
        f'SELECT id, name, storage_location_number FROM {table} WHERE storage_location_number >= ? AND name != ? ORDER BY storage_location_number ASC',
        (new_location, name,)
    ).fetchall()
    # Iterate over these products and increment store_location_numbers where needed
    for product in products_to_adjust:
        if product['storage_location_number'] == new_location:
            print(f'{product['name']} changed from {new_location} to {new_location + 1}')
            # conn.execute(
            #     f'UPDATE {table} SET storage_location_number = storage_location_number + 1 WHERE id = ?',
            #     (product['id'],)
            # )
            # conn.commit()
            new_location += 1

def main():
    # from waitress import serve
    # hostname = socket.gethostname()
    # ipv4_address = socket.gethostbyname(hostname)
    # print(f'\nrunning on http://{ipv4_address}:2222/\n')
    # webbrowser.open(f'http://{ipv4_address}:2222/', new=2)
    # serve(app, host=f'{ipv4_address}', port=2222)
    app.run(debug=True)

if __name__ == '__main__':
    main()