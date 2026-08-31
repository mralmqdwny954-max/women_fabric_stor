import os
from uuid import uuid4
from io import BytesIO

from PIL import Image, ImageOps

import cloudinary
import cloudinary.uploader


# إعداد Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def save_image(file, folder):

    # إنشاء اسم فريد للصورة
    image_id = str(uuid4())

    # فتح الصورة
    image = Image.open(file.file)

    # إعدادات البنرات
    if folder == "banners":
        target_size = (1600, 700)

    else:
        # المنتجات - الألوان - التصنيفات
        target_size = (800, 1000)

    # قص وتعديل الحجم
    image = ImageOps.fit(
        image,
        target_size,
        Image.LANCZOS
    )

    # تحويل الألوان
    image = image.convert("RGB")

    # حفظ الصورة في الذاكرة بصيغة WebP
    image_buffer = BytesIO()

    image.save(
        image_buffer,
        "WEBP",
        quality=80,
        optimize=True,
        method=6
    )

    image_buffer.seek(0)

    # رفع الصورة إلى Cloudinary
    cloudinary.uploader.upload(
        image_buffer,
        folder=f"women_fabric_store/{folder}",
        public_id=image_id,
        format="webp",
        resource_type="image",
        overwrite=True
    )

    # نحفظ في قاعدة البيانات مسارًا نسبيًا
    # حتى تستمر ملفات HTML الحالية بالعمل بدون تعديل
    image_path = f"media/{folder}/{image_id}.webp"

    return image_path


def delete_image(image_path):

    # إذا لا يوجد مسار، لا نفعل شيئًا
    if not image_path:
        return

    # نحذف فقط صور Cloudinary الجديدة
    # ولا نلمس صور uploads القديمة
    if not image_path.startswith("media/"):
        return

    try:

        # مثال:
        # media/products/abc.webp
        # يتحول إلى:
        # women_fabric_store/products/abc

        relative_path = image_path[len("media/"):]

        public_id = os.path.splitext(relative_path)[0]

        public_id = f"women_fabric_store/{public_id}"

        cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
            invalidate=True
        )

    except Exception as error:

        # لا نجعل فشل حذف الصورة يكسر عملية حذف المنتج
        print("Cloudinary image delete failed:")
        print(error)