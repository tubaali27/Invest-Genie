<<<<<<< HEAD
from flask import Flask, render_template, session, redirect, url_for
from technical_analysis.routes import technical_bp
from sentiment_analysis.routes import sentiment_bp
from technical_analysis.psx_data_reader import data_reader  # <-- Add this import
from datetime import date, timedelta
from schedular.genie_scheduler import get_all_stocks_from_firebase, get_gainers_losers
from auth import auth_bp  # <-- Add this import
from config.app_config import config
from auth.forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config.from_object(config['development'])  # or 'production' as needed


# Register blueprints
app.register_blueprint(technical_bp, url_prefix='/technical')
app.register_blueprint(sentiment_bp, url_prefix='/sentiment')
app.register_blueprint(auth_bp, url_prefix='/auth')  # <-- Add this line

# Create context processor to make session user available in all templates
@app.context_processor
def inject_user():
    return dict(session=session)

@app.context_processor
def inject_forms():
    return dict(login_form=LoginForm(), register_form=RegisterForm())

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('home'))  # Home will trigger login modal
        return f(*args, **kwargs)
    return decorated_function

# Home route
@app.route('/')
def home():
    # Fetch gainers and losers for the homepage
    stocks_data = get_all_stocks_from_firebase()
    gainers, losers = get_gainers_losers(stocks_data)
    show_disclaimer = False
    # Show disclaimer only if user is logged in and hasn't accepted
    if 'user' in session and session.get('just_logged_in', False):
        show_disclaimer = True
        session['just_logged_in'] = False  # Only show once after login
    return render_template('index.html', gainers=gainers[:3], losers=losers[:3], show_disclaimer=show_disclaimer)

# About Us route
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/market-movers')
@login_required
def market_movers():
    stocks_data = get_all_stocks_from_firebase()
    gainers, losers = get_gainers_losers(stocks_data)
    return render_template(
        'market_movers.html',
        gainers=gainers[:10],   # Top 10 gainers
        losers=losers[:10]      # Top 10 losers
    )

if __name__ == '__main__':
=======
from flask import Flask, render_template, session, redirect, url_for
from technical_analysis.routes import technical_bp
from sentiment_analysis.routes import sentiment_bp
from technical_analysis.psx_data_reader import data_reader  # <-- Add this import
from datetime import date, timedelta
from schedular.genie_scheduler import get_all_stocks_from_firebase, get_gainers_losers
from auth import auth_bp  # <-- Add this import
from config.app_config import config
from auth.forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config.from_object(config['development'])  # or 'production' as needed

# Register blueprints
app.register_blueprint(technical_bp, url_prefix='/technical')
app.register_blueprint(sentiment_bp, url_prefix='/sentiment')
app.register_blueprint(auth_bp, url_prefix='/auth')  # <-- Add this line

# Create context processor to make session user available in all templates
@app.context_processor
def inject_user():
    return dict(session=session)

@app.context_processor
def inject_forms():
    return dict(login_form=LoginForm(), register_form=RegisterForm())

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('home'))  # Home will trigger login modal
        return f(*args, **kwargs)
    return decorated_function

# Home route
@app.route('/')
def home():
    # Fetch gainers and losers for the homepage
    stocks_data = get_all_stocks_from_firebase()
    gainers, losers = get_gainers_losers(stocks_data)
    return render_template('index.html', gainers=gainers[:3], losers=losers[:3])

# About Us route
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/market-movers')
@login_required
def market_movers():
    stocks_data = get_all_stocks_from_firebase()
    gainers, losers = get_gainers_losers(stocks_data)
    return render_template(
        'market_movers.html',
        gainers=gainers[:10],   # Top 10 gainers
        losers=losers[:10]      # Top 10 losers
    )

if __name__ == '__main__':
>>>>>>> bebaccb05e908cf9d30bb1ef34da0b2920fd595b
    app.run(debug=True)