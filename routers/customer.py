from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session, joinedload

from database import get_db

from models import (
    Banner,
    Category,
    Product,
    ProductColor,
    CartItem,
    Order,
    OrderItem
)


import uuid
import os





# راوتر العميل
router = APIRouter(
    tags=["Customer"]
)



# مكان ملفات HTML
templates = Jinja2Templates(
    directory="templates"
)

# تحويل الريال اليمني إلى الريال السعودي

def to_sar(price):

    if price is None:
        return 0

    return round(float(price) / 410, 2)


templates.env.filters["sar"] = to_sar




# ==============================
# الصفحة الرئيسية
# ==============================

@router.get("/", response_class=HTMLResponse)
def home_page(
    request: Request,
    db: Session = Depends(get_db)
):


    banners = db.query(Banner).filter(
        Banner.is_visible == True
    ).order_by(
        Banner.display_order
    ).all()



    categories = db.query(Category).filter(
        Category.is_visible == True
    ).order_by(
        Category.display_order
    ).all()



    featured_products = db.query(Product).filter(
        Product.is_featured == True,
        Product.is_visible == True
    ).all()



    new_products = db.query(Product).filter(
        Product.is_new == True,
        Product.is_visible == True
    ).all()



    return templates.TemplateResponse(
        request=request,
        name="customer/home.html",
        context={

            "banners": banners,

            "categories": categories,

            "featured_products": featured_products,

            "new_products": new_products

        }
    )







# ==============================
# صفحة جميع المنتجات
# ==============================

@router.get("/products", response_class=HTMLResponse)
def products_page(
    request: Request,
    db: Session = Depends(get_db)
):


    # نأخذ رقم القسم إذا كان موجودًا في الرابط
    category_id = request.query_params.get("category")



    if category_id:

        products = db.query(Product).filter(
            Product.category_id == int(category_id),
            Product.is_visible == True
        ).all()


    else:

        products = db.query(Product).filter(
            Product.is_visible == True
        ).all()



    return templates.TemplateResponse(
    request=request,
    name="customer/products.html",
    context={

        "products": products,

        "category": db.query(Category).filter(
            Category.id == int(category_id)
        ).first() if category_id else None

    }
)



# ==============================
# صفحة منتجات قسم معين
# ==============================

@router.get("/category/{category_id}", response_class=HTMLResponse)
def category_products_page(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db)
):


    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_visible == True
    ).first()



    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_visible == True
    ).all()



    return templates.TemplateResponse(
        request=request,
        name="customer/category_products.html",
        context={

            "category": category,

            "products": products

        }
    )

# ==============================
# صفحة جميع الأقسام للعميل
# ==============================

@router.get("/customer/categories", response_class=HTMLResponse)
def customer_categories_page(
    request: Request,
    db: Session = Depends(get_db)
):


    categories = db.query(Category).filter(
        Category.is_visible == True
    ).order_by(
        Category.display_order
    ).all()



    return templates.TemplateResponse(
        request=request,
        name="customer/categories.html",
        context={

            "categories": categories

        }
    )



# ==============================
# صفحة تفاصيل المنتج
# ==============================

@router.get("/products/{product_id}", response_class=HTMLResponse)
def product_details(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):


    product = db.query(Product).options(
        joinedload(Product.colors)
    ).filter(
        Product.id == product_id,
        Product.is_visible == True
    ).first()



    if product:

        product.colors = [
            color for color in product.colors
            if color.is_visible
        ]



    return templates.TemplateResponse(
        request=request,
        name="customer/product_details.html",
        context={

            "product": product

        }
    )







# ==============================
# طلب السلة عبر الواتساب
# ==============================

@router.get("/cart-whatsapp", response_class=HTMLResponse)
def cart_whatsapp_page(
    request: Request,
    db: Session = Depends(get_db)
):


    session_id = request.session.get(
        "cart_session_id"
    )



    cart_items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()



    total = 0



    for item in cart_items:

        total += item.subtotal





    return templates.TemplateResponse(
        request=request,
        name="customer/whatsapp_order.html",
        context={

            "cart_items": cart_items,

            "total": total

        }
    )

# ==============================
# صفحة إتمام الطلب من السلة
# ==============================

@router.get("/cart/checkout", response_class=HTMLResponse)
def cart_checkout_page(
    request: Request,
    db: Session = Depends(get_db)
):


    session_id = request.session.get(
        "cart_session_id"
    )


    cart_items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()



    total = 0


    for item in cart_items:

        total += item.subtotal





    return templates.TemplateResponse(
        request=request,
        name="customer/cart_checkout.html",
        context={

            "cart_items": cart_items,

            "total": total

        }
    )








# ==============================
# حفظ طلب السلة
# ==============================

@router.post("/cart/checkout")
def create_cart_order(
    request: Request,

    customer_name: str = Form(...),

    phone: str = Form(...),

    city: str = Form(...),

    address: str = Form(...),

    payment: str = Form(...),

    customer_notes: str = Form(None),

    payment_proof: UploadFile = File(None),

    db: Session = Depends(get_db)

):


    session_id = request.session.get(
        "cart_session_id"
    )



    cart_items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()



    if not cart_items:

        return RedirectResponse(
            "/cart",
            status_code=303
        )





    payment_path = None



    if payment_proof:


        file_name = (

            str(uuid.uuid4())

            +

            "_"

            +

            payment_proof.filename

        )



        upload_folder = "uploads/payment"



        os.makedirs(
            upload_folder,
            exist_ok=True
        )



        file_path = (

            upload_folder

            +

            "/"

            +

            file_name

        )



        with open(
            file_path,
            "wb"
        ) as file:


            file.write(
                payment_proof.file.read()
            )



        payment_path = file_path






    order_number = (

        "ORD-"

        +

        str(uuid.uuid4())[:8]

    )






    new_order = Order(


        order_number=order_number,


        customer_name=customer_name,


        phone=phone,


        city=city,


        address=address,


        payment_method=payment,


        payment_status="pending",


        payment_proof_path=payment_path,


        order_status="new",


        customer_notes=customer_notes


    )



    db.add(new_order)


    db.commit()


    db.refresh(new_order)







    for item in cart_items:


        order_item = OrderItem(


            order_id=new_order.id,


            product_id=item.product_id,


            color_id=item.color_id,


            quantity=item.quantity,


            unit_price=item.unit_price,


            subtotal=item.subtotal,


            item_image_path=item.color.image_path,


            sale_unit=item.sale_unit


        )



        db.add(order_item)



    db.commit()



    db.refresh(new_order)






    # حذف السلة بعد نجاح الطلب

    for item in cart_items:

        db.delete(item)



    db.commit()






    return templates.TemplateResponse(

        request=request,

        name="customer/order_success.html",

        context={

            "order": new_order

        }

    )
# ==============================
# صفحة من نحن
# ==============================

@router.get("/about", response_class=HTMLResponse)
def about(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="customer/about.html",
        context={}
    )