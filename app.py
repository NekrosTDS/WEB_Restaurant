from flask import Flask, render_template
from settings import DatabaseConfig, Session
from flask_login import LoginManager
from models import User
from routes import auth, admin, orders
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config.from_object(DatabaseConfig)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-for-development')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 
app.config['REMEMBER_COOKIE_DURATION'] = 3600 

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

login_manager.session_protection = "strong"
login_manager.remember_cookie_duration = 3600

csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    return user

@login_manager.user_loader
def load_user_from_session(user_id):
    try:
        return User.get(int(user_id))
    except:
        return None


@app.route("/")
def index():
    return render_template("index.html")

app.register_blueprint(auth.bp, url_prefix="/auth")
app.register_blueprint(admin.bp)
app.register_blueprint(orders.bp)

# Обработчики ошибок
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)