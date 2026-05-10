import requests
from flask import Flask, render_template, request, redirect, url_for, session, Response
from commands import AddFlowerCommand, UpdateStockCommand
from queries import FlowerQueryService
from repositories import FlowerRepository
from FlowerService import FlowerService, NotificationService
from exporters import JsonExport, CsvExport

app = Flask(__name__)
app.secret_key = 'flower'

repo = FlowerRepository()
query_service = FlowerQueryService(repo)
flower_service = FlowerService(repo, query_service)
flower_service.attach(NotificationService())

@app.route('/')
def index():
    if 'role' in session:
        return redirect(url_for('catalog_view'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            resp = requests.post('http://localhost:5001/login',
                                 json={'email': email, 'password': password})
            if resp.status_code == 200:
                user_data = resp.json()
                session['role'] = user_data['role']
                session['email'] = user_data['email']
                session['username'] = user_data['name']
                return redirect(url_for('catalog_view'))
            return render_template('login.html', error="Invalid credentials")
        except:
            return "Identity Service is not running on port 5001", 503
    return render_template('login.html')

@app.route('/visitor-access')
def visitor_access():
    session['role'] = 'Visitor'
    session['email'] = 'guest@flowershop.com'
    return redirect(url_for('catalog_view'))

@app.route('/catalog')
def catalog_view():
    role = session.get('role')
    if not role:
        return redirect(url_for('index'))
    flowers = query_service.get_catalog(request.args.get('color'), request.args.get('sort'))
    return render_template('home.html', flowers=flowers, role=role)

@app.route('/add', methods=['GET', 'POST']) # Add 'GET' here
def add():
    user_role = session.get('role', 'Visitor')
    if user_role != 'Admin':
        return "Access Denied: Admins Only", 403

    if request.method == 'POST':
        flower_service.add_new_flower(
            user_role, session.get('email'),
            request.form['name'], request.form['color'],
            float(request.form['price']), int(request.form['stock'])
        )
        return redirect(url_for('catalog_view'))

    return render_template('add_flower.html')

@app.route('/update-stock/<int:flower_id>', methods=['POST'])
def update_stock(flower_id):
    # Uses FlowerService which executes UpdateStockCommand
    new_stock = int(request.form.get('stock'))
    flower_service.update_flower_stock(session.get('role'), session.get('email'), flower_id, new_stock)
    return redirect(url_for('catalog_view'))

@app.route('/export/<fmt>')
def export_data(fmt):
    flowers = query_service.get_catalog()
    strategies = {'json': JsonExport(), 'csv': CsvExport()} # Template Pattern
    if fmt in strategies:
        return Response(strategies[fmt].export(flowers), mimetype='application/octet-stream')
    return "Invalid Format", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))