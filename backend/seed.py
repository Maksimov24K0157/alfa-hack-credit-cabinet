from database import SessionLocal, init_db, reset_db
from models import users, companies, products, user_companies, passport, loans
from datetime import datetime, timezone, timedelta
from decimal import Decimal

def seed_database():
    print("Сброс и инициализация базы данных...")
    reset_db() # Если функции нет, удали эту строку и удали test.db вручную
    init_db()
    
    db = SessionLocal()
    try:
        # 1. ДОБАВЛЯЕМ КРЕДИТНЫЕ ПРОДУКТЫ (6 штук)
        print("Добавляем продукты...")
        product_list = [
            products(name="Оборотный кредит", min_amount=100000, max_amount=10000000, min_rate=Decimal("15.0"), max_rate=Decimal("25.0"), max_allowed_risk_levels="medium_risk"),
            products(name="Инвестиционный кредит", min_amount=1000000, max_amount=50000000, min_rate=Decimal("12.0"), max_rate=Decimal("20.0"), max_allowed_risk_levels="low_risk"),
            products(name="Экспресс-кредит", min_amount=50000, max_amount=3000000, min_rate=Decimal("20.0"), max_rate=Decimal("30.0"), max_allowed_risk_levels="high_risk"),
            products(name="Кредит на развитие", min_amount=5000000, max_amount=100000000, min_rate=Decimal("10.0"), max_rate=Decimal("18.0"), max_allowed_risk_levels="low_risk"),
            products(name="Микрозайм для ИП", min_amount=50000, max_amount=1000000, min_rate=Decimal("18.0"), max_rate=Decimal("28.0"), max_allowed_risk_levels="medium_risk"),
            products(name="Тендерный кредит", min_amount=2000000, max_amount=30000000, min_rate=Decimal("14.0"), max_rate=Decimal("22.0"), max_allowed_risk_levels="low_risk"),
        ]
        db.add_all(product_list)
        db.commit()

        # 2. СОЗДАЕМ ПОЛЬЗОВАТЕЛЕЙ, ПАСПОРТА И КОМПАНИИ (9 юзеров, 12 компаний)
        print("Создаем пользователей и компании...")
        
        # Справочники для генерации
        names = [("Иван", "Петров"), ("Петр", "Сидоров"), ("Сергей", "Иванов"), 
                 ("Алексей", "Смирнов"), ("Дмитрий", "Кузнецов"), ("Андрей", "Попов"),
                 ("Михаил", "Васильев"), ("Николай", "Соколов"), ("Владимир", "Михайлов")]
        
        companies_data = [
            ("Vandex", "ООО", "1234567890", 10, "IT", 15000000, 3000000, 0, "positive"),
            ("Marwa-Shawarma", "ИП", "123456789012", 3, "retail", 5000000, 500000, 2000000, "limited"),
            ("DyaDya Stroitel", "ООО", "9876543210", 1, "construction", 1000000, -500000, 8000000, "negative"),
            ("TechnoSoft", "ООО", "1111111111", 5, "IT", 20000000, 5000000, 1000000, "positive"),
            ("CoffeeTochka", "ИП", "222222222222", 2, "retail", 3000000, 300000, 500000, "limited"),
            ("StroyMaster", "ООО", "3333333333", 8, "construction", 30000000, 6000000, 5000000, "positive"),
            ("AutoParts", "ООО", "4444444444", 4, "retail", 12000000, 1000000, 3000000, "limited"),
            ("MedCenter", "ООО", "5555555555", 7, "services", 25000000, 7000000, 0, "positive"),
            ("LogisticPro", "ООО", "6666666666", 6, "transport", 18000000, 2000000, 4000000, "positive"),
            ("EcoFood", "ИП", "777777777777", 1, "retail", 1500000, -100000, 200000, "negative"),
            ("SmartHome", "ООО", "8888888888", 3, "IT", 8000000, 1500000, 1000000, "positive"),
            ("GreenBuild", "ООО", "9999999999", 12, "construction", 45000000, 8000000, 15000000, "limited"),
        ]

        users_created = []
        companies_created = []

        for i in range(9):
            # Создаем паспорт
            p = passport(
                series=f"12{i:02d}", number=f"5678{i:02d}", 
                issued_by="ОВД г. Москвы", 
                issue_date=datetime(2015, 5, 20), 
                code="770-001", 
                registration_address="г. Москва, ул. Ленина, д. 5", 
                birth_date=datetime(1990, 1, 15)
            )
            db.add(p)
            db.commit()

            # Создаем юзера
            u = users(
                passport_id=p.id, 
                email=f"client{i+1}@test.ru", 
                phone=f"799900000{i:02d}", 
                hash_password=f"hash{i+1}", 
                hash_salt=f"salt{i+1}", 
                name=names[i][0], 
                surname=names[i][1]
            )
            db.add(u)
            db.commit()
            users_created.append(u)

        # Распределяем 12 компаний по 9 юзерам (первые 3 юзера получат по 2 компании, остальные по 1)
        comp_idx = 0
        for u_idx, user in enumerate(users_created):
            # Сколько компаний дать этому юзеру
            comps_for_user = 2 if u_idx < 3 else 1
            
            for _ in range(comps_for_user):
                if comp_idx >= len(companies_data):
                    break
                
                c_data = companies_data[comp_idx]
                c = companies(
                    name=c_data[0], entity_type=c_data[1], inn=c_data[2], company_age=c_data[3],
                    industry_okved=c_data[4], revenue_last_year=Decimal(str(c_data[5])), 
                    net_profit=Decimal(str(c_data[6])), existing_debt=Decimal(str(c_data[7])), 
                    credit_history_status=c_data[8]
                )
                db.add(c)
                db.commit()
                
                # Связываем юзера и компанию
                db.add(user_companies(user_id=user.user_id, company_id=c.company_id))
                companies_created.append(c)
                comp_idx += 1

        db.commit()
        print(f"Создано {len(users_created)} пользователей и {len(companies_created)} компаний.")

        # 3. ГЕНЕРАЦИЯ ИСТОРИЧЕСКИХ КРЕДИТОВ (для 3 из 9 юзеров = треть)
        print("Генерация кредитов для трети пользователей...")
        
        def create_direct_loan(company_id, amount, rate, term):
            amount = Decimal(str(amount))
            rate = Decimal(str(rate))
            term_dec = Decimal(str(term))
            
            issue_date = datetime.now(timezone.utc) - timedelta(days=90)
            end_date = issue_date + timedelta(days=term * 30)
            monthly_payment = (amount + (amount * (rate / Decimal("100")) * (term_dec / Decimal("12")))) / term_dec
            
            loan = loans(
                application_id=None, company_id=company_id, amount=amount, 
                interest_rate=rate, term_months=term, issue_date=issue_date, 
                end_date=end_date, monthly_payment=monthly_payment, status='active'
            )
            db.add(loan)
            
            comp = db.query(companies).filter(companies.company_id == company_id).first()
            if comp:
                comp.existing_debt += amount 
            db.commit()

        # Берем первых трех юзеров (client1, client2, client3) и выдаем им кредиты
        # client1 владеет компанией 1 (и 2)
        create_direct_loan(company_id=1, amount=2000000.0, rate=15.0, term=12)
        create_direct_loan(company_id=1, amount=3000000.0, rate=18.5, term=24)
        
        # client2 владеет компанией 3 (и 4)
        create_direct_loan(company_id=3, amount=1000000.0, rate=22.0, term=6)
        
        # client3 владеет компанией 5 (и 6)
        create_direct_loan(company_id=5, amount=500000.0, rate=25.0, term=12)

        print("Готово! База полностью создана и заполнена.")
            
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
