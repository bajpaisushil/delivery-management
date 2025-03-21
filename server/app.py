import falcon
import json
import sqlite3
from falcon_cors import CORS

# Enable CORS
cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)
app = falcon.App(middleware=[cors.middleware])

# SQLite Database Setup
def init_db():
    conn = sqlite3.connect('delivery.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            warehouse_id INTEGER NOT NULL,
            check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_hours_worked FLOAT DEFAULT 0,
            total_distance_covered FLOAT DEFAULT 0,
            total_orders_delivered INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id INTEGER NOT NULL,
            address TEXT NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            status TEXT DEFAULT 'pending',
            assigned_agent_id INTEGER,
            delivery_time_estimate FLOAT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Database connection
def get_db_connection():
    return sqlite3.connect('delivery.db')

# Agents Resource
class AgentsResource:
    def on_get(self, req, resp):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents")
        agents = cursor.fetchall()
        conn.close()
        resp.text = json.dumps(agents)
        resp.status = falcon.HTTP_200

# Orders Resource
class OrdersResource:
    def on_get(self, req, resp):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()
        conn.close()
        resp.text = json.dumps(orders)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        order_data = json.loads(req.bounded_stream.read())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (warehouse_id, address, latitude, longitude) VALUES (?, ?, ?, ?)",
            (order_data['warehouse_id'], order_data['address'], order_data['latitude'], order_data['longitude'])
        )
        conn.commit()
        conn.close()
        resp.status = falcon.HTTP_201

# Allocation Logic
def allocate_orders():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all pending orders
    cursor.execute("SELECT * FROM orders WHERE status = 'pending'")
    pending_orders = cursor.fetchall()

    # Fetch all available agents
    cursor.execute("SELECT * FROM agents WHERE total_hours_worked < 10 AND total_distance_covered < 100")
    available_agents = cursor.fetchall()

    # Assign orders to agents
    for order in pending_orders:
        for agent in available_agents:
            if agent[4] < 10 and agent[5] < 100:  # Check hours and distance
                # Assign order to agent
                cursor.execute(
                    "UPDATE orders SET assigned_agent_id = ?, status = 'assigned' WHERE id = ?",
                    (agent[0], order[0])
                )
                # Update agent's metrics
                cursor.execute(
                    "UPDATE agents SET total_orders_delivered = total_orders_delivered + 1, total_hours_worked = total_hours_worked + 0.0833, total_distance_covered = total_distance_covered + 1 WHERE id = ?",
                    (agent[0],)
                )
                conn.commit()
                break

    conn.close()

# Falcon App
app = falcon.App()
app.add_route('/agents', AgentsResource())
app.add_route('/orders', OrdersResource())

# Run the server using Waitress
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)