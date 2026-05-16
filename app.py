from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = 'database.db'


# -----------------------------
# CONNECT DATABASE
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn


# -----------------------------
# CREATE TABLES
# -----------------------------
def create_tables():

    conn = get_db_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Rooms Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_name TEXT NOT NULL,
        building TEXT NOT NULL
    )
    """)

    # -----------------------------
    # Assets Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Assets (
        asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_name TEXT NOT NULL,
        room_id INTEGER,
        status TEXT,

        FOREIGN KEY(room_id)
        REFERENCES Rooms(room_id)
    )
    """)

    # -----------------------------
    # Employees Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT NOT NULL,
        email TEXT UNIQUE
    )
    """)

    # -----------------------------
    # Technicians Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Technicians (
        technician_id INTEGER PRIMARY KEY AUTOINCREMENT,
        technician_name TEXT NOT NULL,
        specialty TEXT
    )
    """)

    # -----------------------------
    # Maintenance Requests Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Maintenance_Requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,

        employee_id INTEGER,
        asset_id INTEGER,
        technician_id INTEGER,

        issue_description TEXT,
        request_date TEXT,
        status TEXT,

        FOREIGN KEY(employee_id)
        REFERENCES Employees(employee_id),

        FOREIGN KEY(asset_id)
        REFERENCES Assets(asset_id),

        FOREIGN KEY(technician_id)
        REFERENCES Technicians(technician_id)
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route('/')
def home():

    return render_template('index.html')

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route('/dashboard')
def dashboard():

    conn = get_db_connection()

    cursor = conn.cursor()

    # Count Rooms
    cursor.execute("""
    SELECT COUNT(*)
    FROM Rooms
    """)

    total_rooms = cursor.fetchone()[0]

    # Count Assets
    cursor.execute("""
    SELECT COUNT(*)
    FROM Assets
    """)

    total_assets = cursor.fetchone()[0]

    # Count Employees
    cursor.execute("""
    SELECT COUNT(*)
    FROM Employees
    """)

    total_employees = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total_rooms=total_rooms,
        total_assets=total_assets,
        total_employees=total_employees
    )
# -----------------------------
# VIEW ROOMS
# -----------------------------
@app.route('/rooms')
def rooms():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Rooms")

    rooms_data = cursor.fetchall()

    conn.close()

    return render_template(
        'rooms.html',
        rooms=rooms_data
    )


# -----------------------------
# ADD ROOM
# -----------------------------
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():

    if request.method == 'POST':

        room_name = request.form['room_name']
        building = request.form['building']

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO Rooms
        (room_name, building)

        VALUES (?, ?)
        """, (room_name, building))

        conn.commit()
        conn.close()

        return redirect('/rooms')

    return render_template('add_room.html')

# -----------------------------
# DELETE ROOM
# -----------------------------
@app.route('/delete_room/<int:id>')
def delete_room(id):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM Rooms
    WHERE room_id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/rooms')

# -----------------------------
# VIEW EMPLOYEES
# -----------------------------
@app.route('/employees')
def employees():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM Employees
    """)

    employees_data = cursor.fetchall()

    conn.close()

    return render_template(
        'employees.html',
        employees=employees_data
    )


# -----------------------------
# ADD EMPLOYEE
# -----------------------------
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():

    if request.method == 'POST':

        employee_name = request.form['employee_name']
        email = request.form['email']

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO Employees
        (employee_name, email)

        VALUES (?, ?)
        """, (employee_name, email))

        conn.commit()
        conn.close()

        return redirect('/employees')

    return render_template('add_employee.html')

# -----------------------------
# VIEW ASSETS
# -----------------------------
@app.route('/assets')
def assets():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        Assets.asset_id,
        Assets.asset_name,
        Rooms.room_name,
        Assets.status

    FROM Assets

    LEFT JOIN Rooms
    ON Assets.room_id = Rooms.room_id
    """)

    assets_data = cursor.fetchall()

    conn.close()

    return render_template(
        'assets.html',
        assets=assets_data
    )


# -----------------------------
# ADD ASSET
# -----------------------------
@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():

    conn = get_db_connection()

    cursor = conn.cursor()

    # GET ROOMS
    cursor.execute("""
    SELECT * FROM Rooms
    """)

    rooms = cursor.fetchall()

    if request.method == 'POST':

        asset_name = request.form['asset_name']
        room_id = request.form['room_id']
        status = request.form['status']

        cursor.execute("""
        INSERT INTO Assets
        (asset_name, room_id, status)

        VALUES (?, ?, ?)
        """, (asset_name, room_id, status))

        conn.commit()
        conn.close()

        return redirect('/assets')

    conn.close()

    return render_template(
        'add_asset.html',
        rooms=rooms
    )
# -----------------------------
# VIEW MAINTENANCE REQUESTS
# -----------------------------
@app.route('/requests')
def requests_page():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        Maintenance_Requests.request_id,
        Employees.employee_name,
        Assets.asset_name,
        Technicians.technician_name,
        Maintenance_Requests.issue_description,
        Maintenance_Requests.status

    FROM Maintenance_Requests

    LEFT JOIN Employees
    ON Maintenance_Requests.employee_id = Employees.employee_id

    LEFT JOIN Assets
    ON Maintenance_Requests.asset_id = Assets.asset_id

    LEFT JOIN Technicians
    ON Maintenance_Requests.technician_id = Technicians.technician_id
    """)

    requests_data = cursor.fetchall()

    conn.close()

    return render_template(
        'requests.html',
        requests=requests_data
    )
# -----------------------------
# ADD SAMPLE TECHNICIAN
# -----------------------------
@app.route('/add_sample_technician')
def add_sample_technician():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Technicians
    (technician_name, specialty)

    VALUES
    ('John Smith', 'Electrical')
    """)

    conn.commit()
    conn.close()

    return redirect('/')

# -----------------------------
# ADD SAMPLE REQUEST
# -----------------------------
@app.route('/add_sample_request')
def add_sample_request():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Maintenance_Requests
    (
        employee_id,
        asset_id,
        technician_id,
        issue_description,
        request_date,
        status
    )

    VALUES
    (
        1,
        1,
        1,
        'Air conditioner not working',
        '2026-05-16',
        'Pending'
    )
    """)

    conn.commit()
    conn.close()

    return redirect('/requests')
    
# -----------------------------
# RUN APP
# -----------------------------
if __name__ == '__main__':

    create_tables()

    app.run(debug=True)