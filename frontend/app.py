from flask import Flask, render_template, jsonify, request
from backend import crud
from ml.src import catboosting
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/api/users')
def get_users():
    return jsonify(crud.get_all_emails())

@app.route('/api/user/<email>')
def get_user(email):
    user = crud.get_user_by_email(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    passport = crud.get_passport_by_id(user.passport_id) if user.passport_id else None
    companies = crud.get_companies_by_user(user.user_id)
    
    company_names = ", ".join([c.name for c in companies]) if companies else "Нет компании"
    inn = companies[0].inn if companies else "NOT_PRESENT"
    revenue = float(companies[0].revenue_last_year) if companies else 0

    return jsonify({
        'userId': user.user_id, 
        'login': user.email, 
        'password': user.hash_password, 
        'name': user.name, 
        'surname': user.surname, 
        'patronymic': user.patronymic or "", 
        'phone': user.phone, 
        'inn': inn, 
        'company': company_names,
        'salary': revenue,
        'risk': "NOT_PRESENT", 
        'passportSeries': passport.series if passport else "",
        'passportNumber': passport.number if passport else "",
        'passportIssuedBy': passport.issued_by if passport else "",
        'passportIssueDate': passport.issue_date.strftime("%Y-%m-%d") if passport and passport.issue_date else "",
        'passportCode': passport.code if passport else "",
        'registrationAddress': passport.registration_address if passport else "",
        'birthDate': passport.birth_date.strftime("%Y-%m-%d") if passport and passport.birth_date else ""
    })

# НОВЫЙ ЭНДПОИНТ ДЛЯ ПОЛУЧЕНИЯ КОМПАНИЙ (для выпадающего списка)
@app.route('/api/user_companies/<int:user_id>')
def get_user_companies(user_id):
    companies = crud.get_companies_by_user(user_id)
    result = []
    for c in companies:
        result.append({
            'company_id': c.company_id,
            'name': c.name,
            'inn': c.inn
        })
    return jsonify(result)

@app.route('/api/loans/<int:user_id>')
def get_loans(user_id):
    loans = crud.get_loans_by_user_id(user_id)
    result = []
    for loan in loans:
        application = crud.get_application_by_id(loan.application_id)
        purpose = application.loan_purpose if application else "Кредит на бизнес"
        
        company = crud.get_company_by_id(loan.company_id)
        company_name = company.name if company else "Неизвестная компания"
        
        result.append({
            'id': loan.loan_id, 
            'purpose': purpose, 
            'amount': float(loan.amount), 
            'remaining': "NOT_PRESENT", 
            'rate': float(loan.interest_rate), 
            'status': loan.status, 
            'term': loan.term_months, 
            'issue_date': loan.issue_date.strftime("%Y-%m-%d") if loan.issue_date else "",
            'end_date': loan.end_date.strftime("%Y-%m-%d") if loan.end_date else "", 
            'monthly_payment': float(loan.monthly_payment), 
            'bank_name': "Альфа-Банк",
            'company_name': company_name
        })
    return jsonify(result)

@app.route('/api/applications', methods=['POST'])
def create_application():
    data = request.json
    user_id = data.get('userId')
    amount = data.get('amount')
    term = data.get('term')
    purpose = data.get('purpose')
    company_id = data.get('companyId')
    
    if not company_id:
        return jsonify({'error': 'Company ID is required'}), 400
    
    application = crud.create_application(
        user_id=user_id, 
        company_id=int(company_id), 
        amount=amount, 
        term=term, 
        purpose=purpose
    )
    
    return jsonify({'success': True, 'applicationId': application.application_id})

def calc_rate(risk_level, min_rate, max_rate):
    if risk_level == "low_risk":
        return min_rate
    elif risk_level == "medium_risk":
        return min_rate*0.5 + max_rate*0.5
    elif risk_level == "high_risk":
        return min_rate*0.2 + max_rate*0.8
    else:
        return max_rate
def pick_offers(risk_eval, req_amount, req_term):
    risk_numerate = {'low_risk':0, 'medium_risk':1, 'high_risk':2, 'very_high_risk':3}
    products = crud.get_all_products()
    selected = []
    for product in products:
        if risk_numerate[risk_eval["risk_class"]] <= risk_numerate[offer.max_allowed_risk_levels]:
            amount_priority = True
            if req_amount > product.max_amount:
                req_amount = product.max_amount
            elif req_amount < product.min_amount:
                req_amount = product.min_amount
            offer = {
                "amount": req_amount,
                "term": req_term,
                "rate": calc_rate(risk_eval["risk_class"], product.min_rate, product.max_rate),
                "bank_name": "Альфа-Банк",
                "amount_priority": amount_priority
            }
            selected.append(offer)
    selected.sort(key = lambda x: x["rate"])
    return selected

@app.route('/api/offers/<int:user_id>', methods=['POST'])
def get_offers(user_id):
    try:
        data = request.json
        req_amount = float(data.get('amount', 0))
        req_term = int(data.get('term', 0))

        companies = crud.get_companies_by_user(user_id)

        company_cat_data = {
                "company_age": 5,
                "revenue_last_year": 10000000,
                "net_profit": 1000000,
                "existing_debt": 2000000,
                "requested_amount": req_amount,
                "industry_okved": "IT",
                "credit_history_status": "good",
                "loan_purpose": "working_capital",
        }

        risk_eval = catboosting.predict_risk(company_cat_data)
        offers = pick_offers(risk_eval, req_amount, req_term)

        return jsonify({'offers': offers, 'isAlternative': False})
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/issue_loan', methods=['POST'])
def issue_loan():
    data = request.json
    user_id = data.get('userId')
    application_id = data.get('applicationId')
    
    # Используем Decimal для избежания ошибки типов в SQLAlchemy
    amount = Decimal(str(data.get('amount', 0)))
    term = int(data.get('term', 0))
    rate = Decimal(str(data.get('rate', 0)))
    monthly_payment = Decimal(str(data.get('monthly_payment', 0)))
    
    user = crud.get_user_by_id(user_id)
    if user:
        crud.update_user(user_id, phone=data.get('phone'), name=data.get('name'), surname=data.get('surname'))
        if user.passport_id:
            crud.update_passport(
                user.passport_id, 
                series=data.get('passportSeries'), 
                number=data.get('passportNumber'), 
                issued_by=data.get('passportIssuedBy'), 
                issue_date=datetime.strptime(data.get('passportIssueDate'), "%Y-%m-%d") if data.get('passportIssueDate') else None,
                code=data.get('passportCode'), 
                registration_address=data.get('registrationAddress'),
                birth_date=datetime.strptime(data.get('birthDate'), "%Y-%m-%d") if data.get('birthDate') else None
            )
            
    companies = crud.get_companies_by_user(user_id)
    company_id = companies[0].company_id if companies else 1

    crud.create_loan(
        application_id=application_id,
        company_id=company_id,
        amount=amount,
        rate=rate,
        term=term,
        monthly_payment=monthly_payment
    )
    
    return jsonify({'success': True})

