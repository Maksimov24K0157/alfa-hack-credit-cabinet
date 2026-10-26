from backend import crud
import sqlite3
from flask import Flask, jsonify
from json import dumps
def to_dict(orm_row):
    if orm_row is None:
        return None
    dictionary = orm_row.__dict__
    dictionary.pop("_sa_instance_state")
    return dictionary

def create_application():
    data = request.json
    user_id = data.get('userId')
    amount = data.get('amount')
    term = data.get('term')
    purpose = data.get('purpose')
    
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT RiskLevel FROM users WHERE UserID = ?', (user_id,))
    risk_level = cursor.fetchone()[0]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO applications (UserID, CompanyID, Requested_amount, Term_months, Loan_purpose, Status, Created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 1, amount, term, purpose, risk_level, created_at))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

a = get_loans(1)
for aa in a:
    for i in aa.keys():
        print(f"{i}: {aa[i]}")
    print()
#print(get_user("ivanov@mail.ru"))