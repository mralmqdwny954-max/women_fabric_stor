from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas


router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)


# عرض جميع تفاصيل الطلبات
@router.get("/")
def get_order_items(
    db: Session = Depends(get_db)
):

    items = db.query(models.OrderItem).all()

    return items



# إضافة تفاصيل طلب جديدة
@router.post("/")
def create_order_item(
    item: schemas.OrderItemCreate,
    db: Session = Depends(get_db)
):

    new_item = models.OrderItem(

        order_id=item.order_id,

        product_id=item.product_id,

        color_id=item.color_id,

        quantity=item.quantity,

        unit_price=item.unit_price,

        subtotal=item.subtotal,

        item_image_path=item.item_image_path,

        sale_unit=item.sale_unit

    )


    db.add(new_item)

    db.commit()

    db.refresh(new_item)


    return new_item