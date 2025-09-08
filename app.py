from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'votre_cle_secrete'

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    amount REAL,
                    category TEXT,
                    date TEXT,
                    description TEXT
                )''')
    conn.commit()
    conn.close()

# Route principale
@app.route('/')
def index():
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions ORDER BY date DESC")
    transactions = c.fetchall()
    
    total_income = sum(t[2] for t in transactions if t[1] == 'income')
    total_expense = sum(t[2] for t in transactions if t[1] == 'expense')
    balance = total_income - total_expense

    # Calcul de la répartition des dépenses par catégorie
    breakdown = {}
    for t in transactions:
        if t[1] == 'expense':
            cat = t[3]
            breakdown[cat] = breakdown.get(cat, 0) + t[2]
    conn.close()
    return render_template("index.html", 
                           transactions=transactions, 
                           balance=balance, 
                           total_income=total_income, 
                           total_expense=total_expense,
                           breakdown=breakdown)

# Route pour afficher le formulaire d'ajout (page dédiée)
@app.route('/add_transaction')
def add_transaction():
    return render_template("add_transaction.html")

# Route pour ajouter une transaction (traitement du formulaire)
@app.route('/add', methods=['POST'])
def add():
    data = request.form
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (type, amount, category, date, description) VALUES (?, ?, ?, ?, ?)", 
              (data['type'], float(data['amount']), data['category'], data['date'], data['description']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route pour supprimer une transaction
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route pour afficher le formulaire d'édition
@app.route('/edit/<int:id>')
def edit_transaction(id):
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id=?", (id,))
    transaction = c.fetchone()
    conn.close()
    return render_template("edit_transaction.html", transaction=transaction)

# Route pour traiter l'édition d'une transaction
@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    data = request.form
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    c.execute("UPDATE transactions SET type=?, amount=?, category=?, date=?, description=? WHERE id=?", 
              (data['type'], float(data['amount']), data['category'], data['date'], data['description'], id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)