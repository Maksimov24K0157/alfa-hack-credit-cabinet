from database import SessionLocal, init_db
from models import users, companies, products, user_companies

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

        #Создаем пользователей и компании
        
        # --- Пользователь 1 (Хорошая компания, низкий риск) ---
        user1 = users(email="client1@test.ru", phone="79990000001", hash_password="123", hash_salt="salt1", name="Иван", surname="Петров")
        db.add(user1)
        db.commit()
        
        comp1 = companies(
            entity_type="ООО", inn="1234567890", company_age=10,
            industry_okved="IT", revenue_last_year=15000000.0, 
            net_profit=3000000.0, existing_debt=0.0, 
            credit_history_status="positive"
        )
        db.add(comp1)
        db.commit()
        
        db.add(user_companies(user_id=user1.user_id, company_id=comp1.company_id))

        # --- Пользователь 2 (Средняя компания, средний риск) ---
        user2 = users(email="client2@test.ru", phone="79990000002", hash_password="456", hash_salt="salt2", name="Петр", surname="Сидоров")
        db.add(user2)
        db.commit()
        
        comp2 = companies(
            entity_type="ИП", inn="123456789012", company_age=3,
            industry_okved="retail", revenue_last_year=5000000.0, 
            net_profit=500000.0, existing_debt=2000000.0, 
            credit_history_status="limited"
        )
        db.add(comp2)
        db.commit()
        
        db.add(user_companies(user_id=user2.user_id, company_id=comp2.company_id))

        # --- Пользователь 3 (Плохая компания, высокий риск) ---
        user3 = users(email="client3@test.ru", phone="79990000003", hash_password="789", hash_salt="salt3", name="Сергей", surname="Иванов")
        db.add(user3)
        db.commit()
        
        comp3 = companies(
            entity_type="ООО", inn="9876543210", company_age=1,
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

if __name__ == "__main__":
    seed_database()
