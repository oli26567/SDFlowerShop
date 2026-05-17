from flask import Flask
from queries import FlowerQueryService
from repositories import FlowerRepository
from FlowerService import FlowerService, NotificationService
from controllers.flower_controller import FlowerController

app = Flask(__name__)
app.secret_key = 'flower'

repo = FlowerRepository()
query_service = FlowerQueryService(repo)
flower_service = FlowerService(repo, query_service)
flower_service.attach(NotificationService())

controller = FlowerController(flower_service, query_service, repo)

@app.route('/')
def index():
    return controller.index()


@app.route('/login', methods=['GET', 'POST'])
def login():
    return controller.login()


@app.route('/visitor-access')
def visitor_access():
    return controller.visitor_access()


@app.route('/catalog')
def catalog_view():
    return controller.catalog_view()


@app.route('/add', methods=['GET', 'POST'])
def add():
    return controller.add()


@app.route('/update-stock/<int:flower_id>', methods=['POST'])
def update_stock(flower_id):
    return controller.update_stock(flower_id)


@app.route('/edit/<int:flower_id>', methods=['GET', 'POST'])
def edit_flower(flower_id):
    return controller.edit_flower(flower_id)


@app.route('/delete/<int:flower_id>', methods=['POST'])
def delete_flower(flower_id):
    return controller.delete_flower(flower_id)


@app.route('/export/<fmt>')
def export_data(fmt):
    return controller.export_data(fmt)


@app.route('/logout')
def logout():
    return controller.logout()


if __name__ == '__main__':
    app.run(port=5002, debug=True)