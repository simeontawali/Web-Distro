import os
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from loginform import RegisterForm, LoginForm
from reviewform import ReviewForm
from flask import request, session, flash
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user
from hasher import UpdatedHasher
from typing import Optional



scriptdir = os.path.dirname(os.path.abspath(__file__))
dbfile = os.path.join(scriptdir,"database","beans.sqlite3") # adjust 'database' for the path of the database
pepfile = os.path.join(scriptdir,"database", "pepper.bin")

# open and read the contents of the pepper file into your pepper key
# NOTE: you should really generate your own and not use the one from the starter
with open(pepfile, 'rb') as fin:
  pepper_key = fin.read()

# create a new instance of UpdatedHasher using that pepper key
pwd_hasher = UpdatedHasher(pepper_key)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
app.config['SECRET_KEY'] = 'yourmom'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def admin_required(route_function):
    def decorated_function(*args, **kwargs):
        if not current_user or not current_user.isAdmin==1:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('get_home'))
        return route_function(*args, **kwargs)
    return decorated_function


########################################################################################################################################
# Create Database tables
# TODO: Make models for products, users favorites, users
########################################################################################################################################

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode, nullable=False)
    password_hash = db.Column(db.LargeBinary) # hash is a binary attribute
    fname = db.Column(db.Text,nullable = False)
    lname = db.Column(db.Text, nullable = False)
    #favs = db.Column(db.Text)
    isAdmin = db.Column(db.Integer, nullable=False, default=0)
    favorites = db.relationship('Favorites', back_populates='user')
    cart = db.relationship('Cart', backref='user', lazy=True)
    reviews = db.relationship('Review', back_populates='user')


    # make a write-only password property that just updates the stored hash
    @property
    def password(self):
        raise AttributeError("password is a write-only attribute")
    @password.setter
    def password(self, pwd: str) -> None:
        self.password_hash = pwd_hasher.hash(pwd)
    
    # add a verify_password convenience method
    def verify_password(self, pwd: str) -> bool:
        return pwd_hasher.check(pwd, self.password_hash)
    
# Prepare and connect the LoginManager to this app
login_manager = LoginManager()
login_manager.init_app(app)
# function name of the route that has the login form (so it can redirect users)
login_manager.login_view = 'get_login' # type: ignore
# function that takes a user id and
@login_manager.user_loader
def load_user(id: int) -> Optional[User]:
    return User.query.get(int(id))

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.Text,nullable = False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable = False)
    featured = db.Column(db.Integer, nullable = False)
    favorites = db.relationship('Favorites', back_populates='product')
    reviews = db.relationship('Review', back_populates='product')

    def __str__(self):
        return f"Product name={self.name}, id={self.id}"
    def __repr__(self):
        return str(self)    
    
class Review(db.Model):
    __tablename__ = 'Reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

class Favorites(db.Model):
    __tablename__ = 'Favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)
    product = db.relationship('Product', back_populates='favorites')
    user = db.relationship('User', back_populates='favorites')

class Cart(db.Model):
    __tablename__ = 'Carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    

