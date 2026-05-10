from flask import Flask, render_template, request, redirect, url_for, session, Response
from repositories import FlowerRepository, UserRepository
from services import FlowerService, NotificationService, UserService
from exporters import JsonExport, CsvExport, XmlExport

app = Flask(__name__)
app.secret_key = 'flower'  #

flower_repo = FlowerRepository()
user_repo = UserRepository()

flower_service = FlowerService(flower_repo)
user_service = UserService(user_repo)
notif_service = NotificationService()

flower_service.attach(notif_service)


@app.route('/')
def index():
    """Landing Page: Only redirects if a role is actively in session."""
    if 'role' in session:
        return redirect(url_for('catalog_view'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user_data = user_service.login(email, password)

    print(f"DEBUG: Login Attempt for {email}. Result: {user_data}")
    if user_data:
        session['role'] = user_data['role']
        session['email'] = user_data['email']
        session['username'] = user_data['name']
        return redirect(url_for('catalog_view'))
    return render_template('login.html', error="Invalid credentials")


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

    flowers = flower_service.get_catalog(request.args.get('color'), request.args.get('sort'))
    return render_template('home.html', flowers=flowers, role=role)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
def add_flower():
    user_role = session.get('role', 'Visitor')
    if user_role != 'Admin':  #
        return "Access Denied: Admins Only", 403

    if request.method == 'POST':
        try:
            flower_service.add_new_flower(
                user_role=user_role,
                user_email=session.get('email'),
                name=request.form['name'],
                color=request.form['color'],
                price=float(request.form['price']),
                stock=int(request.form['stock'])
            )
            return redirect(url_for('catalog_view'))  # FIXED
        except Exception as e:
            return f"Error adding flower: {str(e)}", 400

    return render_template('add_flower.html')


@app.route('/delete/<int:flower_id>', methods=['POST'])
def delete_flower(flower_id):
    flower_service.delete_flower(session.get('role'), session.get('email'), flower_id)
    return redirect(url_for('catalog_view'))  # FIXED


@app.route('/update-stock/<int:flower_id>', methods=['POST'])
def update_stock(flower_id):
    user_role = session.get('role', 'Visitor')
    user_email = session.get('email')
    new_stock = request.form.get('stock')

    try:
        flower_service.update_flower_stock(user_role, user_email, flower_id, int(new_stock))
        return redirect(url_for('catalog_view'))  # FIXED
    except PermissionError as e:
        return str(e), 403


@app.route('/edit/<int:flower_id>', methods=['GET', 'POST'])
def edit_flower(flower_id):
    user_role = session.get('role', 'Visitor')
    if user_role != 'Admin':  #
        return "Admins only", 403

    if request.method == 'POST':
        flower_service.update_flower_details(
            user_role, session.get('email'), flower_id,
            request.form['name'], request.form['color'],
            float(request.form['price']), int(request.form['stock'])
        )
        return redirect(url_for('catalog_view'))

    flower = flower_repo.get_by_id(flower_id)
    return render_template('edit_flower.html', flower=flower)


@app.route('/export/<fmt>')
def export_data(fmt):
    #
    flowers = flower_service.get_catalog(request.args.get('color'), request.args.get('sort'))
    strategies = {'json': JsonExport(), 'csv': CsvExport(), 'xml': XmlExport()}

    if fmt in strategies:
        return Response(strategies[fmt].export(flowers), mimetype='application/octet-stream',
                        headers={"Content-disposition": f"attachment; filename=export.{fmt}"})
    return "Invalid Format", 400


if __name__ == '__main__':
    app.run(debug=True)