from flask import Flask, render_template, request, redirect
import sqlite3
import webbrowser
import socket
from collections import defaultdict, Counter
from desired_stock import grow_kit_full_stock_1200cc

ALLOWED_TABLES = {'growkits', 'spores', 'cannabis_seeds'}
manufacturer_routes = {
    'Royal Queen Seeds': 'rqs',
    'Fastbuds': 'fastbuds',
    'Green House Seeds': 'ghs',
    'Barneys Farm': 'barney',
    'Dutch Passion': 'dutch_passion'
}

cannabis_strains_colors = {
    "Feminized Autoflower": (0, 255, 0),
    "Feminized": (255, 192, 203),
    "Regular": (169, 169, 169),
    "Feminized Fast Flowering": (255, 255, 255),
    "Feminized Autoflower CBD": (0, 0, 255),
    "Feminized CBD": (0, 0, 255),
    "Feminized F1 Hybrid": (255, 255, 255),
    "Feminized Autoflower Tyson 2.0": (0, 255, 0),
    "Feminized Tyson 2.0": (255, 192, 203)
}

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(r'product_inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def inventory():
    growkits_grouped, spores_grouped = get_mushrooms_grouped()
    proposed_order = get_grow_kit_order_proposal()
    return render_template('inventory.html', products_grouped=growkits_grouped, spores_grouped=spores_grouped, proposed_order=proposed_order)

@app.route('/fastbuds')
def fastbuds():
    seeds_grouped, pack_sizes = get_seeds_grouped('Fastbuds')
    return render_template('seed_inventory.html', cannabis_strains_colors=cannabis_strains_colors, seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, page_title='Fastbuds Seeds', route='fastbuds', page_header='Fastbuds Inventory')

@app.route('/ghs')
def green_house():
    seeds_grouped, pack_sizes = get_seeds_grouped('Green House Seeds')
    return render_template('seed_inventory.html', 
                           cannabis_strains_colors=cannabis_strains_colors, 
                           seeds_grouped=seeds_grouped, 
                           pack_sizes=pack_sizes, 
                           page_title='Green House Seeds', 
                           route='ghs/all', 
                           page_header='Green House Inventory',
                           show_toggle=True)

@app.route('/ghs/all')
def green_house_all():
    seeds_grouped, pack_sizes = get_seeds('Green House Seeds')
    return render_template('single_table_seed_inventory.html', 
                           cannabis_strains_colors=cannabis_strains_colors, 
                           seeds_grouped=seeds_grouped, 
                           pack_sizes=pack_sizes, 
                           page_title='Green House Seeds', 
                           route='ghs', 
                           page_header='Green House Seeds Inventory',
                           show_toggle=True)
@app.route('/barney')
def barney():
    seeds_grouped, pack_sizes = get_seeds_grouped('Barneys Farm')
    return render_template('seed_inventory.html', cannabis_strains_colors=cannabis_strains_colors, seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, page_title='Barneys Farm', route='barney', page_header='Barneys Farm Inventory')

@app.route('/dutch_passion')
def dutch_passion():
    seeds_grouped, pack_sizes = get_seeds_grouped('Dutch Passion')
    return render_template('seed_inventory.html', cannabis_strains_colors=cannabis_strains_colors, seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, page_title='Dutch Passion', route='dutch_passion', page_header='Dutch Passion Inventory')

@app.route('/rqs')
def rqs():
    seeds_grouped, pack_sizes = get_seeds_grouped('Royal Queen Seeds')
    return render_template('seed_inventory.html', cannabis_strains_colors=cannabis_strains_colors, seeds_grouped=seeds_grouped, pack_sizes=pack_sizes, page_title='Royal Queen Seeds', route='rqs', page_header='Royal Queen Seeds Inventory')

@app.route('/all_seeds')
def all_seeds():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cannabis_seeds")
        seeds = cursor.fetchall()
        allowed_fields = get_allowed_fields(conn, 'cannabis_seeds')
    seeds_by_type = defaultdict(lambda: defaultdict(list))
    pack_sizes = defaultdict(set)
    for seed in seeds:
        seed_type = seed['seed_type']
        name = seed['name']
        manufacturer = seed['manufacturer']
        pack_size = seed['pack_size']
        seeds_by_type[seed_type][(name, manufacturer)].append(seed)
        pack_sizes[seed_type].add(pack_size)
    return render_template('all_seeds_inventory.html', cannabis_strains_colors=cannabis_strains_colors, seeds_by_type=seeds_by_type, pack_sizes=pack_sizes, allowed_fields=allowed_fields)

def get_seeds(manufacturer):
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT name, pack_size, stock, retail_price, id, storage_location_number, seed_type, manufacturer, manufacturers_collection
            FROM cannabis_seeds 
            WHERE manufacturer=?
            ORDER BY name, pack_size
        """, (manufacturer,))
        seeds = cursor.fetchall()
    grouped = defaultdict(lambda: defaultdict(list))
    pack_sizes = set()
    for seed in seeds:
        key = seed['name']
        grouped[key][seed['pack_size']].append(seed)
        pack_sizes.add(seed['pack_size'])
    return grouped, sorted(pack_sizes)

def get_seeds_grouped(manufacturer):
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT name, pack_size, stock, retail_price, id, storage_location_number, seed_type, manufacturer, manufacturers_collection
            FROM cannabis_seeds 
            WHERE manufacturer=?
            ORDER BY seed_type, storage_location_number, name, pack_size
        """, (manufacturer,))
        seeds = cursor.fetchall()
    grouped = defaultdict(lambda: defaultdict(list))
    pack_sizes = defaultdict(set)
    for seed in seeds:
        seed_type = seed['seed_type']
        key = (seed['storage_location_number'], seed['name'])
        grouped[seed_type][key].append(seed)
        pack_sizes[seed_type].add(seed['pack_size'])
    return grouped, pack_sizes

