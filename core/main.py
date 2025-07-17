from flask import blueprints
from flask import Flask, render_template, request, redirect, url_for
import json , os
from  datetime import datetime

DATA_FILE = 'data/clients.json'
main = blueprints.Blueprint('main', __name__)

# Load/save helpers
def load_clients():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)
# Ensure data folder and file exist
os.makedirs('data', exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)


def save_clients(clients):
    with open(DATA_FILE, 'w') as f:
        json.dump(clients, f, indent=4)

def get_next_id(clients):
    return max([c["id"] for c in clients], default=0) + 1

@main.route('/')
def index():
    clients = [c for c in load_clients() if not c['is_trashed']]
    return render_template('index.html', clients=clients)

@main.route('/trash')
def trash():
    clients = [c for c in load_clients() if c['is_trashed']]
    return render_template('trash.html', clients=clients)

@main.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        clients = load_clients()
        new_client = {
            "id": get_next_id(clients),
            "name": request.form['name'],
            "items": request.form['items'],
            "amount": float(request.form['amount']),
            "status": request.form['status'],
            "date_added": datetime.now().isoformat(),
            "date_updated": datetime.now().isoformat(),
            "is_trashed": False
        }
        clients.mainend(new_client)
        save_clients(clients)
        return redirect(url_for('index'))
    return render_template('add.html')

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    clients = load_clients()
    client = next((c for c in clients if c['id'] == id), None)
    if not client:
        return "Client not found", 404

    if request.method == 'POST':
        client['name'] = request.form['name']
        client['items'] = request.form['items']
        client['amount'] = float(request.form['amount'])
        client['status'] = request.form['status']
        client['date_updated'] = datetime.now().isoformat()
        save_clients(clients)
        return redirect(url_for('index'))

    return render_template('edit.html', client=client)

@main.route('/soft_delete/<int:id>')
def soft_delete(id):
    clients = load_clients()
    for c in clients:
        if c['id'] == id:
            c['is_trashed'] = True
            break
    save_clients(clients)
    return redirect(url_for('index'))

@main.route('/restore/<int:id>')
def restore(id):
    clients = load_clients()
    for c in clients:
        if c['id'] == id:
            c['is_trashed'] = False
            break
    save_clients(clients)
    return redirect(url_for('trash'))

@main.route('/delete/<int:id>')
def delete(id):
    clients = load_clients()
    clients = [c for c in clients if c['id'] != id]
    save_clients(clients)
    return redirect(url_for('trash'))
