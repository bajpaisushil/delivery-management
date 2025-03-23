import falcon
import json
import sqlite3
from datetime import datetime, timedelta
import math
import random
from falcon_cors import CORS  # Import the CORS middleware

# Configuration (same as before)
WAREHOUSE_COUNT = 10
AGENTS_PER_WAREHOUSE = 20
ORDERS_PER_AGENT = 60
CHECK_IN_TIME = 8  # Hour in the morning for check-in
ALLOCATION_TIME = 9  # Hour in the morning for allocation
MINUTES_PER_KM = 5
MAX_WORKING_HOURS = 10
MAX_DRIVING_DISTANCE = 100
MINIMUM_GUARANTEE = 500
TIER_1_ORDERS = 25
TIER_1_RATE = 35
TIER_2_ORDERS = 50
TIER_2_RATE = 42

DATABASE_NAME = ':memory:'  # Use ':memory:' for an in-memory database

# Create a single connection for the entire application
conn = sqlite3.connect(DATABASE_NAME)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = math.sin(dLat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class WarehouseResource:
    def on_get(self, req, resp):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Warehouses")
        warehouses = cursor.fetchall()
        resp.text = json.dumps([{'warehouse_id': w[0], 'name': w[1], 'latitude': w[2], 'longitude': w[3]} for w in warehouses])

    def on_post(self, req, resp):
        try:
            payload = json.loads(req.bounded_stream.read().decode('utf-8'))
            name = payload.get('name')
            latitude = payload.get('latitude')
            longitude = payload.get('longitude')
            if name and latitude and longitude:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Warehouses (name, latitude, longitude) VALUES (?, ?, ?)", (name, latitude, longitude))
                conn.commit()
                resp.status = falcon.HTTP_201
                resp.text = json.dumps({'message': 'Warehouse created successfully', 'id': cursor.lastrowid})
            else:
                resp.status = falcon.HTTP_400
                resp.text = json.dumps({'error': 'Missing required fields'})
        except (json.JSONDecodeError, KeyError):
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({'error': 'Invalid JSON'})

class AgentResource:
    def on_get(self, req, resp, warehouse_id=None):
        cursor = conn.cursor()
        if warehouse_id:
            cursor.execute("SELECT * FROM Agents WHERE warehouse_id = ?", (warehouse_id,))
            agents = cursor.fetchall()
            resp.text = json.dumps([{'agent_id': a[0], 'warehouse_id': a[1], 'name': a[2], 'latitude': a[3], 'longitude': a[4], 'is_available': bool(a[5]), 'checked_in_at': a[6], 'total_hours_worked': a[7], 'total_distance_travelled': a[8], 'orders_assigned': a[9]} for a in agents])
        else:
            cursor.execute("SELECT * FROM Agents")
            agents = cursor.fetchall()
            resp.text = json.dumps([{'agent_id': a[0], 'warehouse_id': a[1], 'name': a[2], 'latitude': a[3], 'longitude': a[4], 'is_available': bool(a[5]), 'checked_in_at': a[6], 'total_hours_worked': a[7], 'total_distance_travelled': a[8], 'orders_assigned': a[9]} for a in agents])

    def on_post(self, req, resp):
        try:
            payload = json.loads(req.bounded_stream.read().decode('utf-8'))
            warehouse_id = payload.get('warehouse_id')
            name = payload.get('name')
            latitude = payload.get('latitude')
            longitude = payload.get('longitude')
            if warehouse_id and name and latitude and longitude:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Agents (warehouse_id, name, latitude, longitude) VALUES (?, ?, ?, ?)", (warehouse_id, name, latitude, longitude))
                conn.commit()
                resp.status = falcon.HTTP_201
                resp.text = json.dumps({'message': 'Agent created successfully', 'id': cursor.lastrowid})
            else:
                resp.status = falcon.HTTP_400
                resp.text = json.dumps({'error': 'Missing required fields'})
        except (json.JSONDecodeError, KeyError):
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({'error': 'Invalid JSON'})

class OrderResource:
    def on_get(self, req, resp, warehouse_id=None):
        cursor = conn.cursor()
        if warehouse_id:
            cursor.execute("SELECT * FROM Orders WHERE warehouse_id = ?", (warehouse_id,))
            orders = cursor.fetchall()
            resp.text = json.dumps([{'order_id': o[0], 'warehouse_id': o[1], 'customer_name': o[2], 'delivery_address': o[3], 'latitude': o[4], 'longitude': o[5], 'delivery_status': o[6], 'assigned_to_agent': o[7], 'estimated_delivery_time': o[8]} for o in orders])
        else:
            cursor.execute("SELECT * FROM Orders")
            orders = cursor.fetchall()
            resp.text = json.dumps([{'order_id': o[0], 'warehouse_id': o[1], 'customer_name': o[2], 'delivery_address': o[3], 'latitude': o[4], 'longitude': o[5], 'delivery_status': o[6], 'assigned_to_agent': o[7], 'estimated_delivery_time': o[8]} for o in orders])

    def on_post(self, req, resp):
        try:
            payload = json.loads(req.bounded_stream.read().decode('utf-8'))
            warehouse_id = payload.get('warehouse_id')
            customer_name = payload.get('customer_name')
            delivery_address = payload.get('delivery_address')
            latitude = payload.get('latitude')
            longitude = payload.get('longitude')
            if warehouse_id and customer_name and delivery_address and latitude and longitude:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Orders (warehouse_id, customer_name, delivery_address, latitude, longitude) VALUES (?, ?, ?, ?, ?)", (warehouse_id, customer_name, delivery_address, latitude, longitude))
                conn.commit()
                resp.status = falcon.HTTP_201
                resp.text = json.dumps({'message': 'Order created successfully', 'id': cursor.lastrowid})
            else:
                resp.status = falcon.HTTP_400
                resp.text = json.dumps({'error': 'Missing required fields'})
        except (json.JSONDecodeError, KeyError):
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({'error': 'Invalid JSON'})

class AgentCheckInResource:
    def on_post(self, req, resp):
        try:
            payload = json.loads(req.bounded_stream.read().decode('utf-8'))
            agent_id = payload.get('agent_id')
            if agent_id:
                cursor = conn.cursor()
                now = datetime.now()
                cursor.execute("UPDATE Agents SET is_available = TRUE, checked_in_at = ? WHERE agent_id = ?", (now, agent_id))
                conn.commit()
                if cursor.rowcount > 0:
                    resp.status = falcon.HTTP_200
                    resp.text = json.dumps({'message': f'Agent {agent_id} checked in at {now}'})
                else:
                    resp.status = falcon.HTTP_404
                    resp.text = json.dumps({'error': f'Agent {agent_id} not found'})
            else:
                resp.status = falcon.HTTP_400
                resp.text = json.dumps({'error': 'Missing agent_id'})
        except (json.JSONDecodeError, KeyError):
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({'error': 'Invalid JSON'})

class OrderAllocationResource:
    def on_post(self, req, resp):
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Warehouses")
        warehouses = cursor.fetchall()

        for warehouse in warehouses:
            warehouse_id = warehouse[0]
            warehouse_lat = warehouse[2]
            warehouse_lon = warehouse[3]

            # Get available agents at the current warehouse
            cursor.execute("SELECT * FROM Agents WHERE warehouse_id = ? AND is_available = TRUE", (warehouse_id,))
            available_agents = cursor.fetchall()

            # Get pending orders at the current warehouse
            cursor.execute("SELECT * FROM Orders WHERE warehouse_id = ? AND delivery_status = 'Pending'", (warehouse_id,))
            pending_orders = cursor.fetchall()

            assigned_orders_count = 0
            unassigned_orders =[]

            for order in pending_orders:
                order_id = order[0]
                order_lat = order[4]
                order_lon = order[5]

                best_agent = None
                min_distance = float('inf')

                for agent in available_agents:
                    agent_id = agent[0]
                    agent_lat = agent[3]
                    agent_lon = agent[4]
                    total_hours_worked = agent[7]
                    total_distance_travelled = agent[8]
                    orders_assigned = agent[9]

                    # Calculate distance from agent's last known location (initially warehouse) to the order
                    last_location_lat = warehouse_lat if orders_assigned == 0 else agent_lat # Simplified: assuming agent starts from warehouse
                    last_location_lon = warehouse_lon if orders_assigned == 0 else agent_lon

                    distance_to_order = haversine(last_location_lat, last_location_lon, order_lat, order_lon)
                    estimated_travel_time = distance_to_order * MINUTES_PER_KM / 60  # in hours

                    # Check compliance
                    if total_hours_worked + estimated_travel_time <= MAX_WORKING_HOURS and \
                       total_distance_travelled + distance_to_order <= MAX_DRIVING_DISTANCE:
                        if distance_to_order < min_distance:
                            min_distance = distance_to_order
                            best_agent = agent

                if best_agent:
                    agent_id = best_agent[0]
                    agent_lat = best_agent[3]
                    agent_lon = best_agent[4]
                    total_hours_worked = best_agent[7]
                    total_distance_travelled = best_agent[8]
                    orders_assigned = best_agent[9]

                    distance_to_order = haversine(agent_lat, agent_lon, order_lat, order_lon)
                    estimated_travel_time = distance_to_order * MINUTES_PER_KM / 60

                    # Update agent's stats
                    cursor.execute("UPDATE Agents SET total_hours_worked = ?, total_distance_travelled = ?, orders_assigned = ?, latitude = ?, longitude = ? WHERE agent_id = ?",
                                   (total_hours_worked + estimated_travel_time, total_distance_travelled + distance_to_order, orders_assigned + 1, order_lat, order_lon, agent_id))

                    # Assign order to the agent
                    cursor.execute("UPDATE Orders SET delivery_status = 'Assigned', assigned_to_agent = ? WHERE order_id = ?", (agent_id, order_id))
                    cursor.execute("INSERT INTO Agent_Order_Assignment (agent_id, order_id) VALUES (?, ?)", (agent_id, order_id))
                    assigned_orders_count += 1
                    # Remove the assigned agent from the list for this iteration to prevent over-assignment in this simple logic
                    available_agents = [a for a in available_agents if a[0] != agent_id]
                else:
                    unassigned_orders.append(order_id)

            # Update status for unassigned orders
            for order_id in unassigned_orders:
                cursor.execute("UPDATE Orders SET delivery_status = 'Pending - Postponed' WHERE order_id = ?", (order_id,))

        conn.commit()
        resp.text = json.dumps({'message': 'Order allocation completed.', 'unassigned_orders': unassigned_orders})

class MetricsResource:
    def on_get(self, req, resp):
        cursor = conn.cursor()

        # Total number of agents
        cursor.execute("SELECT COUNT(*) FROM Agents")
        total_agents = cursor.fetchone()[0]

        # Number of available agents
        cursor.execute("SELECT COUNT(*) FROM Agents WHERE is_available = TRUE")
        available_agents = cursor.fetchone()[0]

        # Total number of orders
        cursor.execute("SELECT COUNT(*) FROM Orders")
        total_orders = cursor.fetchone()[0]

        # Number of pending orders
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE delivery_status = 'Pending'")
        pending_orders = cursor.fetchone()[0]

        # Number of assigned orders
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE delivery_status = 'Assigned'")
        assigned_orders = cursor.fetchone()[0]

        # Number of postponed orders
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE delivery_status LIKE 'Pending - Postponed%'")
        postponed_orders = cursor.fetchone()[0]

        # Average orders per agent (who have been assigned orders)
        cursor.execute("SELECT AVG(orders_assigned) FROM Agents WHERE orders_assigned > 0")
        avg_orders_per_agent = cursor.fetchone()[0] or 0

        # Agent utilization (number of agents with assigned orders)
        cursor.execute("SELECT COUNT(DISTINCT agent_id) FROM Agent_Order_Assignment")
        agents_with_assignments = cursor.fetchone()[0] or 0
        agent_utilization_percentage = (agents_with_assignments / total_agents * 100) if total_agents > 0 else 0

        metrics = {
            'total_agents': total_agents,
            'available_agents': available_agents,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'assigned_orders': assigned_orders,
            'postponed_orders': postponed_orders,
            'average_orders_per_agent': round(avg_orders_per_agent, 2),
            'agent_utilization_percentage': round(agent_utilization_percentage, 2)
        }

        resp.text = json.dumps(metrics)

def initialize_database():
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Agents (
            agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            is_available BOOLEAN DEFAULT TRUE,
            checked_in_at DATETIME,
            total_hours_worked REAL DEFAULT 0.0,
            total_distance_travelled REAL DEFAULT 0.0,
            orders_assigned INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Warehouses (
            warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id INTEGER NOT NULL,
            customer_name VARCHAR(255) NOT NULL,
            delivery_address VARCHAR(255) NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            delivery_status VARCHAR(50) DEFAULT 'Pending',
            assigned_to_agent INTEGER,
            estimated_delivery_time DATETIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Agent_Order_Assignment (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES Agents(agent_id),
            FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        )
    """)

    # Sample Data Generation
    if cursor.execute("SELECT COUNT(*) FROM Warehouses").fetchone()[0] == 0:
        for i in range(WAREHOUSE_COUNT):
            lat = 28.7041 + random.uniform(-0.5, 0.5)  # Delhi latitude +/- 0.5
            lon = 77.1025 + random.uniform(-0.5, 0.5)  # Delhi longitude +/- 0.5
            cursor.execute("INSERT INTO Warehouses (name, latitude, longitude) VALUES (?, ?, ?)", (f"Warehouse {i+1}", lat, lon))

    if cursor.execute("SELECT COUNT(*) FROM Agents").fetchone()[0] == 0:
        for i in range(WAREHOUSE_COUNT):
            for j in range(AGENTS_PER_WAREHOUSE):
                warehouse_id = i + 1
                lat = 28.7041 + random.uniform(-0.1, 0.1)
                lon = 77.1025 + random.uniform(-0.1, 0.1)
                cursor.execute("INSERT INTO Agents (warehouse_id, name, latitude, longitude) VALUES (?, ?, ?, ?)", (warehouse_id, f"Agent {i+1}-{j+1}", lat, lon))

    if cursor.execute("SELECT COUNT(*) FROM Orders").fetchone()[0] == 0:
        for i in range(WAREHOUSE_COUNT):
            warehouse_id = i + 1
            for j in range(AGENTS_PER_WAREHOUSE * ORDERS_PER_AGENT):
                lat = 28.7041 + random.uniform(-0.2, 0.2)
                lon = 77.1025 + random.uniform(-0.2, 0.2)
                cursor.execute("INSERT INTO Orders (warehouse_id, customer_name, delivery_address, latitude, longitude) VALUES (?, ?, ?, ?, ?)", (warehouse_id, f"Customer {i+1}-{j+1}", f"Address {i+1}-{j+1}", lat, lon))

    conn.commit()

# Initialize the database BEFORE creating the Falcon app
initialize_database()

cors = CORS(allow_all_origins=True)

# Falcon app setup with CORS middleware
app = falcon.App(middleware=[cors.middleware])

app.add_middleware(cors.middleware)

warehouses = WarehouseResource()
agents = AgentResource()
orders = OrderResource()
agent_checkin = AgentCheckInResource()
order_allocation = OrderAllocationResource()
metrics = MetricsResource()

app.add_route('/warehouses', warehouses)
app.add_route('/warehouses/{warehouse_id}/agents', agents)
app.add_route('/warehouses/{warehouse_id}/orders', orders)
app.add_route('/agents', agents)
app.add_route('/orders', orders)
app.add_route('/agents/checkin', agent_checkin)
app.add_route('/allocate', order_allocation)
app.add_route('/metrics', metrics)

if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    print("Serving on port 8000...")
    httpd.serve_forever()