def get_mushrooms_grouped():
    with get_db_connection() as conn:
        # Fetching growkits
        products_raw = conn.execute('SELECT * FROM growkits ORDER BY name, size').fetchall()
        growkits_grouped = defaultdict(list)
        for product in products_raw:
            growkits_grouped[product['name']].append(product)
        # Fetching spores
        spores_raw = conn.execute('SELECT * FROM spores ORDER BY name, form').fetchall()
        spores_grouped = defaultdict(list)
        for spore in spores_raw:
            spores_grouped[spore['name']].append(spore)
    return growkits_grouped, spores_grouped

def get_grow_kit_order_proposal():
    preferred_stock_1200cc = Counter(grow_kit_full_stock_1200cc)
    with get_db_connection() as conn:
        products = conn.execute('SELECT name, stock FROM growkits WHERE size=1200 ORDER BY name').fetchall()
        current_stock = Counter({product['name']: product['stock'] for product in products})
        proposed_order = preferred_stock_1200cc - current_stock
        order_summary = []
        if proposed_order.total() >= 20:
            order_summary.append('freshmushrooms@freshmushrooms.nl\n')
            order_summary.append('Hoi Astrid,\n\nIk zou graag bestellen:\n')
            if proposed_order['Golden Teacher'] >= 15:
                order_summary.append('1 doos 1200cc GT')
                proposed_order['Golden Teacher'] = 0
            if proposed_order['McKennaii'] >= 15:
                order_summary.append('1 doos 1200cc MCK')
                proposed_order['McKennaii'] = 0
            while proposed_order.total() >= 20:
                box_items = Counter()
                for product, qty in proposed_order.items():
                    if box_items.total() < 20:
                        if qty > 0:
                            take_qty = min(qty, 20 - box_items.total())
                            box_items[product] = take_qty
                            proposed_order[product] -= take_qty
                if box_items:
                    order_summary.append('1 doos 1200cc met:')
                    for product, qty in box_items.items():
                        order_summary.append(f' {qty} {product}')
            remaining_kits = proposed_order.total()
            order_summary.append('\nGroeten,\nFrans\n')
            if remaining_kits > 0:
                order_summary.append('Remainder kits as they do not fill a full box:')
                for product, qty in proposed_order.items():
                    if qty > 0:
                        order_summary.append(f' {qty} {product}')
                order_summary.append(f'\nTotal remaining kits: {remaining_kits} (not enough to fill a box of 20)')
        else:
            order_summary.append('No grow kit order needed with the current stock.')
        return '\n'.join(order_summary)

@app.route('/update_stock/<table>/<int:id>', methods=["POST"])
def update_stock(table, id):
    if table not in ALLOWED_TABLES:
        print('noot allowed: table')
        return "Invalid table specified.", 400
    last_refresh_stock = int(request.form['last_refresh_stock'])
    submitted_stock = int(request.form['submitted_stock']) if 'submitted_stock' in request.form and request.form['submitted_stock'] else last_refresh_stock
    stock_difference = submitted_stock - last_refresh_stock
    if not stock_difference:
        return redirect(request.headers.get('Referer', '/'))
    print(f'id: {id}, table: {table}, last_refresh_stock: {last_refresh_stock}, submitted_stock: {submitted_stock}, stock_difference: {stock_difference}')
    with get_db_connection() as conn:
        query = 'UPDATE {} SET stock = stock + ? WHERE id = ?'.format(table)
        conn.execute(query, (stock_difference, id))
        conn.commit()
    return redirect(request.headers.get('Referer', '/'))

