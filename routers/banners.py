from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas


router = APIRouter(
    prefix="/banners",
    tags=["Banners"]
)


# عرض جميع البنرات
@router.get("/")
def get_banners(db: Session = Depends(get_db)):

    banners = db.query(models.Banner).all()

    return banners



# إضافة بانر جديد
@router.post("/")
def create_banner(
    banner: schemas.BannerCreate,
    db: Session = Depends(get_db)
):
    try:
        new_banner = models.Banner(
            title=banner.title,
            subtitle=banner.subtitle,
            image_path=banner.image_path,
            is_visible=banner.is_visible,
            display_order=banner.display_order,
            button_label=banner.button_label,
            button_link=banner.button_link
        )

        db.add(new_banner)
        db.commit()
        db.refresh(new_banner)

        return new_banner

    except Exception as e:
        print("ERROR:", e)
        db.rollback()
        raise e