from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers.admin import router as admin_router
from routers.customer import router as customer_router
from routers.cart import router as cart_router

# إنشاء تطبيق FastAPI
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
# استيراد قاعدة البيانات
from database import engine, create_tables
# استيراد الموديلات
from models import Product

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

app.add_middleware(
    SessionMiddleware,
    secret_key="women_fabric_secret_key"
)


# إعداد صفحات HTML
templates = Jinja2Templates(
    directory="templates"
)

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



#127.0.0.1:8000/admin/    http://127.0.0.1:8000/

#uvicorn main:app --reload