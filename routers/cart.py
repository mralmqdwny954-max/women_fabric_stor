from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from database import get_db

from models import (
    CartItem,
    Product,
    ProductColor
)



# راوتر السلة
router = APIRouter(
    tags=["Cart"]
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




# إنشاء أو جلب جلسة العميل
def get_cart_session(request: Request):


    if "cart_session_id" not in request.session:

        import uuid

        request.session["cart_session_id"] = str(uuid.uuid4())


    return request.session["cart_session_id"]







# إضافة منتج إلى السلة
@router.post("/cart/add")
def add_to_cart(
    request: Request,

    # استقبال البيانات من الفورم
    product_id: int = Form(...),

    color_id: int = Form(...),

    quantity: int = Form(...),

    db: Session = Depends(get_db)
):


    # جلب جلسة العميل
    session_id = get_cart_session(request)



    # جلب المنتج
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()



    # جلب اللون
    color = db.query(ProductColor).filter(
        ProductColor.id == color_id
    ).first()



    # تحديد السعر
    if product.sale_price:

        price = product.sale_price

    else:

        price = product.regular_price





    # حساب المجموع
    subtotal = price * quantity





    # إنشاء عنصر جديد في السلة
    cart_item = CartItem(


        session_id=session_id,


        product_id=product.id,


        color_id=color.id,


        quantity=quantity,


        unit_price=price,


        subtotal=subtotal,


        sale_unit=product.sale_unit


    )



    db.add(cart_item)


    db.commit()



    print("CART ADDED:")
    print(session_id)
    print(product.id)
    print(color.id)
    print(quantity)



    return {

        "message": "تمت إضافة المنتج إلى السلة"

    }








# عرض السلة
@router.get("/cart", response_class=HTMLResponse)
def view_cart(

    request: Request,

    db: Session = Depends(get_db)

):


    session_id = get_cart_session(request)



    cart_items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()



    total = 0



    for item in cart_items:

        total += item.subtotal





    return templates.TemplateResponse(

        request=request,

        name="customer/cart.html",

        context={


            "cart_items": cart_items,


            "total": total


        }

    )

# ==============================
# حذف منتج من السلة
# ==============================

@router.get("/cart/delete/{item_id}")
def delete_cart_item(

    item_id: int,

    request: Request,

    db: Session = Depends(get_db)

):


    # جلب جلسة العميل الحالية
    session_id = get_cart_session(request)



    # البحث عن المنتج داخل سلة هذا العميل فقط
    cart_item = db.query(CartItem).filter(

        CartItem.id == item_id,

        CartItem.session_id == session_id

    ).first()



    # إذا وجد المنتج نحذفه
    if cart_item:

        db.delete(cart_item)

        db.commit()



    # العودة إلى صفحة السلة
    return RedirectResponse(

        url="/cart",

        status_code=303

    )


# ==================================
# تحديث كمية المنتج في السلة
# ==================================

@router.get("/cart/update/{item_id}/{quantity}")
def update_cart_quantity(
    item_id: int,
    quantity: int,
    request: Request,
    db: Session = Depends(get_db)
):


    # جلب جلسة العميل
    session_id = get_cart_session(request)



    # البحث عن المنتج داخل سلة نفس العميل
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.session_id == session_id
    ).first()



    if cart_item:


        # تحديث الكمية
        cart_item.quantity = quantity



        # إعادة حساب المجموع
        cart_item.subtotal = (
            cart_item.unit_price * quantity
        )



        db.commit()



    return RedirectResponse(
        "/cart",
        status_code=303
    )


# ==================================
# صفحة إتمام طلب السلة
# ==================================

@router.get("/cart/checkout", response_class=HTMLResponse)
def cart_checkout(
    request: Request,
    db: Session = Depends(get_db)
):


    session_id = get_cart_session(request)


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


# ==================================
# صفحة طلب السلة عبر الواتساب
# ==================================

@router.get("/cart/whatsapp", response_class=HTMLResponse)
def cart_whatsapp(
    request: Request,
    db: Session = Depends(get_db)
):


    session_id = get_cart_session(request)


    cart_items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()



    total = 0


    for item in cart_items:

        total += item.subtotal



    return templates.TemplateResponse(
        request=request,
        name="customer/cart_whatsapp.html",
        context={

            "cart_items": cart_items,

            "total": total

        }
    )