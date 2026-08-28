from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from database import get_db
import models
import schemas


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# عرض جميع الطلبات
@router.get("/")
def get_orders(
    db: Session = Depends(get_db)
):

    orders = db.query(models.Order).options(
        joinedload(models.Order.items)
    ).all()

    return orders



# إنشاء طلب جديد مع تفاصيل الطلب
@router.post("/")
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):

    new_order = models.Order(

        order_number=order.order_number,

        customer_name=order.customer_name,

        phone=order.phone,

        city=order.city,

        address=order.address,

        payment_method=order.payment_method,

        payment_status=order.payment_status,

        payment_proof_path=order.payment_proof_path,

        order_status=order.order_status,

        customer_notes=order.customer_notes
    )


    db.add(new_order)

    db.commit()

    db.refresh(new_order)


    for item in order.items:

        new_item = models.OrderItem(

            order_id=new_order.id,

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


    db.refresh(new_order)


    return new_order