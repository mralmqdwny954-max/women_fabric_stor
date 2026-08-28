from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# عرض جميع الأقسام
@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories


# إضافة قسم جديد
@router.post("/")
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    new_category = models.Category(
        name=category.name,
        description=category.description,
        image_path=category.image_path,
        display_order=category.display_order,
        is_visible=category.is_visible
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category