from .database import SessionLocal, init_db
from .models import users, companies, products, user_companies, passport, loans
from datetime import datetime, timezone, timedelta
from decimal import Decimal

def seed_database():
    print("Инициализация базы данных...")
    init_db()
    
    db = SessionLocal()
    try:
        #Добавляем кредитные продукты
        product_list = [
            products(name="Оборотный кредит", min_amount=100000, max_amount=10000000, min_rate=15.0, max_rate=25.0, max_allowed_risk_levels="medium_risk"),
            products(name="Инвестиционный кредит", min_amount=1000000, max_amount=50000000, min_rate=12.0, max_rate=20.0, max_allowed_risk_levels="low_risk"),
            products(name="Экспресс-кредит", min_amount=50000, max_amount=3000000, min_rate=20.0, max_rate=30.0, max_allowed_risk_levels="high_risk"),
        ]
        db.add_all(product_list)
        db.commit()

        passport1 = passport(
            series="1234",
            number="567890",
            issued_by="ОВД Кировского района г. Москвы",
            issue_date=datetime(2015, 5, 20),
            code="770-001",
            registration_address="г. Москва, ул. Ленина, д. 5, кв. 10",
            birth_date=datetime(1990, 1, 15)
        )
        db.add(passport1)

# Создаем паспорт для Петра (user2)
        passport2 = passport(
            series="5678",
            number="123456",
            issued_by="УФМС России по г. Санкт-Петербургу",
            issue_date=datetime(2018, 8, 10),
            code="780-002",
            registration_address="г. Санкт-Петербург, Невский пр., д. 100",
            birth_date=datetime(1985, 12, 5)
        )
        db.add(passport2)

# Создаем паспорт для Сергея (user3)
        passport3 = passport(
            series="9012",
            number="345678",
            issued_by="ОВД Центрального района г. Екатеринбурга",
            issue_date=datetime(2012, 3, 12),
            code="660-003",
            registration_address="г. Екатеринбург, ул. Мира, д. 20",
            birth_date=datetime(1995, 7, 25)
        )
        db.add(passport3)
        db.commit()
        #Создаем пользователей и компании
        
        # --- Пользователь 1 (Хорошая компания, низкий риск) ---
        user1 = users(passport_id = passport1.id, email="client1@test.ru", phone="79990000001", hash_password="123", hash_salt="salt1", name="Иван", surname="Петров")
        db.add(user1)
        db.commit()
        
        comp1 = companies(
            name = "Vandex", entity_type="ООО", inn="1234567890", company_age=10,
            industry_okved="IT", revenue_last_year=15000000.0, 
            net_profit=3000000.0, existing_debt=0.0, 
            credit_history_status="positive"
        )
        db.add(comp1)
        db.commit()
        
        db.add(user_companies(user_id=user1.user_id, company_id=comp1.company_id))

        # --- Пользователь 2 (Средняя компания, средний риск) ---
        user2 = users(passport_id = passport2.id, email="client2@test.ru", phone="79990000002", hash_password="456", hash_salt="salt2", name="Петр", surname="Сидоров")
        db.add(user2)
        db.commit()
        
        comp2 = companies(
            name = "Marwa-Shawarma", entity_type="ИП", inn="123456789012", company_age=3,
            industry_okved="retail", revenue_last_year=5000000.0, 
            net_profit=500000.0, existing_debt=2000000.0, 
            credit_history_status="limited"
        )
        db.add(comp2)
        db.commit()
        
        db.add(user_companies(user_id=user2.user_id, company_id=comp2.company_id))

        # --- Пользователь 3 (Плохая компания, высокий риск) ---
        user3 = users(passport_id = passport3.id, email="client3@test.ru", phone="79990000003", hash_password="789", hash_salt="salt3", name="Сергей", surname="Иванов")
        db.add(user3)
        db.commit()
        
        comp3 = companies(
            name = "DyaDya Stroitel", entity_type="ООО", inn="9876543210", company_age=1,
            industry_okved="construction", revenue_last_year=1000000.0, 
            net_profit=-500000.0, existing_debt=8000000.0, 
            credit_history_status="negative"
        )
        db.add(comp3)
        db.commit()
        
        db.add(user_companies(user_id=user3.user_id, company_id=comp3.company_id))

        db.commit()
        
    finally:
        db.close()

def generate_historical_loans():
    print("Генерация исторических кредитов...")
    db = SessionLocal()
    try:
        def create_direct_loan(company_id, amount, rate, term):
            # 1. Создаем кредит напрямую (без заявки)
            issue_date = datetime.now(timezone.utc) - timedelta(days=90)
            end_date = issue_date + timedelta(days=term * 30)
            # Простая формула для платежа (аннуитет для хакатона не нужен)
            monthly_payment = (amount + (amount * (rate/100) * (term/12))) / term
        
            loan = loans(
                application_id=None, # <-- Вот тут пусто
                company_id=company_id,
                amount=amount, 
                interest_rate=rate, 
                term_months=term,
                issue_date=issue_date, 
                end_date=end_date,
                monthly_payment=monthly_payment, 
                status='active'
            )
            db.add(loan)
        
            # 2. Сразу увеличиваем долг компании
            comp = db.query(companies).filter(companies.company_id == company_id).first()
            if comp:
                comp.existing_debt += amount 
            db.commit()
            print(f"  -> Компании ID={company_id} добавлен кредит на сумму {amount}")

        # Иван (компания 1) — 2 кредита
        create_direct_loan(company_id=1, amount=Decimal("2000000.0"), rate=Decimal("15.0"), term=12)
        create_direct_loan(company_id=1, amount=Decimal("3000000.0"), rate=Decimal("18.5"), term=24)

        # Петр (компания 2) — 1 кредит
        create_direct_loan(company_id=2, amount=Decimal("1000000.0"), rate=Decimal("22.0"), term=6)

        # Сергей (компания 3) — без кредитов (пропускаем)

        print("Готово! Исторические кредиты добавлены.")
    finally:
        db.close()
