from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime

from backend import crud
from ml.src import catboosting

app = Flask(__name__)

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/api/users')
def get_users():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Email FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/user/<email>')
def get_user(email):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE Email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({
            'userId': user[0], 'login': user[1], 'password': user[3], 
            'name': user[5], 'surname': user[6], 'patronymic': user[7], 
            'phone': user[2], 'inn': user[8], 'company': user[9],
            'salary': user[10], 'risk': user[11],
            'passportSeries': user[12], 'passportNumber': user[13],
            'passportIssuedBy': user[14], 'passportIssueDate': user[15],
            'passportCode': user[16], 'registrationAddress': user[17],
            'birthDate': user[18]
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/loans/<int:user_id>')
def get_loans(user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.*, c.Name as BankName, c.Icon_Text 
        FROM loans l JOIN companies c ON l.CompanyID = c.CompanyID
        WHERE l.UserID = ?
    ''', (user_id,))
    loans = cursor.fetchall()
    conn.close()
    
    result = []
    for loan in loans:
        result.append({
            'id': loan[0], 'purpose': loan[3], 'amount': loan[4], 'remaining': loan[5],
            'rate': loan[6], 'status': loan[7], 'term': loan[8], 'issue_date': loan[9],
            'end_date': loan[10], 'monthly_payment': loan[11], 'bank_name': loan[12], 'bank_icon': loan[13]
        })
    return jsonify(result)

@app.route('/api/applications', methods=['POST'])
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

@app.route('/api/offers/<int:user_id>', methods=['POST'])
def get_offers(user_id):
    try:
        data = request.json
        req_amount = float(data.get('amount', 0))
        req_term = int(data.get('term', 0))
        req_purpose = data.get('purpose', '')

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT RiskLevel FROM users WHERE UserID = ?', (user_id,))
        result_user = cursor.fetchone()
        
        if not result_user:
            return jsonify({'error': 'User not found'}), 404
            
        risk_level = result_user[0]
        
        if risk_level == 'Критический':
            allowed = ['cat1']
        elif risk_level == 'Высокий':
            allowed = ['cat1', 'cat2']
        elif risk_level == 'Средний':
            allowed = ['cat1', 'cat2', 'cat3']
        else:
            allowed = ['cat1', 'cat2', 'cat3', 'cat4']
            
        placeholders = ','.join(['?'] * len(allowed))
        
        # +-20% допуск
        min_amount = req_amount * 0.8
        max_amount = req_amount * 1.2
        min_term = int(req_term * 0.8)
        max_term = int(req_term * 1.2)

        exact_query = f'''
            SELECT o.*, c.Name as BankName, c.Icon_Text 
            FROM offers o
            JOIN companies c ON o.CompanyID = c.CompanyID
            WHERE o.Risk_category IN ({placeholders}) 
              AND o.Purpose = ? 
              AND o.Amount BETWEEN ? AND ? 
              AND o.Term_months BETWEEN ? AND ?
        '''
        params_exact = allowed + [req_purpose, min_amount, max_amount, min_term, max_term]
        cursor.execute(exact_query, params_exact)
        exact_offers = cursor.fetchall()
        
        result = []
        is_alternative = False
        
        if exact_offers:
            for offer in exact_offers:
                result.append({
                    'id': offer[0], 'purpose': offer[2], 'amount': offer[3], 'term': offer[4],
                    'rate': offer[5], 'bank_name': offer[7], 'bank_icon': offer[8]
                })
            result.sort(key=lambda x: x['rate'])
        else:
            alt_query = f'''
                SELECT o.*, c.Name as BankName, c.Icon_Text 
                FROM offers o
                JOIN companies c ON o.CompanyID = c.CompanyID
                WHERE o.Risk_category IN ({placeholders}) 
                  AND o.Purpose = ?
            '''
            params_alt = allowed + [req_purpose]
            cursor.execute(alt_query, params_alt)
            all_offers = cursor.fetchall()
            
            for offer in all_offers:
                if offer[3] <= req_amount or offer[4] <= req_term:
                    result.append({
                        'id': offer[0], 'purpose': offer[2], 'amount': offer[3], 'term': offer[4],
                        'rate': offer[5], 'bank_name': offer[7], 'bank_icon': offer[8]
                    })
            
            result.sort(key=lambda x: (abs(x['amount'] - req_amount), x['rate']))
            result = result[:10]
            is_alternative = True

        conn.close()
        return jsonify({'offers': result, 'isAlternative': is_alternative})
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/issue_loan', methods=['POST'])
def issue_loan():
    data = request.json
    user_id = data.get('userId')
    amount = float(data.get('amount', 0))
    term = int(data.get('term', 0))
    purpose = data.get('purpose')
    rate = float(data.get('rate', 0))
    monthly_payment = float(data.get('monthly_payment', 0))
    
    # Данные пользователя (включая паспорт)
    name = data.get('name')
    surname = data.get('surname')
    patronymic = data.get('patronymic')
    phone = data.get('phone')
    inn = data.get('inn')
    company = data.get('company')
    passportSeries = data.get('passportSeries')
    passportNumber = data.get('passportNumber')
    passportIssuedBy = data.get('passportIssuedBy')
    passportIssueDate = data.get('passportIssueDate')
    passportCode = data.get('passportCode')
    registrationAddress = data.get('registrationAddress')
    birthDate = data.get('birthDate')
    
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    # Обновляем ВСЕ данные пользователя (включая паспортные)
    cursor.execute('''
        UPDATE users SET 
            Name = ?, Surname = ?, Patronymic = ?, Phone = ?, INN = ?, Company = ?,
            PassportSeries = ?, PassportNumber = ?, PassportIssuedBy = ?, 
            PassportIssueDate = ?, PassportCode = ?, RegistrationAddress = ?, BirthDate = ?
        WHERE UserID = ?
    ''', (name, surname, patronymic, phone, inn, company, 
          passportSeries, passportNumber, passportIssuedBy, 
          passportIssueDate, passportCode, registrationAddress, birthDate, user_id))
    
    # Создаем запись о кредите
    issue_date = datetime.now().strftime("%Y-%m-%d")
    end_date_dt = datetime.now()
    month = end_date_dt.month - 1 + term
    year = end_date_dt.year + month // 12
    month = month % 12 + 1
    day = min(end_date_dt.day, 28)
    end_date = f"{year}-{month:02d}-{day:02d}"
    
    cursor.execute('''
        INSERT INTO loans (UserID, CompanyID, Purpose, Amount, Remaining_Amount, Interest_rate, Status, Term_months, issue_date, end_date, monthly_payment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 1, purpose, amount, amount, rate, 'Активен', term, issue_date, end_date, monthly_payment))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})