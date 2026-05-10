from flask import Flask, render_template, request, redirect, url_for, session
from repositories import FlowerRepository
from services import FlowerService

app = Flask(__name__)
app.secret_key = 'flower'

repo = FlowerRepository()
service = FlowerService(repo)
@app.route('/')
def home():
    user_role = session.get('role', 'Visitor')

    selected_color = request.args.get('color')
    selected_sort = request.args.get('sort')

    flowers = service.get_catalog(user_role, selected_color, selected_sort)
    return render_template('home.html', flowers=flowers, role=user_role)

@app.route('/delete/<int:flower_id>', methods=['POST'])
def delete_flower(flower_id):
    user_role = session.get('role', 'Visitor')
    try:
        service.delete_flower(user_role, flower_id)
    except PermissionError as e:
        return str(e), 403
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        if user == "admin":
            session['role'] = 'Admin'
            session['username'] = 'Admin User'
        elif user == "florist":
            session['role'] = 'Florist'
            session['username'] = 'Florist User'
        else:
            session['role'] = 'Visitor'
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add_flower():
    user_role = session.get('role', 'Visitor')
    if request.method == 'POST':
        try:
            service.add_new_flower(
                user_role,
                request.form['name'],
                request.form['color'],
                float(request.form['price']),
                int(request.form['stock'])
            )
            return redirect(url_for('home'))
        except PermissionError as e:
            return str(e), 403
    return render_template('add_flower.html')

if __name__ == '__main__':
    app.run(debug=True)