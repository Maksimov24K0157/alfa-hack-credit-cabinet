from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime

from backend import crud
from ml.src import catboosting

app = Flask(__name__)

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/api/users')#!
def get_users():
    return jsonify(crud.get_all_emails())

@app.route('/api/user/<email>')#!
def get_user(email):
    user = crud.get_user_by_email(email)
    passport = crud.get_passport_by_id(user.passport_id)
    companies = crud.get_companies_by_user(user.user_id)
    if user:
        return jsonify({
            'userId': user.user_id, 'login': user.email, 'password': user.hash_password, 
            'name': user.name, 'surname': user.surname, 'patronymic': user.patronymic, 
            'phone': user.phone, 'inn': "NOT_IMPLEMENTED", 'company': "NOT_IMPLEMENTED",
            'salary': "NOT_PRESENT", 'risk': "NOT_PRESENT",
            'passportSeries': passport.series, 'passportNumber': passport.number,
            'passportIssuedBy': passport.issued_by, 'passportIssueDate': passport.issue_date,
            'passportCode': passport.code, 'registrationAddress': passport.registration_address,
            'birthDate': passport.birth_date
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/loans/<int:user_id>')#!
def get_loans(user_id):
    loans = crud.get_loans_by_user_id(user_id)
    result = []
    for loan in loans:
        application = crud.get_application_by_id(loan.application_id)
        if application is None:
            purpose = "Unknown"
        else:
            purpose = application.loan_purpose
        result.append({
            'id': loan.loan_id, 'purpose': purpose, 'amount': loan.amount, 'remaining': "NOT_PRESENT",
            'rate': loan.interest_rate, 'status': loan.status, 'term': loan.term_months, 'issue_date': loan.issue_date,
            'end_date': loan.end_date, 'monthly_payment': loan.monthly_payment, 'bank_name': "NOT_PRESENT", 'bank_icon': "NOT_PRESENT"
        })
    return jsonify(result)

@app.route('/api/applications', methods=['POST'])
def create_application():#TODO rewrite for company selection
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

@app.route('/api/offers/<int:user_id>', methods=['POST'])#TODO massive rewrite
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
    passport_id = crud.get_passport_by_id(crud.get_user_by_id(user_id).passport_id).id
    crud.update_user(user_id, phone= phone, name= name, surname= surname)
    crud.update_passport(passport_id, 
                         series= passportSeries, number= passportNumber, issued_by= passportIssuedBy, 
                         issue_date= passportIssueDate, code= passportCode, registration_address= registrationAddress,
                         birth_date= birthDate)
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

    #crud.create_loan() TODO get application id in this function
    cursor.execute('''
        INSERT INTO loans (UserID, CompanyID, Purpose, Amount, Remaining_Amount, Interest_rate, Status, Term_months, issue_date, end_date, monthly_payment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 1, purpose, amount, amount, rate, 'Активен', term, issue_date, end_date, monthly_payment))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})