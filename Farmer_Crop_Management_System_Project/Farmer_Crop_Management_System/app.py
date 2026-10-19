from datetime import date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(25))
    location = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    land_area = db.Column(db.Float, default=0)
    soil_type = db.Column(db.String(80))
    sowing_date = db.Column(db.Date)
    expected_harvest_date = db.Column(db.Date)
    status = db.Column(db.String(30), default="Active")

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crop.id"), nullable=False)
    activity_type = db.Column(db.String(80), nullable=False)
    activity_date = db.Column(db.Date, default=date.today)
    description = db.Column(db.String(255))
    crop = db.relationship("Crop")

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crop.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0)
    expense_date = db.Column(db.Date, default=date.today)
    description = db.Column(db.String(255))
    crop = db.relationship("Crop")

class Harvest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crop.id"), nullable=False)
    harvest_date = db.Column(db.Date, default=date.today)
    quantity_kg = db.Column(db.Float, nullable=False, default=0)
    price_per_kg = db.Column(db.Float, nullable=False, default=0)
    crop = db.relationship("Crop")
    @property
    def revenue(self):
        return self.quantity_kg * self.price_per_kg

def require_login(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def owned_crop(crop_id):
    return Crop.query.filter_by(id=crop_id, user_id=session["user_id"]).first_or_404()

def parse_date(value):
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None

@app.context_processor
def globals_for_templates():
    return {"logged_in": "user_id" in session}

@app.route("/")
def home():
    return redirect(url_for("dashboard")) if logged_in() else render_template("home.html")

def logged_in():
    return "user_id" in session

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name, a valid email, and a password of at least 8 characters.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("That email is already registered.", "danger")
        else:
            user = User(name=name, email=email, phone=request.form.get("phone", ""),
                        location=request.form.get("location", ""),
                        password_hash=generate_password_hash(password))
            db.session.add(user); db.session.commit()
            session["user_id"] = user.id
            flash("Welcome! Your account has been created.", "success")
            return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email", "").strip().lower()).first()
        if user and check_password_hash(user.password_hash, request.form.get("password", "")):
            session.clear(); session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@require_login
def dashboard():
    crops = Crop.query.filter_by(user_id=session["user_id"]).all()
    ids = [c.id for c in crops]
    expenses = Expense.query.filter(Expense.crop_id.in_(ids)).all() if ids else []
    harvests = Harvest.query.filter(Harvest.crop_id.in_(ids)).all() if ids else []
    cost = sum(e.amount for e in expenses); revenue = sum(h.revenue for h in harvests)
    user = db.session.get(User, session["user_id"])
    return render_template("dashboard.html", user=user, crops=crops, cost=cost,
        revenue=revenue, profit=revenue-cost,
        active=sum(c.status == "Active" for c in crops))

@app.route("/crops")
@require_login
def crops():
    rows = Crop.query.filter_by(user_id=session["user_id"]).order_by(Crop.id.desc()).all()
    return render_template("crops.html", rows=rows)

@app.route("/crops/add", methods=["GET", "POST"])
@require_login
def crop_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Crop name is required.", "danger")
        else:
            c = Crop(user_id=session["user_id"], name=name,
                land_area=float(request.form.get("land_area") or 0),
                soil_type=request.form.get("soil_type", ""),
                sowing_date=parse_date(request.form.get("sowing_date")),
                expected_harvest_date=parse_date(request.form.get("expected_harvest_date")),
                status=request.form.get("status", "Active"))
            db.session.add(c); db.session.commit()
            flash("Crop saved.", "success"); return redirect(url_for("crops"))
    return render_template("crop_form.html", crop=None)

@app.route("/crops/<int:cid>/edit", methods=["GET", "POST"])
@require_login
def crop_edit(cid):
    c = owned_crop(cid)
    if request.method == "POST":
        c.name = request.form.get("name", "").strip()
        c.land_area = float(request.form.get("land_area") or 0)
        c.soil_type = request.form.get("soil_type", "")
        c.sowing_date = parse_date(request.form.get("sowing_date"))
        c.expected_harvest_date = parse_date(request.form.get("expected_harvest_date"))
        c.status = request.form.get("status", "Active")
        db.session.commit(); flash("Crop updated.", "success")
        return redirect(url_for("crops"))
    return render_template("crop_form.html", crop=c)

@app.route("/crops/<int:cid>/delete", methods=["POST"])
@require_login
def crop_delete(cid):
    c = owned_crop(cid)
    for model in (Activity, Expense, Harvest):
        model.query.filter_by(crop_id=c.id).delete()
    db.session.delete(c); db.session.commit()
    flash("Crop and its related records deleted.", "info")
    return redirect(url_for("crops"))

@app.route("/activities", methods=["GET", "POST"])
@require_login
def activities():
    crops = Crop.query.filter_by(user_id=session["user_id"]).all()
    if request.method == "POST":
        c = owned_crop(int(request.form["crop_id"]))
        db.session.add(Activity(crop_id=c.id, activity_type=request.form["activity_type"],
            activity_date=parse_date(request.form.get("activity_date")) or date.today(),
            description=request.form.get("description", "")))
        db.session.commit(); flash("Activity saved.", "success"); return redirect(url_for("activities"))
    ids = [c.id for c in crops]
    rows = Activity.query.filter(Activity.crop_id.in_(ids)).order_by(Activity.activity_date.desc()).all() if ids else []
    return render_template("activities.html", crops=crops, rows=rows)

@app.route("/expenses", methods=["GET", "POST"])
@require_login
def expenses():
    crops = Crop.query.filter_by(user_id=session["user_id"]).all()
    if request.method == "POST":
        c = owned_crop(int(request.form["crop_id"]))
        amount = float(request.form.get("amount") or 0)
        if amount < 0: flash("Amount cannot be negative.", "danger")
        else:
            db.session.add(Expense(crop_id=c.id, category=request.form["category"], amount=amount,
                expense_date=parse_date(request.form.get("expense_date")) or date.today(),
                description=request.form.get("description", "")))
            db.session.commit(); flash("Expense saved.", "success"); return redirect(url_for("expenses"))
    ids = [c.id for c in crops]
    rows = Expense.query.filter(Expense.crop_id.in_(ids)).order_by(Expense.expense_date.desc()).all() if ids else []
    return render_template("expenses.html", crops=crops, rows=rows)

@app.route("/harvests", methods=["GET", "POST"])
@require_login
def harvests():
    crops = Crop.query.filter_by(user_id=session["user_id"]).all()
    if request.method == "POST":
        c = owned_crop(int(request.form["crop_id"]))
        qty = float(request.form.get("quantity_kg") or 0); price = float(request.form.get("price_per_kg") or 0)
        if qty < 0 or price < 0: flash("Quantity and price cannot be negative.", "danger")
        else:
            db.session.add(Harvest(crop_id=c.id, harvest_date=parse_date(request.form.get("harvest_date")) or date.today(),
                                   quantity_kg=qty, price_per_kg=price))
            c.status = "Harvested"; db.session.commit()
            flash("Harvest saved.", "success"); return redirect(url_for("harvests"))
    ids = [c.id for c in crops]
    rows = Harvest.query.filter(Harvest.crop_id.in_(ids)).order_by(Harvest.harvest_date.desc()).all() if ids else []
    return render_template("harvests.html", crops=crops, rows=rows)

@app.route("/reports")
@require_login
def reports():
    crops = Crop.query.filter_by(user_id=session["user_id"]).all()
    rows = []
    for c in crops:
        cost = sum(e.amount for e in Expense.query.filter_by(crop_id=c.id).all())
        revenue = sum(h.revenue for h in Harvest.query.filter_by(crop_id=c.id).all())
        rows.append({"crop": c, "cost": cost, "revenue": revenue, "profit": revenue-cost})
    return render_template("reports.html", rows=rows)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
