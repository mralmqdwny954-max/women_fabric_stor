from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import SessionLocal
from models import Category, Product, Order, Banner, ProductColor, Admin
from sqlalchemy.orm import joinedload
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from utils.upload import save_image, delete_image

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

templates = Jinja2Templates(
    directory="templates"
)

# التحقق من تسجيل دخول الأدمن

# التحقق من تسجيل دخول الأدمن

def check_admin_session(request: Request):

    if not request.session.get("admin_id"):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    return True

# إعداد تشفير كلمة المرور
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request):

    # التأكد أن الأدمن مسجل دخول
    if not request.session.get("admin_id"):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    db = SessionLocal()

    # عدد المنتجات
    products_count = db.query(Product).count()

    # عدد التصنيفات
    categories_count = db.query(Category).count()

    # عدد الطلبات
    orders_count = db.query(Order).count()

    # عدد البنرات
    banners_count = db.query(Banner).count()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "products_count": products_count,
            "categories_count": categories_count,
            "orders_count": orders_count,
            "banners_count": banners_count
        }
    )

# صفحة المنتجات
# صفحة المنتجات
@router.get("/products", response_class=HTMLResponse)
def products_page(request: Request):

    # التأكد أن الأدمن مسجل دخول
    if not request.session.get("admin_id"):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    db = SessionLocal()

    # جلب جميع المنتجات من قاعدة البيانات
    products = db.query(Product).options(
        joinedload(Product.category)
    ).all()

    # إغلاق الاتصال بقاعدة البيانات
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/products.html",
        context={
            "products": products,
            "error": request.query_params.get("error")
        }
    )

# صفحة الطلبات

@router.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request):

    # التأكد أن الأدمن مسجل دخول
    if not request.session.get("admin_id"):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    db = SessionLocal()

    orders = db.query(Order).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/orders.html",
        context={
            "orders": orders
        }
    )

# حذف طلب

@router.get("/orders/delete/{order_id}")
def delete_order(
    request: Request,
    order_id: int
):

    # التأكد من تسجيل دخول الأدمن
    if not request.session.get("admin_id"):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order:

        db.delete(order)

        db.commit()

    db.close()

    return RedirectResponse(
        url="/admin/orders",
        status_code=303
    )

# صفحة تفاصيل الطلب
@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order_details_page(
    request: Request,
    order_id: int
):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    from models import OrderItem

    items = db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()

    # حساب إجمالي الطلب
    total = 0

    for item in items:
        total += item.quantity * item.unit_price

    # تحميل المنتجات والألوان قبل إغلاق قاعدة البيانات
    for item in items:

        item.product

        if item.color:
            item.color

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/order_details.html",
        context={
            "order": order,
            "items": items,
            "total": total
        }
    )

# تحديث حالة الطلب والدفع

@router.post("/orders/{order_id}/update-status")
def update_order_status(

    order_id: int,

    payment_status: str = Form(...),

    order_status: str = Form(...)

):

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order:

        order.payment_status = payment_status

        order.order_status = order_status

        db.commit()

    db.close()

    return RedirectResponse(
        url=f"/admin/orders/{order_id}",
        status_code=303
    )

# صفحة عرض إثبات الدفع

@router.get("/orders/{order_id}/payment-proof", response_class=HTMLResponse)
def payment_proof_page(
    request: Request,
    order_id: int
):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/payment_proof.html",
        context={
            "order": order
        }
    )

# صفحة البنرات
@router.get("/banners", response_class=HTMLResponse)
def banners_page(request: Request):

    # التأكد أن الأدمن مسجل دخول
    if not request.session.get("admin_id"):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    db = SessionLocal()

    banners = db.query(Banner).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/banners.html",
        context={
            "banners": banners
        }
    )

@router.get("/banners/add", response_class=HTMLResponse)
def add_banner_page(request: Request):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    categories = db.query(Category).all()

    products = db.query(Product).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/add_banner.html",
        context={

            "categories": categories,

            "products": products

        }
    )

