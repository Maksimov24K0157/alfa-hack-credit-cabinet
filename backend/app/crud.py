# type: ignore
from database import SessionLocal
from models import users, companies, user_companies, applications, risk_assesments, products, loan_offers, loans
from datetime import datetime, timezone

# ==========================================
# 1. ПОЛЬЗОВАТЕЛИ (USERS)
# ==========================================
def create_user(email: str, phone: str, hash_password: str, hash_salt: str, name: str, surname: str, patronymic: str = None):
    db = SessionLocal()
    try:
        new_user = users(
            email=email, phone=phone, hash_password=hash_password, hash_salt=hash_salt,
            name=name, surname=surname, patronymic=patronymic
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()

def get_user_by_id(user_id: int):
    db = SessionLocal()
    try:
        return db.query(users).filter(users.user_id == user_id).first()
    finally:
        db.close()

def get_user_by_email(email: str):
    db = SessionLocal()
    try:
        return db.query(users).filter(users.email == email).first()
    finally:
        db.close()

def update_user(user_id: int, **kwargs):
    db = SessionLocal()
    try:
        user = db.query(users).filter(users.user_id == user_id).first()
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.commit()
            return user
        return None
    finally:
        db.close()

def delete_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(users).filter(users.user_id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    finally:
        db.close()


# ==========================================
# 2. КОМПАНИИ (COMPANIES)
# ==========================================
def create_company(entity_type: str, inn: str, company_age: int, industry_okved: str, revenue_last_year: float, net_profit: float, existing_debt: float, credit_history_status: str):
    db = SessionLocal()
    try:
        new_company = companies(
            entity_type=entity_type, inn=inn, company_age=company_age, industry_okved=industry_okved,
            revenue_last_year=revenue_last_year, net_profit=net_profit, existing_debt=existing_debt,
            credit_history_status=credit_history_status
        )
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        return new_company
    finally:
        db.close()

def get_company_by_id(company_id: int):
    db = SessionLocal()
    try:
        return db.query(companies).filter(companies.company_id == company_id).first()
    finally:
        db.close()

def get_companies_by_user(user_id: int):
    db = SessionLocal()
    try:
        return db.query(companies).join(
            user_companies, companies.company_id == user_companies.company_id
        ).filter(user_companies.user_id == user_id).all()
    finally:
        db.close()

def update_company(company_id: int, **kwargs):
    db = SessionLocal()
    try:
        company = db.query(companies).filter(companies.company_id == company_id).first()
        if company:
            for key, value in kwargs.items():
                setattr(company, key, value)
            db.commit()
            return company
        return None
    finally:
        db.close()

def delete_company(company_id: int):
    db = SessionLocal()
    try:
        company = db.query(companies).filter(companies.company_id == company_id).first()
        if company:
            db.delete(company)
            db.commit()
            return True
        return False
    finally:
        db.close()


# ==========================================
# 3. СВЯЗЬ ПОЛЬЗОВАТЕЛЕЙ И КОМПАНИЙ (USER_COMPANIES)
# ==========================================
def create_user_company(user_id: int, company_id: int):
    db = SessionLocal()
    try:
        new_link = user_companies(user_id=user_id, company_id=company_id)
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        return new_link
    finally:
        db.close()

def get_user_companies_by_user_id(user_id: int):
    db = SessionLocal()
    try:
        return db.query(user_companies).filter(user_companies.user_id == user_id).all()
    finally:
        db.close()

def get_user_companies_by_company_id(company_id: int):
    db = SessionLocal()
    try:
        return db.query(user_companies).filter(user_companies.company_id == company_id).all()
    finally:
        db.close()

def delete_user_company(link_id: int):
    db = SessionLocal()
    try:
        link = db.query(user_companies).filter(user_companies.id == link_id).first()
        if link:
            db.delete(link)
            db.commit()
            return True
        return False
    finally:
        db.close()


# ==========================================
# 4. ЗАЯВКИ (APPLICATIONS)
# ==========================================
def create_application(user_id: int, company_id: int, amount: float, term: int, purpose: str):
    db = SessionLocal()
    try:
        new_app = applications(
            user_id=user_id, company_id=company_id, requested_amount=amount,
            term_months=term, loan_purpose=purpose, status='created'
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return new_app
    finally:
        db.close()

def get_application_by_id(application_id: int):
    db = SessionLocal()
    try:
        return db.query(applications).filter(applications.application_id == application_id).first()
    finally:
        db.close()

def get_applications_by_user_id(user_id: int):
    db = SessionLocal()
    try:
        return db.query(applications).filter(applications.user_id == user_id).all()
    finally:
        db.close()

def get_applications_by_company_id(company_id: int):
    db = SessionLocal()
    try:
        return db.query(applications).filter(applications.company_id == company_id).all()
    finally:
        db.close()

def update_application(application_id: int, **kwargs):
    db = SessionLocal()
    try:
        app = db.query(applications).filter(applications.application_id == application_id).first()
        if app:
            for key, value in kwargs.items():
                setattr(app, key, value)
            db.commit()
            return app
        return None
    finally:
        db.close()

def delete_application(application_id: int):
    db = SessionLocal()
    try:
        app = db.query(applications).filter(applications.application_id == application_id).first()
        if app:
            db.delete(app)
            db.commit()
            return True
        return False
    finally:
        db.close()


# ==========================================
# 5. ОЦЕНКА РИСКА (RISK_ASSESMENTS)
# ==========================================
def create_risk_assessment(application_id: int, risk_class: str):
    db = SessionLocal()
    try:
        assessment = risk_assesments(application_id=application_id, risk_class=risk_class)
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment
    finally:
        db.close()

def get_risk_by_application(application_id: int):
    db = SessionLocal()
    try:
        return db.query(risk_assesments).filter(risk_assesments.application_id == application_id).first()
    finally:
        db.close()

def update_risk_assessment(risk_id: int, risk_class: str):
    db = SessionLocal()
    try:
        risk = db.query(risk_assesments).filter(risk_assesments.id == risk_id).first()
        if risk:
            risk.risk_class = risk_class
            db.commit()
            return risk
        return None
    finally:
        db.close()

def delete_risk_assessment(risk_id: int):
    db = SessionLocal()
    try:
        risk = db.query(risk_assesments).filter(risk_assesments.id == risk_id).first()
        if risk:
            db.delete(risk)
            db.commit()
            return True
        return False
    finally:
        db.close()


# ==========================================
# 6. ПРОДУКТЫ (PRODUCTS)
# ==========================================
def create_product(name: str, min_amount: float, max_amount: float, min_rate: float, max_rate: float, max_allowed_risk_levels: str):
    db = SessionLocal()
    try:
        new_product = products(
            name=name, min_amount=min_amount, max_amount=max_amount,
            min_rate=min_rate, max_rate=max_rate, max_allowed_risk_levels=max_allowed_risk_levels
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    finally:
        db.close()

def get_product_by_id(product_id: int):
    db = SessionLocal()
    try:
        return db.query(products).filter(products.product_id == product_id).first()
    finally:
        db.close()

def get_all_products():
    db = SessionLocal()
    try:
        return db.query(products).all()
    finally:
        db.close()

def update_product(product_id: int, **kwargs):
    db = SessionLocal()
    try:
        product = db.query(products).filter(products.product_id == product_id).first()
        if product:
            for key, value in kwargs.items():
                setattr(product, key, value)
            db.commit()
            return product
        return None
    finally:
        db.close()

def delete_product(product_id: int):
    db = SessionLocal()
    try:
        product = db.query(products).filter(products.product_id == product_id).first()
        if product:
            db.delete(product)
            db.commit()
            return True
        return False
    finally:
        db.close()


# ==========================================
# 7. ПРЕДЛОЖЕНИЯ (LOAN_OFFERS)
# ==========================================
def create_loan_offers(application_id: int, offers_list: list):
    db = SessionLocal()
    try:
        for offer in offers_list:
            new_offer = loan_offers(
                application_id=application_id, product_id=offer['product_id'],
                approved_amount=offer['approved_amount'], interest_rate=offer['interest_rate'],
                terms_months=offer['terms_months'], is_selected=False
            )
            db.add(new_offer)
        db.commit()
        return True
    finally:
        db.close()

def get_offer_by_id(offer_id: int):
    db = SessionLocal()
    try:
        return db.query(loan_offers).filter(loan_offers.id == offer_id).first()
    finally:
        db.close()

def get_offers_by_application(application_id: int):
    db = SessionLocal()
    try:
        return db.query(loan_offers).filter(loan_offers.application_id == application_id).all()
    finally:
        db.close()

def update_loan_offer(offer_id: int, **kwargs):
    db = SessionLocal()
    try:
        offer = db.query(loan_offers).filter(loan_offers.id == offer_id).first()
        if offer:
            for key, value in kwargs.items():
                setattr(offer, key, value)
            db.commit()
            return offer
        return None
    finally:
        db.close()

def delete_loan_offer(offer_id: int):
    db = SessionLocal()
    try:
        offer = db.query(loan_offers).filter(loan_offers.id == offer_id).first()
        if offer:
            db.delete(offer)
            db.commit()
            return True
        return False
    finally:
        db.close()

def select_offer(offer_id: int, application_id: int):
    db = SessionLocal()
    try:
        db.query(loan_offers).filter(loan_offers.application_id == application_id).update({"is_selected": False})
        offer = db.query(loan_offers).filter(loan_offers.id == offer_id).first()
        if offer:
            offer.is_selected = True
            db.commit()
            return offer
        return None
    finally:
        db.close()


# ==========================================
# 8. ВЫДАННЫЕ КРЕДИТЫ (LOANS)
# ==========================================
def create_loan(application_id: int, company_id: int, amount: float, rate: float, term: int, monthly_payment: float):
    db = SessionLocal()
    try:
        issue_date = datetime.now(timezone.utc)
        end_date = issue_date
        
        new_loan = loans(
            application_id=application_id, company_id=company_id, amount=amount,
            interest_rate=rate, term_months=term, issue_date=issue_date,
            end_date=end_date, monthly_payment=monthly_payment, status='active'
        )
        db.add(new_loan)
        
        company = db.query(companies).filter(companies.company_id == company_id).first()
        if company:
            company.existing_debt += amount
            
        db.commit()
        db.refresh(new_loan)
        return new_loan
    finally:
        db.close()

def get_loan_by_id(loan_id: int):
    db = SessionLocal()
    try:
        return db.query(loans).filter(loans.loan_id == loan_id).first()
    finally:
        db.close()

def get_loans_by_company_id(company_id: int):
    db = SessionLocal()
    try:
        return db.query(loans).filter(loans.company_id == company_id).all()
    finally:
        db.close()

def update_loan(loan_id: int, **kwargs):
    db = SessionLocal()
    try:
        loan = db.query(loans).filter(loans.loan_id == loan_id).first()
        if loan:
            for key, value in kwargs.items():
                setattr(loan, key, value)
            db.commit()
            return loan
        return None
    finally:
        db.close()

def delete_loan(loan_id: int):
    db = SessionLocal()
    try:
        loan = db.query(loans).filter(loans.loan_id == loan_id).first()
        if loan:
            db.delete(loan)
            db.commit()
            return True
        return False
    finally:
        db.close()
