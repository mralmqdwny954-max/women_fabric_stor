# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from routers.admin import router as admin_router
# from routers.customer import router as customer_router
# from routers.cart import router as cart_router

# # إنشاء تطبيق FastAPI
# from fastapi import FastAPI
# from starlette.middleware.sessions import SessionMiddleware
# # استيراد قاعدة البيانات
# from database import engine, create_tables
# # استيراد الموديلات
# from models import Product

# from routers.categories import router as categories_router
# from routers.products import router as products_router
# from routers.product_colors import router as product_colors_router
# from routers.banners import router as banners_router
# from routers.orders import router as orders_router
# from routers.order_items import router as order_items_router

# # إنشاء التطبيق
# app = FastAPI(
#     title="Women Fabric Store API",
#     debug=True
# )

# # ربط ملفات التصميم
# app.mount(
#     "/static",
#     StaticFiles(directory="static"),
#     name="static"
# )


# # ربط مجلد الصور المرفوعة
# app.mount(
#     "/uploads",
#     StaticFiles(directory="uploads"),
#     name="uploads"
# )

# app.add_middleware(
#     SessionMiddleware,
#     secret_key="women_fabric_secret_key"
# )


# # إعداد صفحات HTML
# templates = Jinja2Templates(
#     directory="templates"
# )

# app.include_router(categories_router)
# app.include_router(products_router)
# app.include_router(product_colors_router)
# app.include_router(banners_router)
# app.include_router(orders_router)
# app.include_router(order_items_router)
# app.include_router(admin_router)
# app.include_router(customer_router)
# app.include_router(cart_router)
# # إنشاء جداول قاعدة البيانات
# create_tables()


# # اختبار الاتصال بقاعدة البيانات
# try:
#     connection = engine.connect()
#     print("Database connection successful")
#     connection.close()

# except Exception as error:
#     print("Database connection failed:")
#     print(error)

# # الصفحة الرئيسية للتأكد أن التطبيق يعمل

# @app.get("/")
# def home():
#     return {
#         "message": "Women Fabric Store API is working"
#     }



# #127.0.0.1:8000/admin/    http://127.0.0.1:8000/

# #uvicorn main:app --reload


import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse


# قاعدة البيانات
from database import engine, create_tables, SessionLocal

# الموديلات
from models import Product, Admin

# Routers
from routers.admin import router as admin_router
from routers.customer import router as customer_router
from routers.cart import router as cart_router
from routers.categories import router as categories_router
from routers.products import router as products_router
from routers.product_colors import router as product_colors_router
from routers.banners import router as banners_router
from routers.orders import router as orders_router
from routers.order_items import router as order_items_router


# إنشاء التطبيق
app = FastAPI(
    title="Women Fabric Store API",
    debug=True
)

# عرض صور Cloudinary مع الحفاظ على طريقة عرض الصور الحالية في HTML
@app.get("/media/{folder}/{filename}")
def cloudinary_image(folder: str, filename: str):

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")

    image_url = (
        f"https://res.cloudinary.com/{cloud_name}"
        f"/image/upload/women_fabric_store/{folder}/{filename}"
    )

    return RedirectResponse(
        url=image_url,
        status_code=307
    )
# ربط ملفات التصميم
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ربط مجلد الصور المرفوعة
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)


# الجلسات
app.add_middleware(
    SessionMiddleware,
    secret_key="women_fabric_secret_key"
)


# إعداد صفحات HTML
templates = Jinja2Templates(
    directory="templates"
)


# ربط الـ Routers
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(product_colors_router)
app.include_router(banners_router)
app.include_router(orders_router)
app.include_router(order_items_router)
app.include_router(admin_router)
app.include_router(customer_router)
app.include_router(cart_router)


# إنشاء جداول قاعدة البيانات
create_tables()


# إنشاء أو تحديث حساب الأدمن في Render
def create_default_admin():

    db = SessionLocal()

    try:
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")

        # التأكد من وجود المتغيرات في Render
        if not username or not password:
            print("ADMIN_USERNAME or ADMIN_PASSWORD not found")
            return

        # تشفير كلمة المرور
        pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )

        # نبحث عن أول حساب أدمن موجود
        existing_admin = db.query(Admin).first()

        # إذا الحساب موجود، نحدث بياناته
        if existing_admin:
            existing_admin.username = username
            existing_admin.password_hash = pwd_context.hash(password)

            db.commit()

            print("Admin updated successfully")
            return

        # إذا لا يوجد أي أدمن، ننشئ حساب جديد
        new_admin = Admin(
            username=username,
            password_hash=pwd_context.hash(password)
        )

        db.add(new_admin)
        db.commit()

        print("Admin created successfully")

    except Exception as error:
        db.rollback()
        print("Error creating/updating admin:")
        print(error)

    finally:
        db.close()



# تشغيل إنشاء الأدمن
create_default_admin()


# اختبار الاتصال بقاعدة البيانات
try:
    connection = engine.connect()

    print("Database connection successful")

    connection.close()

except Exception as error:

    print("Database connection failed:")
    print(error)


# الصفحة الرئيسية للتأكد أن التطبيق يعمل
@app.get("/")
def home():
    return {
        "message": "Women Fabric Store API is working"
    }


# تشغيل محلي:
# uvicorn main:app --reload
#
# لوحة الأدمن محليًا:
# http://127.0.0.1:8000/admin/
#
# لوحة الأدمن على Render:
# https://women-fabric-stor.onrender.com/admin/login