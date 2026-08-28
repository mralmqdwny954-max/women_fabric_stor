from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Schema إضافة قسم جديد
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_path: Optional[str] = None
    display_order: Optional[int] = 0
    is_visible: Optional[bool] = True


# Schema عرض القسم
class Category(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_path: Optional[str]
    display_order: int
    is_visible: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# Product Schemas
# =========================

class ProductCreate(BaseModel):

    product_code: str

    name: str

    description: Optional[str] = None

    main_image_path: Optional[str] = None

    regular_price: Optional[float] = None

    sale_price: Optional[float] = None

    has_discount: bool = False

    is_visible: bool = True

    sale_unit: Optional[str] = None

    is_featured: bool = False

    is_new: bool = False

    category_id: int
    



class Product(BaseModel):

    id: int

    product_code: str

    name: str

    description: Optional[str]

    main_image_path: Optional[str]

    regular_price: Optional[float]

    sale_price: Optional[float]

    has_discount: bool

    is_visible: bool

    sale_unit: Optional[str]

    is_featured: bool

    is_new: bool

    category_id: int

    colors: list["ProductColor"] = []


    class Config:
        from_attributes = True

# ==========================
# Product Color Schemas
# ==========================

class ProductColorCreate(BaseModel):
    product_id: int
    color_name: str
    image_path: str
    display_order: int = 0
    is_visible: bool = True

class ProductColor(BaseModel):

    id: int
    product_id: int
    color_name: str
    image_path: str
    display_order: int
    is_visible: bool

    class Config:
        from_attributes = True

# ==========================
# Banner Schemas
# ==========================

class BannerCreate(BaseModel):

    title: Optional[str] = None

    subtitle: Optional[str] = None

    image_path: Optional[str] = None

    is_visible: bool = True

    display_order: int = 0

    button_label: Optional[str] = None

    button_link: Optional[str] = None



class Banner(BaseModel):

    id: int

    title: Optional[str] = None

    subtitle: Optional[str] = None

    image_path: Optional[str] = None

    is_visible: bool

    display_order: int

    button_label: Optional[str] = None

    button_link: Optional[str] = None

    created_at: datetime


    class Config:
        from_attributes = True



# ==========================
# Order Schemas
# ==========================

class OrderCreate(BaseModel):

    order_number: str

    customer_name: str

    phone: str

    city: str

    address: str

    payment_method: str

    payment_status: str = "pending"

    payment_proof_path: Optional[str] = None

    order_status: str = "new"

    customer_notes: Optional[str] = None

    items: list["OrderItemCreate"] = []


class Order(BaseModel):

    id: int

    order_number: str

    customer_name: str

    phone: str

    city: str

    address: str

    payment_method: str

    payment_status: str

    payment_proof_path: Optional[str] = None

    order_status: str

    customer_notes: Optional[str] = None

    created_at: datetime

    items: list["OrderItem"] = []


    class Config:
        from_attributes = True



# ==========================
# Order Item Schemas
# ==========================

class OrderItemCreate(BaseModel):

    order_id: int

    product_id: int

    color_id: Optional[int] = None

    quantity: int

    unit_price: float

    subtotal: float

    item_image_path: str

    sale_unit: Optional[str] = None



class OrderItem(BaseModel):

    id: int

    order_id: int

    product_id: int

    color_id: Optional[int] = None

    quantity: int

    unit_price: float

    subtotal: float

    item_image_path: str

    sale_unit: Optional[str] = None


    class Config:
        from_attributes = True
Product.model_rebuild()
Order.model_rebuild()