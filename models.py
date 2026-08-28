from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# جدول التصنيفات
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    image_path = Column(String(255), nullable=True)

    display_order = Column(Integer, default=0)

    is_visible = Column(Boolean, default=True)

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )


    # العلاقة مع المنتجات
    products = relationship(
        "Product",
        back_populates="category"
    )



# جدول المنتجات
class Product(Base):
    __tablename__ = "products"


    id = Column(Integer, primary_key=True, index=True)

    product_code = Column(
        String(100),
        unique=True,
        nullable=False
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    main_image_path = Column(
        String(255),
        nullable=True
    )

    regular_price = Column(
        Numeric(10, 2),
        nullable=True
    )

    sale_price = Column(
        Numeric(10, 2),
        nullable=True
    )

    has_discount = Column(
        Boolean,
        default=False
    )

    is_visible = Column(
        Boolean,
        default=True
    )

    sale_unit = Column(
        String(50),
        nullable=True
    )

    is_featured = Column(
        Boolean,
        default=False
    )

    is_new = Column(
        Boolean,
        default=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )


    # العلاقة مع التصنيف
    category = relationship(
        "Category",
        back_populates="products"
    )


    # العلاقة مع الألوان
    colors = relationship(
        "ProductColor",
        back_populates="product"
    )


    # العلاقة مع تفاصيل الطلب
    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )



# جدول ألوان المنتجات
class ProductColor(Base):
    __tablename__ = "product_colors"


    id = Column(Integer, primary_key=True, index=True)


    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )


    color_name = Column(
        String(100),
        nullable=False
    )


    image_path = Column(
        String(255),
        nullable=False
    )


    display_order = Column(
        Integer,
        default=0
    )


    is_visible = Column(
        Boolean,
        default=True
    )


    # العلاقة مع المنتج
    product = relationship(
        "Product",
        back_populates="colors"
    )


    # العلاقة مع تفاصيل الطلب
    order_items = relationship(
        "OrderItem",
        back_populates="color"
    )



# جدول البنرات
class Banner(Base):
    __tablename__ = "banners"


    id = Column(Integer, primary_key=True, index=True)


    title = Column(
        String(255),
        nullable=True
    )


    subtitle = Column(
        Text,
        nullable=True
    )


    image_path = Column(
        String(255),
        nullable=True
    )


    is_visible = Column(
        Boolean,
        default=True
    )


    display_order = Column(
        Integer,
        default=0
    )


    button_label = Column(
        String(100),
        nullable=True
    )


    button_link = Column(
        String(255),
        nullable=True
    )


    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )



# جدول الطلبات
class Order(Base):
    __tablename__ = "orders"


    id = Column(Integer, primary_key=True, index=True)


    order_number = Column(
        String(100),
        unique=True,
        nullable=False
    )


    customer_name = Column(
        String(100),
        nullable=False
    )


    phone = Column(
        String(30),
        nullable=False
    )


    city = Column(
        String(100),
        nullable=False
    )


    address = Column(
        Text,
        nullable=False
    )


    payment_method = Column(
        String(50),
        nullable=False
    )


    payment_status = Column(
        String(50),
        default="pending"
    )


    payment_proof_path = Column(
        String(255),
        nullable=True
    )


    order_status = Column(
        String(50),
        default="new"
    )


    customer_notes = Column(
        Text,
        nullable=True
    )


    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )


    # العلاقة مع تفاصيل الطلب
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )



# جدول تفاصيل الطلب
class OrderItem(Base):
    __tablename__ = "order_items"


    id = Column(Integer, primary_key=True, index=True)


    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )


    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )


    color_id = Column(
        Integer,
        ForeignKey("product_colors.id"),
        nullable=True
    )


    quantity = Column(
        Integer,
        nullable=False
    )


    unit_price = Column(
        Numeric(10,2),
        nullable=False
    )


    subtotal = Column(
    Numeric(10,2),
    nullable=False
    )


    item_image_path = Column(
        String(255),
        nullable=False
    )


    sale_unit = Column(
        String(50),
        nullable=True
    )


    # العلاقة مع الطلب
    order = relationship(
        "Order",
        back_populates="items"
    )


    # العلاقة مع المنتج
    product = relationship(
        "Product",
        back_populates="order_items"
    )


    # العلاقة مع اللون
    color = relationship(
        "ProductColor",
        back_populates="order_items"
    )



# جدول مستخدم الأدمن
class Admin(Base):
    __tablename__ = "admins"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    username = Column(
        String(100),
        unique=True,
        nullable=False
    )


    password_hash = Column(
        String(255),
        nullable=False
    )


    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )



# جدول سلة المشتريات
class CartItem(Base):
    __tablename__ = "cart_items"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # رقم مؤقت يميز جهاز العميل
    session_id = Column(
        String(255),
        nullable=False
    )


    # المنتج الموجود في السلة
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )


    # اللون المختار
    color_id = Column(
        Integer,
        ForeignKey("product_colors.id"),
        nullable=True
    )


    # الكمية المطلوبة
    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )


    # سعر القطعة أو المتر وقت الإضافة
    unit_price = Column(
        Numeric(10,2),
        nullable=False
    )


    # المجموع = الكمية × السعر
    subtotal = Column(
        Numeric(10,2),
        nullable=False
    )


    # وحدة البيع (متر / قطعة)
    sale_unit = Column(
        String(50),
        nullable=True
    )


    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )


    # العلاقة مع المنتج
    product = relationship(
        "Product"
    )


    # العلاقة مع اللون
    color = relationship(
        "ProductColor"
    )