@app.route('/refresh', methods=["POST"])
def refresh_page():
    return redirect(request.headers.get('Referer', '/'))

def get_allowed_fields(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    allowed_fields = {col[1] for col in columns if col[5] == 0}  # column name is at index 1, pk flag at index 5
    return allowed_fields

def get_unique_values(table_name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        exclusions = {'id', 'name', 'retail_price', 'wholesale_price', 'stock', 'storage_location_number'}
        allowed_columns = [col[1] for col in columns_info if col[1] not in exclusions and col[5] == 0]
        unique_values = {}
        for column in allowed_columns:
            cursor.execute(f"SELECT DISTINCT {column} FROM {table_name}")
            fetched_values = cursor.fetchall()
            unique_values[column] = [val[0] for val in fetched_values]
    return unique_values

@app.route('/edit_product/<table>/<int:id>', methods=["GET"])
def edit_product(table, id):
    with get_db_connection() as conn:
        allowed_fields = get_allowed_fields(conn, table)
        unique_values = get_unique_values(table)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
        product = cursor.fetchone()
    if not product:
        return "Product not found", 404
    product_data = dict(product)
    return render_template('edit_product.html', product=product_data, fields=allowed_fields, unique_values=unique_values, table=table)

@app.route('/update_product/<table>/<int:id>', methods=["POST"])
def update_product(table, id):
    with get_db_connection() as conn:
        allowed_fields = get_allowed_fields(conn, table)
        update_data = {field: request.form[field] for field in allowed_fields if field in request.form}
        print(f'data: {update_data}')
        if not update_data:
            return "No valid fields provided.", 400
        set_clause = ', '.join([f"{field} = ?" for field in update_data])
        values = list(update_data.values())
        values.append(id)
        query = f'UPDATE {table} SET {set_clause} WHERE id = ?'
        conn.execute(query, values)
        conn.commit()
    return redirect(f'/{manufacturer_routes.get(update_data["manufacturer"], "")}')

@app.route('/add_product/<table>', methods=["GET", "POST"])
def add_product(table):
    with get_db_connection() as conn:
        allowed_fields = get_allowed_fields(conn, table)
        unique_values = get_unique_values(table)
        if request.method == 'POST':
            new_product_data = {field: request.form[field] for field in allowed_fields if field in request.form}
            if not new_product_data:
                return "All fields are required.", 400
            manufacturer = request.form.get('manufacturer')
            if table == 'cannabis_seeds':
                adjust_store_locations(conn, table, request.form.get('storage_location_number'), request.form.get('name'), manufacturer)
            columns = ', '.join(new_product_data.keys())
            placeholders = ', '.join(['?'] * len(new_product_data))
            query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
            conn.execute(query, list(new_product_data.values()))
            conn.commit()
            return redirect(f'/{manufacturer_routes.get(manufacturer, "")}')
    return render_template('add_product.html', fields=allowed_fields, unique_values=unique_values, table=table)

@app.route('/delete_product/<table>/<int:id>', methods=["POST"])
def delete_product(table, id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT manufacturer FROM {table} WHERE id = ?", (id,))
        product = cursor.fetchone()
        if not product:
            return "Product not found", 404
        manufacturer = product['manufacturer']
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
        conn.commit()
    return redirect(f'/{manufacturer_routes.get(manufacturer, "")}')

def adjust_store_locations(conn, table, new_location, name, manufacturer):
    new_location = int(new_location)
    print('running adjuster')
    print(f'table: {table}, chosen location: {new_location}, name: {name}, manufacturer: {manufacturer}')
    
    products_to_adjust = conn.execute(
        f'SELECT id, name, storage_location_number FROM {table} WHERE storage_location_number >= ? AND name != ? AND manufacturer = ? ORDER BY storage_location_number ASC',
        (new_location, name, manufacturer)
    ).fetchall()
    for product in products_to_adjust:
        if product['storage_location_number'] == new_location:
            print(f"{product['name']} changed from {new_location} to {new_location + 1}")
            conn.execute(
                f'UPDATE {table} SET storage_location_number = storage_location_number + 1 WHERE name = ? AND manufacturer = ?',
                (product['name'], manufacturer)
            )
            conn.commit()
            new_location += 1

def main():
    get_grow_kit_order_proposal()
    from waitress import serve
    hostname = socket.gethostname()
    ipv4_address = socket.gethostbyname(hostname)
    print(f'\nrunning on http://{ipv4_address}:8080/\n')
    webbrowser.open(f'http://{ipv4_address}:8080/', new=2)
    serve(app, host=f'{ipv4_address}', port=8080)

if __name__ == '__main__':
    main()