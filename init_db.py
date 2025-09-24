from models import Base, User, Menu, Order, Reservation
from settings import Session
from werkzeug.security import generate_password_hash

def init_db():
    base = Base()
    
    print("=" * 50)
    print("ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ СУШИ-БАРУ")
    print("=" * 50)
    
    choice = input("Видалити всі дані та створити нову базу? (y/n): ").lower()
    
    if choice == 'y':
        print("Видаляємо стару базу даних...")
        base.drop_db()
        print("Створюємо нову базу даних...")
        base.create_db()
        print("Базу даних створено!")
    else:
        print("Просто створюємо таблиці (якщо не існують)...")
        base.create_db()
        print("Базу даних перевірено!")

    session = Session()
    

    existing_admin = session.query(User).filter(User.username == "sushi_admin").first()
    if not existing_admin:

        admin_user = User(
            username="sushi_admin", 
            email="admin@sushi-bar.ua", 
            hash_password=generate_password_hash("SushiAdmin123!"),
            is_admin=True
        )
        session.add(admin_user)
        print(" Адміністратора створено!")
        print("   Логін: sushi_admin")
        print("   Пароль: SushiAdmin123!")
        print("   Email: admin@sushi-bar.ua")
    else:
        print("  Адміністратор вже існує!")

    # Перевіряємо чи тестовий користувач вже існує
    existing_test_user = session.query(User).filter(User.username == "test_user").first()
    if not existing_test_user:
        # Створюємо тестового користувача
        test_user = User(
            username="test_user", 
            email="test@user.ua", 
            hash_password=generate_password_hash("TestUser123!"),
            is_admin=False
        )
        session.add(test_user)
        print(" Тестового користувача створено!")
        print("   Логін: test_user")
        print("   Пароль: TestUser123!")
    else:
        print("  Тестовий користувач вже існує!")


    existing_menu = session.query(Menu).first()
    if not existing_menu:
 
        menu_items = [
            Menu(
                name="Філадельфія класична",
                price=320.00,
                rating=5,
                description="Лосось, вершковий сир, огірок, авокадо, норі",
                image_path="/static/image/philadelphia_roll.jpg",
                category="Роли",
                active=True
            ),
            Menu(
                name="Каліфорнія з вугрем",
                price=280.00,
                rating=4,
                description="Вугор, вершковий сир, авокадо, ікра масаго",
                image_path="/static/image/california_roll.jpg",
                category="Роли",
                active=True
            ),
            Menu(
                name="Сет 'Самурай'",
                price=650.00,
                rating=5,
                description="8 ролів: філадельфія, каліфорнія, з лососем та тунцем",
                image_path="/static/image/classic_sudrl.jpg",
                category="Сети",
                active=True
            ),
            Menu(
                name="Місо суп",
                price=120.00,
                rating=4,
                description="Традиційний японський суп з пастою місо, тофу та водоростями",
                image_path="/static/image/classic_sudrl.jpg",
                category="Супи",
                active=True
            ),
            Menu(
                name="Темпура з креветок",
                price=180.00,
                rating=4,
                description="Креветки в хрусткому тісті темпура з соусом",
                image_path="/static/image/classic_sudrl.jpg",
                category="Гарячі страви",
                active=True
            ),
            Menu(
                name="Запечений рол з лососем",
                price=220.00,
                rating=5,
                description="Лосось, вершковий сир, запечені під соусом унагі",
                image_path="/static/image/classic_sudrl.jpg",
                category="Запечені роли",
                active=True
            ),
            Menu(
                name="Гункани з тунцем",
                price=150.00,
                rating=4,
                description="4 шт., тунець, ікра тобіко, майонез",
                image_path="/static/image/classic_sudrl.jpg",
                category="Гункани",
                active=True
            ),
            Menu(
                name="Спайсі рол з креветкою",
                price=190.00,
                rating=4,
                description="Креветка, огірок, спайсі соус, ікра масаго",
                image_path="/static/image/classic_sudrl.jpg",
                category="Спайсі роли",
                active=True
            ),
            Menu(
                name="Вегетаріанський сет",
                price=380.00,
                rating=4,
                description="Роли з авокадо, огірком, перцем та морквою",
                image_path="/static/image/classic_sudrl.jpg",
                category="Сети",
                active=True
            ),
            Menu(
                name="Чай зелений",
                price=50.00,
                rating=5,
                description="Якісний зелений чай на порцію",
                image_path="/static/image/green_tea.jpg",
                category="Напої",
                active=True
            ),
            Menu(
                name="Мочі",
                price=80.00,
                rating=4,
                description="Солодкі рисові кліцки з різними начинками",
                image_path="/static/image/mochi.jpg",
                category="Десерти",
                active=True
            ),
            Menu(
                name="Сашимі з лосося",
                price=200.00,
                rating=5,
                description="Свіжий лосось, тонко нарізаний",
                image_path="/static/image/sashimi.jpg",
                category="Сашимі",
                active=True
            )
        ]

        for item in menu_items:
            session.add(item)
        print(f"✅ Додано {len(menu_items)} страв меню!")
    else:
        menu_count = session.query(Menu).count()
        print(f"  Меню вже заповнене! Кількість страв: {menu_count}")

    try:
        session.commit()
        print("=" * 50)
        print(" БАЗУ ДАНИХ УСПІШНО ІНІЦІАЛІЗОВАНО!")
        print("=" * 50)
        

        users_count = session.query(User).count()
        menu_count = session.query(Menu).count()
        admins_count = session.query(User).filter(User.is_admin == True).count()
        
        print(f"Користувачів у системі: {users_count}")
        print(f"Адміністраторів: {admins_count}")
        print(f"Страв у меню: {menu_count}")
        print("=" * 50)
        
    except Exception as e:
        session.rollback()
        print(f" Помилка при збереженні даних: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_db()