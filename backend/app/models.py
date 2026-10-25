import sqlalchemy
from datetime import datetime, timezone
from sqlalchemy import text, Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key = True, autoincrement = True)
    email = Column(String(255), nullable = False, unique = True)
    phone = Column(String(12), nullable = False)
    hash_password = Column(String(100), nullable = False, unique = True)
    hash_salt = Column(String(64), nullable = False, unique = True)
    name = Column(String(100), nullable = False)
    surname = Column(String(100), nullable = False)
    patronymic = Column(String(100), default = None)

class user_companies(Base):
    __tablename__ = 'user_companies'
    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete = "CASCADE"), nullable = False)
    company_id = Column(Integer, ForeignKey("companies.company_id", ondelete = "CASCADE"), nullable = False)

    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', name='unique_user_company'),
    )
class companies(Base):
    __tablename__ = 'companies'
    company_id = Column(Integer, primary_key = True, autoincrement = True)
    entity_type = Column(String(11), nullable = False) #строго OOO, ИП, Самозанятый
    inn = Column(String(12), nullable = False, unique = True)
    company_age = Column(Integer, nullable = False,)
    industry_okved = Column(String(100), nullable = False)
    revenue_last_year = Column(Numeric(precision=14, scale=2), nullable = False)
    net_profit = Column(Numeric(precision=14, scale=2), nullable = False)
    existing_debt = Column(Numeric(precision=14, scale=2), nullable = False)
    credit_history_status = Column(String(20), nullable = False)
    __table_args__ = (
        CheckConstraint("entity_type in ('ООО', 'ИП', 'Самозанятый')", name='check_entity_type'),
        CheckConstraint("(entity_type = 'ООО' AND length(inn) = 10) OR "
                       "(entity_type IN ('ИП', 'Самозанятый') AND length(inn) = 12)", 
                       name='check_inn_length_by_type'),
        CheckConstraint("company_age >= 0", name='check_company_age'),
        CheckConstraint("revenue_last_year >= 0", name='check_revenue_last_year'),
        CheckConstraint("existing_debt >= 0", name='check_existing_debt'),
        CheckConstraint("credit_history_status in ('positive', 'negative', 'limited')", name='check_credit_history_status'),
        CheckConstraint("industry_okved in ('IT', 'manufacturing', 'construction', 'retail', 'wholsale', 'transport', 'agriculture', 'consulting')", name='check_industry_okved'),
    )

class applications(Base):
    __tablename__ = 'applications'

    application_id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete = "CASCADE"), nullable = False)
    company_id = Column(Integer, ForeignKey("companies.company_id", ondelete = "CASCADE"), nullable = False)
    requested_amount = Column(Numeric(precision=14, scale=2), nullable = False)
    term_months = Column(Integer, nullable = False)
    loan_purpose = Column(String, nullable = False)
    status = Column(String(30), nullable = False)
    created_at = Column(DateTime(timezone = True), nullable = False, default = lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("requested_amount > 0", name='check_requested_amount'), #возможно имеет смысл ввести минимальную ссумму кредитования
        CheckConstraint("term_months >= 0", name='check_term_months'),
        CheckConstraint("status in ('created', 'scored', 'offered', 'approved', 'closed by user', 'denied')", name='check_status'),
        CheckConstraint("loan_purpose in ('working_capital', 'equipment', 'business_expansion', 'refinancing')", name='check_loan_purpose'),
    )

class risk_assesments(Base):
    __tablename__ = 'risk_assesments'

    id = Column(Integer, primary_key = True, autoincrement = True)
    application_id = Column(Integer, ForeignKey("applications.application_id", ondelete = "CASCADE"), nullable = False)
    risk_class = Column(String, nullable = False)

    __table_args__ = (
        CheckConstraint("risk_class in ('low_risk', 'medium_risk', 'high_risk', 'very_high_risk')", name = 'check_risk_class'),
    )

class products(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key = True, autoincrement = True)
    name  = Column(String, nullable = False)
    min_amount  = Column(Numeric(precision=14, scale=2), nullable = False)
    max_amount = Column(Numeric(precision=14, scale=2), nullable = False)
    min_rate = Column(Numeric(precision=14, scale=2), nullable = False)
    max_rate = Column(Numeric(precision=14, scale=2), nullable = False)
    max_allowed_risk_levels = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("min_amount >= 0", name='check_min_amount'),
        CheckConstraint("max_amount > 0 AND max_amount >= min_amount", name='check_max_amount'),
        CheckConstraint("min_rate > 0", name='check_min_rate'),
        CheckConstraint("max_rate > 0 AND max_rate >= min_rate", name='check_max_rate'),
        CheckConstraint("max_allowed_risk_levels in ('low_risk', 'medium_risk', 'high_risk', 'very_high_risk')", name='check_max_allowed_risk_levels'),
    )

class loan_offers(Base):
    __tablename__ = 'loan_offers'

    id = Column(Integer, primary_key = True, autoincrement = True)
    application_id = Column(Integer, ForeignKey("applications.application_id", ondelete = "CASCADE"), nullable = False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete = "CASCADE"), nullable = False)
    approved_amount = Column(Numeric(precision=14, scale=2), nullable = False)
    interest_rate = Column(Numeric(precision=14, scale=2), nullable = False)
    terms_months = Column(Integer, nullable = False)
    is_selected = Column(Boolean, nullable = False, default=False)

    __table_args__ = (
        CheckConstraint("approved_amount > 0", name='check_approved_amount'),
        CheckConstraint("interest_rate > 0", name='check_interest_rate'),
        CheckConstraint("terms_months > 0", name='check_terms_months'),
    )

class loans(Base):
    __tablename__ = 'loans'

    loan_id = Column(Integer, primary_key = True, autoincrement = True)
    application_id = Column(Integer, ForeignKey("applications.application_id", ondelete = "CASCADE"), nullable = False)
    company_id = Column(Integer, ForeignKey("companies.company_id", ondelete = "CASCADE"), nullable = False)
    amount = Column(Numeric(precision=14, scale=2), nullable = False)
    interest_rate = Column(Numeric(precision=14, scale=2), nullable = False)
    status = Column(String(20), nullable=False, default='active')
    term_months = Column(Integer, nullable = False)
    issue_date = Column(DateTime(timezone = True), nullable = False)
    end_date = Column(DateTime(timezone = True), nullable = False)
    monthly_payment = Column(Numeric(precision=14, scale=2), nullable = False)

    __table_args__ = (
        CheckConstraint("amount >= 0", name='check_amount'),
        CheckConstraint("interest_rate > 0", name='check_interest_rate'),
        CheckConstraint("status in ('active', 'closed')", name='check_status'),
        CheckConstraint("term_months >= 0", name='check_term_months'),
        CheckConstraint("monthly_payment > 0", name='check_monthly_payment'),
    )
