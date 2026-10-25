from sqlalchemy.orm import Session
from database import SessionLocal
from models import users, companies, user_companies, applications, risk_assesments, products, loan_offers, loans
from datetime import datetime, timezone

# ==========================================
# 1. ПОЛЬЗОВАТЕЛИ И КОМПАНИИ
# ==========================================

def get_user_by_email(email: str):
    """Найти пользователя по email (для логина)."""
    db = SessionLocal()
    try:
        return db.query(users).filter(users.email == email).first()
    finally:
        db.close()

def get_companies_by_user(user_id: int):
    """Получить список компаний, которыми владеет пользователь."""
    db = SessionLocal()
    try:
        # Делаем JOIN таблицы компаний и таблицы связей
        return db.query(companies).join(
            user_companies, companies.company_id == user_companies.company_id
        ).filter(user_companies.user_id == user_id).all()
    finally:
        db.close()

def get_company_by_id(company_id: int):
    """Получить данные одной компании."""
    db = SessionLocal()
    try:
        return db.query(companies).filter(companies.company_id == company_id).first()
    finally:
        db.close()


# ==========================================
# 2. ЗАЯВКИ (APPLICATIONS)
# ==========================================

def create_application(user_id: int, company_id: int, amount: float, term: int, purpose: str):
    """Создать новую заявку на кредит."""
    db = SessionLocal()
    try:
        new_app = applications(
            user_id=user_id,
            company_id=company_id,
            requested_amount=amount,
            term_months=term,
            loan_purpose=purpose,
            status='created'
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app) # Обновляем, чтобы получить ID из базы
        return new_app
    finally:
        db.close()

def get_application_by_id(application_id: int):
    """Получить заявку по ID."""
    db = SessionLocal()
    try:
        return db.query(applications).filter(applications.application_id == application_id).first()
    finally:
        db.close()

def update_application_status(application_id: int, new_status: str):
    """Сменить статус заявки (например, на 'scored' или 'offered')."""
    db = SessionLocal()
    try:
        app = db.query(applications).filter(applications.application_id == application_id).first()
        if app:
            app.status = new_status
            db.commit()
            return app
        return None
    finally:
        db.close()


# ==========================================
# 3. ОЦЕНКА РИСКА (ML)
# ==========================================

def save_risk_assessment(application_id: int, risk_class: str):
    """Сохранить результат ML-модели."""
    db = SessionLocal()
    try:
        assessment = risk_assesments(
            application_id=application_id,
            risk_class=risk_class
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment
    finally:
        db.close()

def get_risk_by_application(application_id: int):
    """Получить оценку риска по заявке."""
    db = SessionLocal()
    try:
        return db.query(risk_assesments).filter(risk_assesments.application_id == application_id).first()
    finally:
        db.close()


# ==========================================
# 4. ПРЕДЛОЖЕНИЯ (LOAN OFFERS)
# ==========================================

def create_loan_offers(application_id: int, offers_list: list):
    """
    Создать несколько предложений сразу.
    offers_list — это список словарей: [{'product_id': 1, 'approved_amount': 500000, 'interest_rate': 15, 'terms_months': 12}, ...]
    """
    db = SessionLocal()
    try:
        for offer in offers_list:
            new_offer = loan_offers(
                application_id=application_id,
                product_id=offer['product_id'],
                approved_amount=offer['approved_amount'],
                interest_rate=offer['interest_rate'],
                terms_months=offer['terms_months'],
                is_selected=False
            )
            db.add(new_offer)
        db.commit()
        return True
    finally:
        db.close()

def get_offers_by_application(application_id: int):
    """Получить все предложения по заявке."""
    db = SessionLocal()
    try:
        return db.query(loan_offers).filter(loan_offers.application_id == application_id).all()
    finally:
        db.close()

def select_offer(offer_id: int, application_id: int):
    """Выбрать одно предложение (и сбросить остальные для этой заявки)."""
    db = SessionLocal()
    try:
        # Сначала сбрасываем все предложения для этой заявки
        db.query(loan_offers).filter(loan_offers.application_id == application_id).update({"is_selected": False})
        
        # Потом выбираем нужное
        offer = db.query(loan_offers).filter(loan_offers.id == offer_id).first()
        if offer:
            offer.is_selected = True
            db.commit()
            return offer
        return None
    finally:
        db.close()


# ==========================================
# 5. ВЫДАЧА КРЕДИТА (LOANS)
# ==========================================

def create_loan(application_id: int, company_id: int, amount: float, rate: float, term: int, monthly_payment: float):
    """Создать факт выдачи кредита и обновить долг компании."""
    db = SessionLocal()
    try:
        # 1. Создаем кредит
        issue_date = datetime.now(timezone.utc)
        # Простой расчет даты окончания (прибавляем месяцы)
        # В реальности нужно использовать dateutil.relativedelta, но для MVP сойдет
        end_date = issue_date # Заглушка, лучше рассчитать нормально
        
        new_loan = loans(
            application_id=application_id,
            company_id=company_id,
            amount=amount,
            interest_rate=rate,
            term_months=term,
            issue_date=issue_date,
            end_date=end_date,
            monthly_payment=monthly_payment,
            status='active'
        )
        db.add(new_loan)

        # 2. Обновляем долг компании
        company = db.query(companies).filter(companies.company_id == company_id).first()
        if company:
            company.existing_debt += amount

        db.commit()
        db.refresh(new_loan)
        return new_loan
    finally:
        db.close()
