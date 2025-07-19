from flask import blueprints
from flask import Flask, render_template, request, redirect, url_for
import json , os
from  datetime import datetime
from typing import Any
DATA_FILE = 'data/clients.json'
main = blueprints.Blueprint('main', __name__)

# Load/save helpers
def load_clients() -> list[dict|Any]:
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

@main.route('/mark_paid/<int:id>', methods=['POST'])
def mark_paid(id):
    clients = load_clients()
    client = next((c for c in clients if c['id'] == id), None)
    if not client:
        return "Client not found", 404
    client['status'] = 'paid'
    client['date_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M')
    save_clients(clients)
    return redirect(url_for('main.index'))

@main.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        clients= load_clients()
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M')
        new_client = {
            "id": get_next_id(clients),
            "name": request.form['name'],
            "items": request.form['items'],
            "amount": float(request.form['amount']),
            "status": request.form['status'],
            "date_added": now_str,
            "date_updated": now_str,
            "is_trashed": False
        }
        clients.append(new_client)
        save_clients(clients)
        return redirect(url_for('main.index'))
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
        client['date_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M')
        save_clients(clients)
        return redirect(url_for('main.index'))

    return render_template('edit.html', client=client)

@main.route('/soft_delete/<int:id>', methods=['POST'])
def soft_delete(id):
    clients = load_clients()
    for c in clients:
        if c['id'] == id:
            c['is_trashed'] = True
            break
    save_clients(clients)
    return redirect(url_for('main.index'))

@main.route('/restore/<int:id>', methods=['GET', 'POST'])
def restore(id):
    clients = load_clients()
    for c in clients:
        if c['id'] == id:
            c['is_trashed'] = False
            break
    save_clients(clients)
    return redirect(url_for('main.trash'))

@main.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    clients = load_clients()
    deleted_client = next((c for c in clients if c['id'] == id), None)

    if deleted_client:
        # Remove from main list
        clients = [c for c in clients if c['id'] != id]
        save_clients(clients)

        # Load archive.json and append the deleted client
        try:
            with open('data/archive.json', 'r') as f:
                archive = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            archive = []

        archive.append(deleted_client)

        with open('data/archive.json', 'w') as f:
            json.dump(archive, f, indent=2)

    return redirect(url_for('main.trash'))
