from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from settings import Session
from models import Menu, Order, OrderStatus
import sqlite3
import os

bp = Blueprint('orders', __name__)

@bp.route("/menu")
def menu():
    with Session() as session:
        menu_items = session.query(Menu).filter(Menu.active == True).all()
        return render_template("menu.html", menu_items=menu_items)

@bp.route("/add_to_cart/<int:item_id>", methods=["POST"])
@login_required
def add_to_cart(item_id):
    quantity = int(request.form.get("quantity", 1))
    
    with Session() as session:
        menu_item = session.query(Menu).filter(Menu.id == item_id).first()
        
        if not menu_item:
            flash("Страву не знайдено", "error")
            return redirect(url_for("orders.menu"))
        
        # Создаем новый заказ
        new_order = Order(
            user_id=current_user.id,
            menu_id=item_id,
            quantity=quantity,
            total_price=menu_item.price * quantity
        )
        
        session.add(new_order)
        session.commit()
        
        flash(f"'{menu_item.name}' додано до замовлення!", "success")
        return redirect(url_for("orders.menu"))

@bp.route("/cart")
@login_required
def cart():
    with Session() as session:
        cart_items = session.query(Order).filter(
            Order.user_id == current_user.id,
            Order.status == OrderStatus.PENDING
        ).all()
        
        total = sum(item.total_price for item in cart_items)
        return render_template("cart.html", cart_items=cart_items, total=total)

@bp.route("/update_cart/<int:order_id>", methods=["POST"])
@login_required
def update_cart(order_id):
    quantity = int(request.form.get("quantity", 1))
    
    with Session() as session:
        order = session.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).first()
        
        if order and quantity > 0:
            order.quantity = quantity
            order.total_price = order.menu_item.price * quantity
            session.commit()
            flash("Кількість оновлено!", "success")
        elif order and quantity == 0:
            session.delete(order)
            session.commit()
            flash("Страву видалено з кошика!", "success")
        
        return redirect(url_for("orders.cart"))

@bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    with Session() as session:
        # Подтверждаем все pending заказы пользователя
        pending_orders = session.query(Order).filter(
            Order.user_id == current_user.id,
            Order.status == OrderStatus.PENDING
        ).all()
        
        for order in pending_orders:
            order.status = OrderStatus.CONFIRMED
        
        session.commit()
        
        flash("Замовлення оформлено! Очікуйте підтвердження.", "success")
        return redirect(url_for("orders.menu"))

@bp.route("/order_history")
@login_required
def order_history():
    with Session() as session:
        orders = session.query(Order).filter(
            Order.user_id == current_user.id
        ).order_by(Order.created_at.desc()).all()
        
        return render_template("order_history.html", orders=orders)

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
