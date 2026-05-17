import requests
from flask import request, session, redirect, url_for, render_template, Response

from commands import AddFlowerCommand, UpdateFlowerCommand, DeleteFlowerCommand
from exporters import JsonExport, CsvExport


class FlowerController:
    """
    Controller layer — handles HTTP request parsing, session management,
    and delegates all business logic to the service layer.
    """

    def __init__(self, flower_service, query_service, repo):
        self.flower_service = flower_service
        self.query_service = query_service
        self.repo = repo

    def index(self):
        if 'role' in session:
            return redirect(url_for('catalog_view'))
        return render_template('login.html')

    def login(self):
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            try:
                resp = requests.post(
                    'http://localhost:5001/login',
                    json={'email': email, 'password': password}
                )
                if resp.status_code == 200:
                    user_data = resp.json()
                    session['role'] = user_data['role']
                    session['email'] = user_data['email']
                    session['username'] = user_data['name']
                    return redirect(url_for('catalog_view'))
                return render_template('login.html', error="Invalid credentials")
            except Exception:
                return "Identity Service is not running on port 5001", 503
        return render_template('login.html')

    def visitor_access(self):
        session['role'] = 'Visitor'
        session['email'] = 'guest@flowershop.com'
        return redirect(url_for('catalog_view'))

    def catalog_view(self):
        role = session.get('role')
        if not role:
            return redirect(url_for('index'))
        flowers = self.query_service.get_catalog(
            request.args.get('color'),
            request.args.get('sort')
        )
        return render_template('home.html', flowers=flowers, role=role)

    def add(self):
        user_role = session.get('role', 'Visitor')
        if user_role != 'Admin':
            return "Access Denied: Admins Only", 403

        if request.method == 'POST':
            try:
                self.flower_service.add_new_flower(
                    user_role,
                    session.get('email'),
                    request.form['name'],
                    request.form['color'],
                    float(request.form['price']),
                    int(request.form['stock'])
                )
                return redirect(url_for('catalog_view'))
            except ValueError as e:
                return render_template('add_flower.html', error=str(e))

        return render_template('add_flower.html')

    def update_stock(self, flower_id):
        new_stock = int(request.form.get('stock'))
        try:
            self.flower_service.update_flower_stock(
                session.get('role'),
                session.get('email'),
                flower_id,
                new_stock
            )
        except ValueError as e:
            flowers = self.query_service.get_catalog()
            return render_template('home.html', flowers=flowers,
                                   role=session.get('role'), error=str(e))
        return redirect(url_for('catalog_view'))

    def edit_flower(self, flower_id):
        flower = self.repo.get_by_id(flower_id)
        if not flower:
            return "Flower not found", 404

        if request.method == 'POST':
            try:
                price = float(request.form.get('price'))
                stock = int(request.form.get('stock'))
                if price <= 0:
                    raise ValueError("Price must be greater than 0.")
                if stock < 0:
                    raise ValueError("Stock quantity cannot be negative.")
                cmd = UpdateFlowerCommand(
                    self.repo,
                    flower_id,
                    request.form.get('name'),
                    request.form.get('color'),
                    price,
                    stock
                )
                self.flower_service.execute_command(cmd)
                return redirect(url_for('catalog_view'))
            except ValueError as e:
                return render_template('edit_flower.html', flower=flower,
                                       role=session.get('role'), error=str(e))

        return render_template('edit_flower.html', flower=flower, role=session.get('role'))

    def delete_flower(self, flower_id):
        self.flower_service.delete_flower(
            session.get('role'),
            session.get('email'),
            flower_id
        )
        return redirect(url_for('catalog_view'))

    def export_data(self, fmt):
        flowers = self.query_service.get_catalog()
        strategies = {'json': JsonExport(), 'csv': CsvExport()}
        if fmt in strategies:
            return Response(
                strategies[fmt].export(flowers),
                mimetype='application/octet-stream'
            )
        return "Invalid Format", 400

    def logout(self):
        session.clear()
        return redirect(url_for('index'))
