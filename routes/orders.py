from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from settings import Session
from models import Menu, Order, OrderStatus
from sqlalchemy.orm import joinedload
import sqlite3
import os

bp = Blueprint('orders', __name__)

@bp.route("/menu")
def menu():
    from app import t
    current_lang = session.get('language', 'uk')

    with Session() as db_session:
        menu_items = db_session.query(Menu).filter(Menu.active == True).all()
        categories = sorted(list(set(item.category for item in menu_items if item.category)))
    return render_template("menu.html", menu_items=menu_items, categories=categories,t=lambda key: t(key, current_lang), lang=current_lang)

@bp.route("/add_to_cart/<int:item_id>", methods=["POST"])
@login_required
def add_to_cart(item_id):
    quantity = int(request.form.get("quantity", 1))
    print(f"DEBUG: Adding to cart - item_id: {item_id}, quantity: {quantity}, user: {current_user.id}")
    
    with Session() as db_session:
        menu_item = db_session.query(Menu).filter(Menu.id == item_id).first()
        if not menu_item:
            flash("Страву не знайдено", "error")
            return redirect(url_for("orders.menu"))
        
        print(f"DEBUG: Menu item found - {menu_item.name}")
        
        # Проверяем, есть ли уже такой товар в корзине (со статусом PENDING)
        existing_order = db_session.query(Order).filter(
            Order.user_id == current_user.id,
            Order.menu_id == item_id,
            Order.status == OrderStatus.PENDING
        ).first()
        
        if existing_order:
            print(f"DEBUG: Existing order found - updating quantity")
            existing_order.quantity += quantity
            existing_order.total_price = existing_order.menu_item.price * existing_order.quantity
        else:
            # Создаем новый заказ
            print(f"DEBUG: Creating new order")
            new_order = Order(
                user_id=current_user.id,
                menu_id=item_id,
                quantity=quantity,
                total_price=menu_item.price * quantity
            )
            db_session.add(new_order)
        
        db_session.commit()
        print(f"DEBUG: Order saved successfully")
        
        flash(f"'{menu_item.name}' додано до замовлення!", "success")
        return redirect(url_for("orders.menu"))

@bp.route("/cart")
@login_required
def cart():
    print(f"DEBUG: Cart page - user: {current_user.id}")
    from app import t
    current_lang = session.get('language', 'uk')
    
    with Session() as db_session:
        # Используем eager loading для загрузки связанных данных
        cart_items = db_session.query(Order).options(
            joinedload(Order.menu_item)
        ).filter(
            Order.user_id == current_user.id,
            Order.status == OrderStatus.PENDING
        ).all()
        
        print(f"DEBUG: Found {len(cart_items)} items in cart")
        for item in cart_items:
            print(f"DEBUG: Cart item - ID: {item.id}, Menu: {item.menu_item.name}, Qty: {item.quantity}")
        
        total = sum(item.total_price for item in cart_items)
        
        # Получаем фоновое изображение
        from app import get_background_settings
        images = get_background_settings()
        
        return render_template("cart.html", 
                             cart_items=cart_items, 
                             total=total,
                             background_image=images.get('cart_background_image'),
                               t=lambda key: t(key, current_lang),
                               lang=current_lang)

@bp.route("/update_cart/<int:order_id>", methods=["POST"])
@login_required
def update_cart(order_id):
    quantity = int(request.form.get("quantity", 1))
    with Session() as db_session:
        order = db_session.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).first()
        if order and quantity > 0:
            order.quantity = quantity
            order.total_price = order.menu_item.price * quantity
            db_session.commit()
            flash("Кількість оновлено!", "success")
        elif order and quantity == 0:
            db_session.delete(order)
            db_session.commit()
            flash("Страву видалено з кошика!", "success")
        return redirect(url_for("orders.cart"))

@bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    with Session() as db_session:
        # Подтверждаем все pending заказы пользователя
        pending_orders = db_session.query(Order).filter(
            Order.user_id == current_user.id,
            Order.status == OrderStatus.PENDING
        ).all()
        for order in pending_orders:
            order.status = OrderStatus.CONFIRMED
        db_session.commit()
        flash("Замовлення оформлено! Очікуйте підтвердження.", "success")
        return redirect(url_for("orders.menu"))

@bp.route("/order_history")
@login_required
def order_history():
    print(f"DEBUG: Order history page - user: {current_user.id}")
    from app import t
    current_lang = session.get('language', 'uk')
    
    with Session() as db_session:
        # Используем eager loading для загрузки связанных данных
        orders_list = db_session.query(Order).options(
            joinedload(Order.menu_item)
        ).filter(
            Order.user_id == current_user.id
        ).order_by(Order.created_at.desc()).all()
        
        print(f"DEBUG: Found {len(orders_list)} orders in history")
        for order in orders_list:
            print(f"DEBUG: Order {order.id} - Status: {order.status}, Menu: {order.menu_item.name}")
        
        # Получаем фоновое изображение
        from app import get_background_settings
        images = get_background_settings()
        
        return render_template("order_history.html", 
                             orders=orders_list,
                             background_image=images.get('order_history_background_image'),
                               t=lambda key: t(key, current_lang),
                               lang=current_lang)
    
@bp.route("/cancel_order/<int:order_id>")
@login_required
def cancel_order(order_id):
    with Session() as db_session:
        # Находим заказ, принадлежащий текущему пользователю
        order = db_session.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
            Order.status == OrderStatus.PENDING  # Можно отменять только pending заказы
        ).first()
        
        if order:
            # Удаляем заказ из корзины
            db_session.delete(order)
            db_session.commit()
            flash("Замовлення скасовано!", "success")
        else:
            flash("Замовлення не знайдено або не може бути скасоване", "error")
    
    return redirect(url_for("orders.cart"))

@bp.route('/menu')
def show_menu():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'restaurant_db.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu WHERE active = 1")
    menu_items = cursor.fetchall()
    conn.close()
    return render_template('menu.html', menu_items=menu_items)