# حفظ البنر الجديد مع رفع الصورة
@router.post("/banners/add")
def add_banner(

    title: str = Form(None),

    subtitle: str = Form(None),

    is_visible: bool = Form(True),

    display_order: int = Form(0),

    button_label: str = Form(None),

    link_type: str = Form(None),

    category_id: int = Form(None),

    product_id: int = Form(None),

    image: UploadFile = File(...)

):

    db = SessionLocal()

    # حفظ صورة البنر داخل مجلد banners

    image_path = save_image(
        image,
        "banners"
    )

    # إنشاء رابط الزر تلقائياً

    button_link = None

    if link_type == "products":

        button_link = "/products"

    elif link_type == "category" and category_id:

        button_link = "/products?category=" + str(category_id)

    elif link_type == "product" and product_id:

        button_link = "/products/" + str(product_id)

    new_banner = Banner(

        title=title,

        subtitle=subtitle,

        image_path=image_path,

        is_visible=is_visible,

        display_order=display_order,

        button_label=button_label,

        button_link=button_link

    )

    db.add(new_banner)

    db.commit()

    db.refresh(new_banner)

    db.close()

    return RedirectResponse(
        url="/admin/banners",
        status_code=303
    )

# صفحة التصنيفات
@router.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request):

    # التأكد أن الأدمن مسجل دخول
    if not request.session.get("admin_id"):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    db = SessionLocal()

    categories = db.query(Category).all()

    for category in categories:

        category.products_count = len(category.products)

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/categories.html",
        context={
            "categories": categories,
            "error": request.query_params.get("error")
        }
    )

# صفحة منتجات تصنيف معين
@router.get(
    "/categories/{category_id}/products",
    response_class=HTMLResponse
)
def category_products_page(
    request: Request,
    category_id: int
):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    products = db.query(Product).filter(
        Product.category_id == category_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/category_products.html",
        context={
            "category": category,
            "products": products
        }
    )

# صفحة إضافة تصنيف جديد

@router.get("/categories/add", response_class=HTMLResponse)
def add_category_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/add_category.html"
    )

# حفظ التصنيف الجديد مع رفع الصورة

@router.post("/categories/add")
def add_category(

    name: str = Form(...),

    description: str = Form(None),

    display_order: int = Form(0),

    is_visible: bool = Form(True),

    image: UploadFile = File(...)

):

    db = SessionLocal()

    # حفظ صورة التصنيف داخل مجلد categories
    image_path = save_image(
        image,
        "categories"
    )

    new_category = Category(

        name=name,

        description=description,

        image_path=image_path,

        display_order=display_order,

        is_visible=is_visible

    )

    # إضافة التصنيف إلى قاعدة البيانات
    db.add(new_category)

    # حفظ البيانات
    db.commit()

    # تحديث البيانات بعد الحفظ
    db.refresh(new_category)

    # إغلاق الاتصال
    db.close()

    return RedirectResponse(
        url="/admin/categories",
        status_code=303
    )

# صفحة إضافة منتج جديد

@router.get("/products/add", response_class=HTMLResponse)
def add_product_page(request: Request):

    db = SessionLocal()

    categories = db.query(Category).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/add_product.html",
        context={
            "categories": categories
        }
    )

# حفظ المنتج الجديد مع رفع الصورة

@router.post("/products/add")
def add_product(

    request: Request,

    product_code: str = Form(...),

    name: str = Form(...),

    description: str = Form(None),

    regular_price: float = Form(None),

    sale_price: float = Form(None),

    has_discount: bool = Form(False),

    is_visible: bool = Form(True),

    sale_unit: str = Form(None),

    is_featured: bool = Form(False),

    is_new: bool = Form(False),

    category_id: int = Form(...),

    image: UploadFile = File(...)

):

    db = SessionLocal()

    # التأكد من وجود السعر الأساسي

    if regular_price is None:

        db.close()

        return RedirectResponse(
            url="/admin/products/add?error=price",
            status_code=303
        )

    try:

        # حفظ الصورة

        image_path = save_image(
            image,
            "products"
        )

        new_product = Product(

            product_code=product_code,

            name=name,

            description=description,

            main_image_path=image_path,

            regular_price=regular_price,

            sale_price=sale_price,

            has_discount=has_discount,

            is_visible=is_visible,

            sale_unit=sale_unit,

            is_featured=is_featured,

            is_new=is_new,

            category_id=category_id

        )

        db.add(new_product)

        db.commit()

        db.refresh(new_product)

        db.close()

        return RedirectResponse(
            url="/admin/products",
            status_code=303
        )

    except IntegrityError:

        db.rollback()

        db.close()

        return RedirectResponse(
            url="/admin/products/add?error=code",
            status_code=303
        )

