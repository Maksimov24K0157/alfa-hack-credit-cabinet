from database import SessionLocal, init_db
from models import users, companies, products, user_companies, passport, loans
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
            products(name="Кредит на развитие", min_amount=5000000, max_amount=100000000, min_rate=10.0, max_rate=18.0, max_allowed_risk_levels="low_risk"),
            products(name="Микрозайм для ИП", min_amount=50000, max_amount=1000000, min_rate=18.0, max_rate=28.0, max_allowed_risk_levels="medium_risk"),
            products(name="Тендерный кредит", min_amount=2000000, max_amount=30000000, min_rate=14.0, max_rate=22.0, max_allowed_risk_levels="low_risk"),
        ]
        db.add_all(product_list)
        db.commit()

        # --- ПАСПОРТА (9 штук) ---
        passport1 = passport(series="1234", number="567890", issued_by="ОВД Кировского района г. Москвы", issue_date=datetime(2015, 5, 20), code="770-001", registration_address="г. Москва, ул. Ленина, д. 5, кв. 10", birth_date=datetime(1990, 1, 15))
        db.add(passport1)
        passport2 = passport(series="5678", number="123456", issued_by="УФМС России по г. Санкт-Петербургу", issue_date=datetime(2018, 8, 10), code="780-002", registration_address="г. Санкт-Петербург, Невский пр., д. 100", birth_date=datetime(1985, 12, 5))
        db.add(passport2)
        passport3 = passport(series="9012", number="345678", issued_by="ОВД Центрального района г. Екатеринбурга", issue_date=datetime(2012, 3, 12), code="660-003", registration_address="г. Екатеринбург, ул. Мира, д. 20", birth_date=datetime(1995, 7, 25))
        db.add(passport3)
        passport4 = passport(series="1111", number="222222", issued_by="ОВД г. Казани", issue_date=datetime(2016, 1, 15), code="160-001", registration_address="г. Казань, ул. Баумана, д. 1", birth_date=datetime(1992, 3, 10))
        db.add(passport4)
        passport5 = passport(series="3333", number="444444", issued_by="ОВД г. Новосибирска", issue_date=datetime(2014, 6, 20), code="540-001", registration_address="г. Новосибирск, ул. Ленина, д. 10", birth_date=datetime(1988, 8, 20))
        db.add(passport5)
        passport6 = passport(series="5555", number="666666", issued_by="ОВД г. Нижнего Новгорода", issue_date=datetime(2017, 11, 5), code="520-001", registration_address="г. Н. Новгород, ул. Горького, д. 15", birth_date=datetime(1991, 5, 5))
        db.add(passport6)
        passport7 = passport(series="7777", number="888888", issued_by="ОВД г. Самары", issue_date=datetime(2013, 2, 25), code="630-001", registration_address="г. Самара, ул. Мира, д. 8", birth_date=datetime(1987, 11, 11))
        db.add(passport7)
        passport8 = passport(series="9999", number="000000", issued_by="ОВД г. Омска", issue_date=datetime(2019, 9, 9), code="550-001", registration_address="г. Омск, ул. Ленина, д. 3", birth_date=datetime(1993, 4, 4))
        db.add(passport8)
        passport9 = passport(series="1212", number="343434", issued_by="ОВД г. Ростова-на-Дону", issue_date=datetime(2011, 7, 7), code="610-001", registration_address="г. Ростов-на-Дону, ул. Садовая, д. 20", birth_date=datetime(1989, 9, 9))
        db.add(passport9)
        db.commit()

        # --- ПОЛЬЗОВАТЕЛИ И КОМПАНИИ ---
        
        # --- Пользователь 1 (2 компании) ---
        user1 = users(passport_id = passport1.id, email="client1@test.ru", phone="79990000001", hash_password="123", hash_salt="salt1", name="Иван", surname="Петров")
        db.add(user1)
        db.commit()
        comp1 = companies(name = "Vandex", entity_type="ООО", inn="1234567890", company_age=10, industry_okved="IT", revenue_last_year=15000000.0, net_profit=3000000.0, existing_debt=0.0, credit_history_status="positive")
        db.add(comp1)
        db.commit()
        db.add(user_companies(user_id=user1.user_id, company_id=comp1.company_id))
        
        comp2 = companies(name = "TechnoSoft", entity_type="ООО", inn="1111111111", company_age=5, industry_okved="IT", revenue_last_year=20000000.0, net_profit=5000000.0, existing_debt=1000000.0, credit_history_status="positive")
        db.add(comp2)
        db.commit()
        db.add(user_companies(user_id=user1.user_id, company_id=comp2.company_id))

        # --- Пользователь 2 (2 компании) ---
        user2 = users(passport_id = passport2.id, email="client2@test.ru", phone="79990000002", hash_password="456", hash_salt="salt2", name="Петр", surname="Сидоров")
        db.add(user2)
        db.commit()
        comp3 = companies(name = "Marwa-Shawarma", entity_type="ИП", inn="123456789012", company_age=3, industry_okved="retail", revenue_last_year=5000000.0, net_profit=500000.0, existing_debt=2000000.0, credit_history_status="limited")
        db.add(comp3)
        db.commit()
        db.add(user_companies(user_id=user2.user_id, company_id=comp3.company_id))
        
        comp4 = companies(name = "CoffeeTochka", entity_type="ИП", inn="222222222222", company_age=2, industry_okved="retail", revenue_last_year=3000000.0, net_profit=300000.0, existing_debt=500000.0, credit_history_status="limited")
        db.add(comp4)
        db.commit()
        db.add(user_companies(user_id=user2.user_id, company_id=comp4.company_id))

        # --- Пользователь 3 (2 компании) ---
        user3 = users(passport_id = passport3.id, email="client3@test.ru", phone="79990000003", hash_password="789", hash_salt="salt3", name="Сергей", surname="Иванов")
        db.add(user3)
        db.commit()
        comp5 = companies(name = "DyaDya Stroitel", entity_type="ООО", inn="9876543210", company_age=1, industry_okved="construction", revenue_last_year=1000000.0, net_profit=-500000.0, existing_debt=8000000.0, credit_history_status="negative")
        db.add(comp5)
        db.commit()
        db.add(user_companies(user_id=user3.user_id, company_id=comp5.company_id))
        
        comp6 = companies(name = "StroyMaster", entity_type="ООО", inn="3333333333", company_age=8, industry_okved="construction", revenue_last_year=30000000.0, net_profit=6000000.0, existing_debt=5000000.0, credit_history_status="positive")
        db.add(comp6)
        db.commit()
        db.add(user_companies(user_id=user3.user_id, company_id=comp6.company_id))

        # --- Пользователь 4 (1 компания) ---
        user4 = users(passport_id = passport4.id, email="client4@test.ru", phone="79990000004", hash_password="hash4", hash_salt="salt4", name="Алексей", surname="Смирнов")
        db.add(user4)
        db.commit()
        comp7 = companies(name = "AutoParts", entity_type="ООО", inn="4444444444", company_age=4, industry_okved="retail", revenue_last_year=12000000.0, net_profit=1000000.0, existing_debt=3000000.0, credit_history_status="limited")
        db.add(comp7)
        db.commit()
        db.add(user_companies(user_id=user4.user_id, company_id=comp7.company_id))

        # --- Пользователь 5 (1 компания) ---
        user5 = users(passport_id = passport5.id, email="client5@test.ru", phone="79990000005", hash_password="hash5", hash_salt="salt5", name="Дмитрий", surname="Кузнецов")
        db.add(user5)
        db.commit()
        comp8 = companies(name = "MedCenter", entity_type="ООО", inn="5555555555", company_age=7, industry_okved="services", revenue_last_year=25000000.0, net_profit=7000000.0, existing_debt=0.0, credit_history_status="positive")
        db.add(comp8)
        db.commit()
        db.add(user_companies(user_id=user5.user_id, company_id=comp8.company_id))

        # --- Пользователь 6 (1 компания) ---
        user6 = users(passport_id = passport6.id, email="client6@test.ru", phone="79990000006", hash_password="hash6", hash_salt="salt6", name="Андрей", surname="Попов")
        db.add(user6)
        db.commit()
        comp9 = companies(name = "LogisticPro", entity_type="ООО", inn="6666666666", company_age=6, industry_okved="transport", revenue_last_year=18000000.0, net_profit=2000000.0, existing_debt=4000000.0, credit_history_status="positive")
        db.add(comp9)
        db.commit()
        db.add(user_companies(user_id=user6.user_id, company_id=comp9.company_id))

        # --- Пользователь 7 (1 компания) ---
        user7 = users(passport_id = passport7.id, email="client7@test.ru", phone="79990000007", hash_password="hash7", hash_salt="salt7", name="Михаил", surname="Васильев")
        db.add(user7)
        db.commit()
        comp10 = companies(name = "EcoFood", entity_type="ИП", inn="777777777777", company_age=1, industry_okved="retail", revenue_last_year=1500000.0, net_profit=-100000.0, existing_debt=200000.0, credit_history_status="negative")
        db.add(comp10)
        db.commit()
        db.add(user_companies(user_id=user7.user_id, company_id=comp10.company_id))

        # --- Пользователь 8 (1 компания) ---
        user8 = users(passport_id = passport8.id, email="client8@test.ru", phone="79990000008", hash_password="hash8", hash_salt="salt8", name="Николай", surname="Соколов")
        db.add(user8)
        db.commit()
        comp11 = companies(name = "SmartHome", entity_type="ООО", inn="8888888888", company_age=3, industry_okved="IT", revenue_last_year=8000000.0, net_profit=1500000.0, existing_debt=1000000.0, credit_history_status="positive")
        db.add(comp11)
        db.commit()
        db.add(user_companies(user_id=user8.user_id, company_id=comp11.company_id))

        # --- Пользователь 9 (1 компания) ---
        user9 = users(passport_id = passport9.id, email="client9@test.ru", phone="79990000009", hash_password="hash9", hash_salt="salt9", name="Владимир", surname="Михайлов")
        db.add(user9)
        db.commit()
        comp12 = companies(name = "GreenBuild", entity_type="ООО", inn="9999999999", company_age=12, industry_okved="construction", revenue_last_year=45000000.0, net_profit=8000000.0, existing_debt=15000000.0, credit_history_status="limited")
        db.add(comp12)
        db.commit()
        db.add(user_companies(user_id=user9.user_id, company_id=comp12.company_id))

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
            # Простая формула для платежа
            monthly_payment = (amount + (amount * (rate/100) * (Decimal(term)/12))) / Decimal(term)
        
            loan = loans(
                application_id=None,
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

        # Иван (компания 1 и 2) — 2 кредита
        create_direct_loan(company_id=1, amount=Decimal("2000000.0"), rate=Decimal("15.0"), term=12)
        create_direct_loan(company_id=2, amount=Decimal("3000000.0"), rate=Decimal("18.5"), term=24)

        # Петр (компания 3 и 4) — 1 кредит
        create_direct_loan(company_id=3, amount=Decimal("1000000.0"), rate=Decimal("22.0"), term=6)

        # Сергей (компания 5 и 6) — 1 кредит
        create_direct_loan(company_id=5, amount=Decimal("500000.0"), rate=Decimal("25.0"), term=12)

        # Остальные (юзеры 4-9) — без кредитов

        print("Готово! Исторические кредиты добавлены.")
    finally:
        db.close()
