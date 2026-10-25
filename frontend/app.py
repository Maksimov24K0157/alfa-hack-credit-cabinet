from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    # Таблица пользователей (с паспортными данными)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            UserID INTEGER PRIMARY KEY,
            Email TEXT, Phone TEXT, HashPassword TEXT, HashSalt TEXT,
            Name TEXT, Surname TEXT, Patronymic TEXT, INN TEXT, Company TEXT,
            Salary REAL, RiskLevel TEXT,
            PassportSeries TEXT, PassportNumber TEXT, PassportIssuedBy TEXT,
            PassportIssueDate TEXT, PassportCode TEXT, RegistrationAddress TEXT,
            BirthDate TEXT
        )
    ''')
    
    # Таблица банков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            CompanyID INTEGER PRIMARY KEY, Name TEXT, Icon_Text TEXT
        )
    ''')
    
    # Таблица выданных кредитов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            LoanID INTEGER PRIMARY KEY AUTOINCREMENT, 
            UserID INTEGER, CompanyID INTEGER,
            Purpose TEXT, Amount REAL, Remaining_Amount REAL, Interest_rate REAL,
            Status TEXT, Term_months INTEGER, issue_date TEXT, end_date TEXT, monthly_payment REAL
        )
    ''')
    
    # Таблица заявок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            ApplicationID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER, CompanyID INTEGER, Requested_amount REAL,
            Term_months INTEGER, Loan_purpose TEXT, Status TEXT, Created_at TEXT
        )
    ''')
    
    # Таблица предложений банков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            OfferID INTEGER PRIMARY KEY, CompanyID INTEGER, Purpose TEXT,
            Amount REAL, Term_months INTEGER, Interest_rate REAL, Risk_category TEXT
        )
    ''')
    
    # Очищаем только пользователей, банки и предложения.
    # ВАЖНО: loans и applications НЕ ОЧИЩАЕМ, чтобы история сохранялась!
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM companies')
    cursor.execute('DELETE FROM offers')
    
    # Данные пользователей (с паспортами)
    users = [
        (1, 'ivanov@mail.ru', '+79991112233', 'pass1', 'salt1', 'Иван', 'Иванов', 'Иванович', '123456789012', 'ООО "Ромашка"', 75000, 'Низкий', '4510', '123456', 'ОВД г. Москвы', '2010-05-15', '770-001', 'г. Москва, ул. Ленина, д. 1', '1990-01-01'),
        (2, 'petrova@mail.ru', '+79992223344', 'pass2', 'salt2', 'Анна', 'Петрова', 'Сергеевна', '234567890123', 'ИП Петрова', 120000, 'Средний', '4515', '654321', 'УФМС г. Санкт-Петербурга', '2015-08-20', '780-002', 'г. Санкт-Петербург, ул. Мира, д. 10', '1985-05-12'),
        (3, 'sidorov@mail.ru', '+79993334455', 'pass3', 'salt3', 'Сергей', 'Сидоров', 'Петрович', '345678901234', 'Самозанятый', 45000, 'Высокий', '4520', '112233', 'ОВД г. Казани', '2020-02-10', '160-003', 'г. Казань, ул. Баумана, д. 5', '1995-11-30'),
        (4, 'smirnov@mail.ru', '+79994445566', 'pass4', 'salt4', 'Алексей', 'Смирнов', 'Алексеевич', '456789012345', 'ООО "Тяжмаш"', 30000, 'Критический', '4525', '445566', 'ОВД г. Екатеринбурга', '2025-01-15', '660-004', 'г. Екатеринбург, ул. Гагарина, д. 20', '2000-07-07'),
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', users)
    
    # Данные банков (только Альфа)
    companies = [
        (1, 'Альфа-Банк', 'А')
    ]
    cursor.executemany('INSERT INTO companies VALUES (?, ?, ?)', companies)
    
    # Проверяем: если кредитов вообще нет (первый запуск), добавляем тестовый
    cursor.execute('SELECT COUNT(*) FROM loans')
    if cursor.fetchone()[0] == 0:
        loans = [
            (1, 1, 1, 'Ипотека', 5000000, 4788120, 8.5, 'Активен', 240, '2019-01-01', '2039-01-01', 43400)
        ]
        cursor.executemany('INSERT INTO loans (LoanID, UserID, CompanyID, Purpose, Amount, Remaining_Amount, Interest_rate, Status, Term_months, issue_date, end_date, monthly_payment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', loans)
    
    # Генерация предложений (256 штук)
    purposes = [
        "Ремонт", "Автомобиль", "Образование", "Ипотека", 
        "Первоначальный взнос", "Открытие бизнеса", "Потребительский", "Кредитная карта"
    ]
    
    offers = []
    offer_id = 1
    
    for purpose in purposes:
        # Категория 1 (Критический риск)
        for i in range(8):
            amount = 30000 + (i * 10000)
            term = 6 + i
            rate = 25.0 - (i * 0.5)
            offers.append((offer_id, 1, purpose, amount, term, rate, 'cat1'))
            offer_id += 1
            
        # Категория 2 (Высокий риск)
        for i in range(8):
            amount = 50000 + (i * 35000)
            term = 12 + (i * 2)
            rate = 21.0 - (i * 0.4)
            offers.append((offer_id, 1, purpose, amount, term, rate, 'cat2'))
            offer_id += 1

        # Категория 3 (Средний риск)
        for i in range(8):
            amount = 100000 + (i * 120000)
            term = 24 + (i * 6)
            rate = 16.0 - (i * 0.4)
            offers.append((offer_id, 1, purpose, amount, term, rate, 'cat3'))
            offer_id += 1

        # Категория 4 (Низкий риск)
        for i in range(8):
            amount = 500000 + (i * 600000)
            term = 36 + (i * 12)
            rate = 12.0 - (i * 0.4)
            offers.append((offer_id, 1, purpose, amount, term, rate, 'cat4'))
            offer_id += 1

    cursor.executemany('INSERT INTO offers VALUES (?, ?, ?, ?, ?, ?, ?)', offers)
    
    conn.commit()
    conn.close()

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)