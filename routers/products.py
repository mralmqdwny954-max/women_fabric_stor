from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
import models
from utils.upload import save_image



router = APIRouter(
    prefix="/products",
    tags=["Products"]
)



templates = Jinja2Templates(
    directory="templates"
)



# ==================================
# صفحة جميع المنتجات للعميل
# ==================================

@router.get("/", response_class=HTMLResponse)
def products_page(
    request: Request,
    category: int = None,
    db: Session = Depends(get_db)
):


    query = db.query(models.Product).filter(
        models.Product.is_visible == True
    )


    # إذا اختار العميل قسم معين
    if category:

        query = query.filter(
            models.Product.category_id == category
        )


    products = query.all()



    return templates.TemplateResponse(
        request=request,
        name="customer/products.html",
        context={

            "products": products

        }
    )





# ==================================
# إنشاء منتج جديد من الأدمن
# ==================================

@router.post("/")
def create_product(

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

    image: UploadFile = File(...),

    db: Session = Depends(get_db)

):


    image_path = save_image(
        image,
        "products"
    )



    new_product = models.Product(

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



    return new_product