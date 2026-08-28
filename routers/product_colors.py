from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas


router = APIRouter(
    prefix="/product-colors",
    tags=["Product Colors"]
)


# عرض جميع ألوان المنتجات
@router.get("/")
def get_product_colors(db: Session = Depends(get_db)):

    colors = db.query(models.ProductColor).all()

    return colors



# إضافة لون جديد لمنتج
@router.post("/")
def create_product_color(
    color: schemas.ProductColorCreate,
    db: Session = Depends(get_db)
):

    new_color = models.ProductColor(

        product_id=color.product_id,

        color_name=color.color_name,

        image_path=color.image_path,

        display_order=color.display_order,

        is_visible=color.is_visible

    )


    db.add(new_color)

    db.commit()

    db.refresh(new_color)


    return new_color

# عرض ألوان منتج معين فقط
@router.get("/product/{product_id}")
def get_colors_by_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    colors = db.query(models.ProductColor).filter(
        models.ProductColor.product_id == product_id,
        models.ProductColor.is_visible == True
    ).order_by(
        models.ProductColor.display_order
    ).all()


    return colors