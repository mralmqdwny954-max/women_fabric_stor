from database import SessionLocal
from models import Admin
from passlib.context import CryptContext


# إعداد تشفير كلمة المرور
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# فتح قاعدة البيانات
db = SessionLocal()


# بيانات الأدمن
username = "admin"
password = "123456"


# إنشاء التشفير
hashed_password = pwd_context.hash(
    password.encode("utf-8")
)


# إنشاء حساب الأدمن
admin = Admin(
    username=username,
    password_hash=hashed_password
)


# حفظ الحساب
db.add(admin)
db.commit()


print("Admin created successfully")


# إغلاق الاتصال
db.close()