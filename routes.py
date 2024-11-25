from flask import render_template, request, redirect, url_for, flash, session
from models import db, User, Todo
from datetime import datetime

def init_routes(app):
    @app.route("/")
    def index():
        if "user_id" not in session:
            return redirect(url_for("login"))
        todos = Todo.query.filter_by(user_id=session["user_id"]).order_by(Todo.order).all()
        print(Todo.order)
        return render_template("index.html", todos=todos)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if User.query.filter_by(username=username).first():
                flash("Username already exists.")
                return redirect(url_for("signup"))
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully.")
            return redirect(url_for("login"))
        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session["user_id"] = user.id
                return redirect(url_for("index"))
            flash("Invalid username or password.")
        return render_template("login.html")
    
    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        flash("You have been logged out.")
        return redirect(url_for("login"))

    @app.route("/add", methods=["POST"])
    def add():
        if "user_id" not in session:
            return redirect(url_for("login"))
        
        task = request.form["todo"]
        due_date = request.form.get("due_date")
        due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None

        max_order = db.session.query(db.func.max(Todo.order)).scalar() or 0
        new_todo = Todo(task=task, done=False, due_date=due_date, order=max_order + 1, user_id=session["user_id"])
        db.session.add(new_todo)
        db.session.commit()
        
        flash("You have added a new todo!")

        return redirect(url_for("index"))

    @app.route("/edit/<int:id>", methods=["GET", "POST"])
    def edit(id):
        todo = Todo.query.get_or_404(id)
        if request.method == "POST":
            todo.task = request.form["todo"]
            due_date = request.form.get("due_date")
            todo.due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("edit.html", todo=todo)

    @app.route("/check/<int:id>")
    def check(id):
        todo = Todo.query.get_or_404(id)
        todo.done = not todo.done
        db.session.commit()
        return redirect(url_for("index"))

    @app.route("/delete/<int:id>")
    def delete(id):
        todo = Todo.query.get_or_404(id)
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for("index"))
    

    @app.route("/move_up/<int:id>")
    def move_up(id):
        if "user_id" not in session:
            return redirect(url_for("login"))
        todo = Todo.query.get_or_404(id)
        previous_todo = Todo.query.filter(Todo.user_id == session["user_id"], Todo.order < todo.order).order_by(Todo.order.desc()).first()

        if previous_todo:
            todo.order, previous_todo.order = previous_todo.order, todo.order
            db.session.commit()

        return redirect(url_for("index"))


    @app.route("/move_down/<int:id>")
    def move_down(id):
        if "user_id" not in session:
            return redirect(url_for("login"))
        todo = Todo.query.get_or_404(id)
        next_todo = Todo.query.filter(Todo.user_id == session["user_id"], Todo.order > todo.order).order_by(Todo.order).first()

        if next_todo:
            todo.order, next_todo.order = next_todo.order, todo.order
            db.session.commit()

        return redirect(url_for("index"))