with app.app_context():
    db.drop_all()
    user = User()
    db.create_all() # this is only needed if the database doesn't already exist

    admin = User(email="admin@admin.com",password="password", fname="admin",lname="admin",isAdmin=1)
    basic = User(email="joe@gmail.com", password ="password",fname="Joe",lname="Shmoe",isAdmin=0)
    """
    u1 = User(email="garry@gmail.com", fname='garry',lname='johnson', isAdmin=0)
    u2 = User(email="terry@gmail.com", fname='terry',lname='johnson', isAdmin=0)
    u33 = User(email="phillip@gmail.com", fname='phillip',lname='johnson', isAdmin=0)
    u4 = User(email="jim@gmail.com", fname='jim',lname='johnson', isAdmin=0)
    u5 = User(email="sheryl@gmail.com", fname='sheryl',lname='johnson', isAdmin=1)
    u6 = User(email="jake@gmail.com", fname='jake',lname='johnson', isAdmin=0)
    u7 = User(email="kenneth@gmail.com", fname='kenneth',lname='johnson', isAdmin=1)
    """
    p1 = Product(name="Strong Coffee", stock=50, price=23.5, featured = 0)
    p2 = Product(name="less Strong Coffee", stock=45, price=23.5, featured = 0)
    p3 = Product(name="Medium Coffee", stock=25, price=21.5, featured = 0)
    p4 = Product(name="slighty Weak Coffee", stock=50, price=3.5, featured = 1)
    p5 = Product(name="Iced Sugar Cookie Oatmilk Shaken Espresso", stock=50, price=13.5, featured = 1)
    p6 = Product(name="poop Coffee", stock=50, price=0.0, featured = 1)
    
    db.session.add(admin)
    db.session.add(basic)
    #db.session.add_all((u1,u2,u4,u5,u6,u7,u33))
    db.session.add_all((p1,p2,p3,p4,p5,p6))
    db.session.commit()
    
    
########################################################################################################################################
# Define routes for flask server.
########################################################################################################################################


@app.route("/home", methods=['GET', 'POST'])
@login_required
def get_home():
    if request.method == 'POST':
        return redirect(url_for('get_home'))
    else:
        products = Product.query.all()
        featured = Product.query.filter_by(featured = 1)
        return render_template('home.html',current_user=current_user, products=products, featured=featured)

@app.route("/cart", methods=['GET', 'POST'])
@login_required
def get_cart():
    if request.method == 'POST':
        return redirect(url_for('get_cart'))
    else:
        return render_template('cart.html',current_user=current_user)

@app.get('/register/')
def get_register():
    form = RegisterForm()
    return render_template('register.html', form=form)

@app.post('/register/')
def post_register():
    form = RegisterForm()
    if form.validate():
        # check if there is already a user with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if the email address is free, create a new user and send to login
        if user is None:
            user = User(email=form.email.data, password=form.password.data, fname = form.first_name.data, lname = form.last_name.data) # type:ignore
            db.session.add(user)
            # Create a cart for the user
            cart = Cart(user=user)
            db.session.add(cart)
            db.session.commit()
            return redirect(url_for('get_login'))
        else: # if the user already exists
            # flash a warning message and redirect to get registration form
            flash('There is already an account with that email address')
            return redirect(url_for('get_register'))
    else: # if the form was invalid
        # flash error messages and redirect to get registration form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))


@app.get('/login/')
def get_login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.post('/login/')
def post_login():
    form = LoginForm()
    if form.validate():
        # try to get the user associated with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if this user exists and the password matches
        if user is not None and user.verify_password(form.password.data):
            # log this user in through the login_manager
            login_user(user)
            # redirect the user to the page they wanted or the home page
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('get_home')
            return redirect(next)
        else: # if the user does not exist or the password is incorrect
            # flash an error message and redirect to login form
            flash('Invalid email address or password')
            return redirect(url_for('get_login'))
    else: # if the form was invalid
        # flash error messages and redirect to get login form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_login'))

@app.get('/')
def get_welcome():
    return render_template('welcomeScreen.html', current_user=current_user)

@app.get('/logout/')
@login_required
def get_logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('get_home'))

@app.get('/quiz')
def get_quiz():
    return render_template('tasteQuiz.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def get_admin():
    users = User.query.all()
    if request.method == 'POST':
        return redirect(url_for('get_admin'))
    else:
        return render_template('admin.html', current_user=current_user, users=users)


@app.get('/product')
def get_product():
    products = Product.query.all()
    return render_template('product.html', products=products)

@login_required
@app.get('/product/review')
def get_review():
    form = ReviewForm()
    return render_template('review.html', form=form)
@app.post('/product/review')
def post_review():
    return
