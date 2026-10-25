from database import SessionLocal
from models import applications, risk_assesments, loan_offers, loans, companies
from datetime import datetime, timezone, timedelta

def generate_historical_loans():
    print("Генерация исторических кредитов...")
    db = SessionLocal()
    try:
        # Вспомогательная функция (принимает готовые ID)
        def create_mock_loan(user_id, company_id, amount, rate, term):
            # Заявка
            app = applications(user_id=user_id, company_id=company_id, requested_amount=amount, term_months=term, loan_purpose="Пополнение оборотных средств", status="approved")
            db.add(app)
            db.commit()

            # Риск
            risk = risk_assesments(application_id=app.application_id, risk_class="low_risk")
            db.add(risk)
            
            # Предложение
            offer = loan_offers(application_id=app.application_id, product_id=1, approved_amount=amount, interest_rate=rate, terms_months=term, is_selected=True)
            db.add(offer)
            
            # Кредит
            issue_date = datetime.now(timezone.utc) - timedelta(days=90)
            end_date = issue_date + timedelta(days=term * 30)
            monthly_payment = (amount + (amount * (rate/100) * (term/12))) / term
            
            loan = loans(
                application_id=app.application_id, company_id=company_id,
                amount=amount, interest_rate=rate, term_months=term,
                issue_date=issue_date, end_date=end_date,
                monthly_payment=monthly_payment, status='active'
            )
            db.add(loan)
            
            # Обновляем долг компании
            comp = db.query(companies).filter(companies.company_id == company_id).first()
            if comp:
                comp.existing_debt += amount 
            db.commit()
            print(f"  -> Создан кредит для user_id={user_id} на сумму {amount}")

        # user1 (id=1) и его компания (id=1) — 2 кредита
        create_mock_loan(user_id=1, company_id=1, amount=2000000.0, rate=15.0, term=12)
        create_mock_loan(user_id=1, company_id=1, amount=3000000.0, rate=18.5, term=24)

        # user2 (id=2) и его компания (id=2) — 1 кредит
        create_mock_loan(user_id=2, company_id=2, amount=1000000.0, rate=22.0, term=6)

        # user3 (id=3) — без кредитов

        print("Готово! Исторические кредиты добавлены.")
    finally:
        db.close()

if __name__ == "__main__":
    generate_historical_loans()
