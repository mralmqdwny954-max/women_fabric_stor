import os
from uuid import uuid4
from PIL import Image, ImageOps


def save_image(file, folder):

    # مكان حفظ الصور
    upload_dir = f"uploads/{folder}"

    # إنشاء المجلد
    os.makedirs(
        upload_dir,
        exist_ok=True
    )


    # اسم جديد للصورة
    filename = f"{uuid4()}.webp"


    # المسار النهائي
    file_path = os.path.join(
        upload_dir,
        filename
    )


    # فتح الصورة
    image = Image.open(file.file)



    # إعدادات البنرات
    if folder == "banners":

        # مقاس البنر المناسب للموقع
        target_size = (1600, 700)

    else:

        # صور المنتجات
        target_size = (800, 1000)



    # قص وتعديل الحجم تلقائياً
    image = ImageOps.fit(
        image,
        target_size,
        Image.LANCZOS
    )



    # تحويل الألوان
    image = image.convert("RGB")



    # حفظ WebP مضغوط
    image.save(
        file_path,
        "WEBP",
        quality=80,
        optimize=True,
        method=6
    )



    # رابط الصورة
    image_url = file_path.replace(
        "\\",
        "/"
    )


    return image_url