# صفحة ألوان المنتج

@router.get("/products/{product_id}/colors", response_class=HTMLResponse)
def product_colors_page(
    request: Request,
    product_id: int
):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    colors = db.query(ProductColor).filter(
        ProductColor.product_id == product_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/product_colors.html",
        context={
            "product": product,
            "colors": colors
        }
    )

# صفحة إضافة لون جديد للمنتج

@router.get(
    "/products/{product_id}/colors/add",
    response_class=HTMLResponse
)
def add_product_color_page(
    request: Request,
    product_id: int
):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/add_product_color.html",
        context={
            "product": product
        }
    )

# حفظ لون جديد للمنتج مع رفع الصورة

@router.post("/products/{product_id}/colors/add")
def add_product_color(

    request: Request,

    product_id: int,

    color_name: str = Form(...),

    display_order: int = Form(0),

    is_visible: bool = Form(False),

    image: UploadFile = File(...)

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    image_path = save_image(
        image,
        "colors"
    )

    new_color = ProductColor(

        product_id=product_id,

        color_name=color_name,

        image_path=image_path,

        display_order=display_order,

        is_visible=is_visible

    )

    db.add(new_color)

    db.commit()

    db.refresh(new_color)

    db.close()

    return RedirectResponse(
        url=f"/admin/products/{product_id}/colors",
        status_code=303
    )

# صفحة تعديل البنر
# صفحة تعديل البنر

@router.get("/banners/{banner_id}/edit", response_class=HTMLResponse)
def edit_banner_page(

    request: Request,

    banner_id: int

):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    banner = db.query(Banner).filter(
        Banner.id == banner_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/edit_banner.html",
        context={
            "banner": banner
        }
    )

# حفظ تعديل البنر مع إمكانية تغيير الصورة

@router.post("/banners/{banner_id}/edit")
def edit_banner(

    request: Request,

    banner_id: int,

    title: str = Form(None),

    subtitle: str = Form(None),

    is_visible: bool = Form(True),

    display_order: int = Form(0),

    button_label: str = Form(None),

    link_type: str = Form(None),

    link_id: int = Form(None),

    image: UploadFile = File(None)

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    banner = db.query(Banner).filter(
        Banner.id == banner_id
    ).first()

    button_link = None

    if link_type == "products":

        button_link = "/products"

    elif link_type == "category" and link_id:

        button_link = "/products?category=" + str(link_id)

    elif link_type == "product" and link_id:

        button_link = "/products/" + str(link_id)

    banner.title = title

    banner.subtitle = subtitle

    banner.is_visible = is_visible

    banner.display_order = display_order

    banner.button_label = button_label

    banner.button_link = button_link

    # تغيير الصورة فقط إذا اختار المستخدم صورة جديدة

    old_image_path = None

    if image and image.filename:

        old_image_path = banner.image_path

        new_image_path = save_image(
            image,
            "banners"
        )

        banner.image_path = new_image_path

    db.commit()

    db.refresh(banner)

    db.close()

    if old_image_path:
        delete_image(old_image_path)

    return RedirectResponse(
        url="/admin/banners",
        status_code=303
    )

# حذف البنر

@router.get("/banners/{banner_id}/delete")
def delete_banner(

    request: Request,

    banner_id: int

):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    banner = db.query(Banner).filter(
        Banner.id == banner_id
    ).first()

    image_path = None

    if banner:

        image_path = banner.image_path

        db.delete(banner)

        db.commit()

    db.close()

    if image_path:
        delete_image(image_path)

    return RedirectResponse(
        url="/admin/banners",
        status_code=303
    )

# إخفاء البنر

@router.get("/banners/{banner_id}/hide")
def hide_banner(

    request: Request,

    banner_id: int

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    banner = db.query(Banner).filter(
        Banner.id == banner_id
    ).first()

    if banner:

        banner.is_visible = False

        db.commit()

    db.close()

    return RedirectResponse(
        url="/admin/banners",
        status_code=303
    )

# إظهار البنر

@router.get("/banners/{banner_id}/show")
def show_banner(

    request: Request,

    banner_id: int

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    banner = db.query(Banner).filter(
        Banner.id == banner_id
    ).first()

    if banner:

        banner.is_visible = True

        db.commit()

    db.close()

    return RedirectResponse(
        url="/admin/banners",
        status_code=303
    )

# صفحة تعديل التصنيف

@router.get("/categories/{category_id}/edit", response_class=HTMLResponse)
def edit_category_page(
    request: Request,
    category_id: int
):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/edit_category.html",
        context={
            "category": category
        }
    )

# حفظ تعديل التصنيف مع إمكانية تغيير الصورة
# حفظ تعديل التصنيف مع إمكانية تغيير الصورة
@router.post("/categories/{category_id}/edit")
def edit_category(

    request: Request,

    category_id: int,

    name: str = Form(...),

    description: str = Form(None),

    display_order: int = Form(0),

    is_visible: bool = Form(True),

    image: UploadFile = File(None)

):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    category.name = name

    category.description = description

    category.display_order = display_order

    category.is_visible = is_visible

    # تغيير الصورة فقط إذا اختار المستخدم صورة جديدة

    old_image_path = None

    if image and image.filename:

        old_image_path = category.image_path

        new_image_path = save_image(
            image,
            "categories"
        )

        category.image_path = new_image_path

    db.commit()

    db.refresh(category)

    db.close()

    if old_image_path:
        delete_image(old_image_path)

    return RedirectResponse(
        url="/admin/categories",
        status_code=303
    )

# حذف التصنيف
# حذف التصنيف

@router.get("/categories/{category_id}/delete")
def delete_category(

    request: Request,

    category_id: int

):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    image_path = None

    if category:

        # فحص هل يوجد منتجات داخل التصنيف
        products_count = db.query(Product).filter(
            Product.category_id == category_id
        ).count()

        if products_count > 0:

            db.close()

            return RedirectResponse(
                url="/admin/categories?error=has_products",
                status_code=303
            )

        image_path = category.image_path

        # حذف التصنيف إذا لا يوجد منتجات
        db.delete(category)

        db.commit()

    db.close()

    if image_path:
        delete_image(image_path)

    return RedirectResponse(
        url="/admin/categories",
        status_code=303
    )

# إخفاء التصنيف
# إخفاء التصنيف

@router.get("/categories/{category_id}/hide")
def hide_category(

    request: Request,

    category_id: int

):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category:

        category.is_visible = False

        db.commit()

    db.close()

    return RedirectResponse(
        url="/admin/categories",
        status_code=303
    )

# إظهار التصنيف
# إظهار التصنيف

@router.get("/categories/{category_id}/show")
def show_category(

    request: Request,

    category_id: int

):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category:

        category.is_visible = True

        db.commit()

    db.close()

    return RedirectResponse(
        url="/admin/categories",
        status_code=303
    )

# صفحة تعديل المنتج

@router.get("/products/{product_id}/edit", response_class=HTMLResponse)
def edit_product_page(
    request: Request,
    product_id: int
):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    categories = db.query(Category).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/edit_product.html",
        context={
            "product": product,
            "categories": categories
        }
    )

# حفظ تعديل المنتج مع إمكانية تغيير الصورة

@router.post("/products/{product_id}/edit")
def edit_product(

    product_id: int,

    product_code: str = Form(...),

    name: str = Form(...),

    description: str = Form(None),

    regular_price: float = Form(None),

    sale_price: float = Form(None),

    has_discount: bool = Form(False),

    is_visible: bool = Form(True),

    sale_unit: str = Form(None),

    is_featured: bool = Form(False),

    is_new: bool = Form(False),

    category_id: int = Form(...),

    image: UploadFile = File(None)

):

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    product.product_code = product_code

    product.name = name

    product.description = description

    # تغيير الصورة فقط إذا اختار المستخدم صورة جديدة

    old_image_path = None

    if image and image.filename:

        old_image_path = product.main_image_path

        new_image_path = save_image(
            image,
            "products"
        )

        product.main_image_path = new_image_path

    product.regular_price = regular_price

    product.sale_price = sale_price

    product.has_discount = has_discount

    product.is_visible = is_visible

    product.sale_unit = sale_unit

    product.is_featured = is_featured

    product.is_new = is_new

    product.category_id = category_id

    db.commit()

    db.refresh(product)

    db.close()

    if old_image_path:
        delete_image(old_image_path)

    return RedirectResponse(
        url="/admin/products",
        status_code=303
    )

# حذف المنتج

@router.get("/products/{product_id}/delete")
def delete_product(

    request: Request,

    product_id: int

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    product_image_path = None
    color_image_paths = []

    if product:

        # التأكد هل المنتج مستخدم في الطلبات
        from models import OrderItem

        order_item = db.query(OrderItem).filter(
            OrderItem.product_id == product_id
        ).first()

        if order_item:

            db.close()

            return RedirectResponse(
                url="/admin/products?error=has_orders",
                status_code=303
            )

        product_image_path = product.main_image_path

        product_colors = db.query(ProductColor).filter(
            ProductColor.product_id == product_id
        ).all()

        color_image_paths = [
            color.image_path
            for color in product_colors
            if color.image_path
        ]

        # حذف ألوان المنتج أولاً
        db.query(ProductColor).filter(
            ProductColor.product_id == product_id
        ).delete(
            synchronize_session=False
        )

        # حذف المنتج
        db.delete(product)

        db.commit()

    db.close()

    if product_image_path:
        delete_image(product_image_path)

    for color_image_path in color_image_paths:
        delete_image(color_image_path)

    return RedirectResponse(
        url="/admin/products",
        status_code=303
    )

# إخفاء المنتج
@router.get("/products/{product_id}/hide")
def hide_product(

    request: Request,

    product_id: int

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product:

        product.is_visible = False

        db.commit()

    db.close()

    return RedirectResponse(
        url="/admin/products",
        status_code=303
    )

# إظهار المنتج

@router.get("/products/{product_id}/show")
def show_product(

    request: Request,

    product_id: int

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product:

        product.is_visible = True

        db.commit()

    db.close()

    return RedirectResponse(
        url="/admin/products",
        status_code=303
    )

# صفحة تعديل لون المنتج

@router.get(
    "/products/{product_id}/colors/{color_id}/edit",
    response_class=HTMLResponse
)
def edit_product_color_page(
    request: Request,
    product_id: int,
    color_id: int
):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    color = db.query(ProductColor).filter(
        ProductColor.id == color_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin/edit_product_color.html",
        context={
            "product": product,
            "color": color
        }
    )

# حفظ تعديل لون المنتج مع إمكانية تغيير الصورة

@router.post(
    "/products/{product_id}/colors/{color_id}/edit"
)
def edit_product_color(

    request: Request,

    product_id: int,

    color_id: int,

    color_name: str = Form(...),

    display_order: int = Form(0),

    is_visible: bool = Form(True),

    image: UploadFile = File(None)

):

    # التأكد أن الأدمن مسجل دخول
    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    color = db.query(ProductColor).filter(
        ProductColor.id == color_id
    ).first()

    color.color_name = color_name

    color.display_order = display_order

    color.is_visible = is_visible

    # تغيير الصورة فقط إذا اختار المستخدم صورة جديدة

    old_image_path = None

    if image and image.filename:

        old_image_path = color.image_path

        new_image_path = save_image(
            image,
            "colors"
        )

        color.image_path = new_image_path

    db.commit()

    db.refresh(color)

    db.close()

    if old_image_path:
        delete_image(old_image_path)

    return RedirectResponse(
        url=f"/admin/products/{product_id}/colors",
        status_code=303
    )

# حذف لون المنتج مع التحقق من الطلبات

@router.get(
    "/products/{product_id}/colors/{color_id}/delete"
)
@router.get(
    "/products/{product_id}/colors/{color_id}/delete"
)
def delete_product_color(

    request: Request,

    product_id: int,

    color_id: int

):

    auth = check_admin_session(request)

    if auth != True:
        return auth

    db = SessionLocal()

    color = db.query(ProductColor).filter(
        ProductColor.id == color_id
    ).first()

    image_path = None

    if color:

        from models import OrderItem

        order_item = db.query(OrderItem).filter(
            OrderItem.color_id == color_id
        ).first()

        if order_item:

            db.close()

            return RedirectResponse(
                url=f"/admin/products/{product_id}/colors?error=has_orders",
                status_code=303
            )

        image_path = color.image_path

        db.delete(color)

        db.commit()

    db.close()

    if image_path:
        delete_image(image_path)

    return RedirectResponse(
        url=f"/admin/products/{product_id}/colors",
        status_code=303
    )

# إخفاء لون المنتج

@router.get(
    "/products/{product_id}/colors/{color_id}/hide"
)
def hide_product_color(
    product_id: int,
    color_id: int
):

    db = SessionLocal()

    color = db.query(ProductColor).filter(
        ProductColor.id == color_id
    ).first()

    if color:

        color.is_visible = False

        db.commit()

    db.close()

    return RedirectResponse(
        url=f"/admin/products/{product_id}/colors",
        status_code=303
    )

# إظهار لون المنتج

@router.get(
    "/products/{product_id}/colors/{color_id}/show"
)
def show_product_color(
    product_id: int,
    color_id: int
):

    db = SessionLocal()

    color = db.query(ProductColor).filter(
        ProductColor.id == color_id
    ).first()

    if color:

        color.is_visible = True

        db.commit()

    db.close()

    return RedirectResponse(
        url=f"/admin/products/{product_id}/colors",
        status_code=303
    )

# صفحة تسجيل دخول الأدمن

@router.get("/login", response_class=HTMLResponse)
def admin_login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html"
    )

# صفحة تسجيل دخول الأدمن

@router.get("/login", response_class=HTMLResponse)
def admin_login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html"
    )

@router.post("/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    db = SessionLocal()

    # إزالة المسافات الزائدة من اسم المستخدم
    username = username.strip()

    # البحث عن الأدمن
    admin = db.query(Admin).filter(
        Admin.username == username
    ).first()

    # إذا اسم المستخدم غير موجود
    if not admin:
        print("LOGIN DEBUG: USERNAME NOT FOUND")

        db.close()

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    print("LOGIN DEBUG: USERNAME FOUND")

    # التحقق من كلمة المرور
    password_correct = pwd_context.verify(
        password,
        admin.password_hash
    )

    # إذا كلمة المرور خطأ
    if not password_correct:
        print("LOGIN DEBUG: PASSWORD INCORRECT")

        db.close()

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    print("LOGIN DEBUG: PASSWORD CORRECT")

    # حفظ بيانات الأدمن في الجلسة
    request.session["admin_id"] = admin.id
    request.session["admin_username"] = admin.username

    db.close()

    print("LOGIN DEBUG: LOGIN SUCCESS")

    return RedirectResponse(
        url="/admin/",
        status_code=303
    )

# تسجيل خروج الأدمن

@router.get("/logout")
def admin_logout(
    request: Request
):

    # حذف بيانات الأدمن من الجلسة
    request.session.clear()

    return RedirectResponse(
        url="/admin/login",
        status_code=303
    )