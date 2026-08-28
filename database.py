from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# رابط قاعدة البيانات PostgreSQL
DATABASE_URL = "postgresql://postgres:qwezxcasd@localhost:5432/women_fabric_store"


# إنشاء محرك الاتصال بقاعدة البيانات
engine = create_engine(
    DATABASE_URL
)


# إنشاء جلسة للتعامل مع قاعدة البيانات
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# الأساس الذي سنبني عليه الجداول لاحقًا
Base = declarative_base()


# دالة فتح الاتصال بقاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)        