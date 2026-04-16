from flask import render_template, request, redirect, session
from backend.auth import check_user
from backend.docker_service import run_container

def register_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login", methods=["GET","POST"])
    def login():

        if request.method == "POST":

            username = request.form["username"]
            password = request.form["password"]

            user = check_user(username, password)

            if user:
                session["user"] = username
                return redirect("/dashboard")

            return "Invalid Login"

        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():

        if "user" not in session:
            return redirect("/login")

        return render_template("dashboard.html", user=session["user"])

    @app.route("/ai")
    def ai():

        if "user" not in session:
            return redirect("/login")

        return render_template("ai.html")

    @app.route("/devops-ai")
    def devops_ai():

        if "user" not in session:
            return redirect("/login")

        return render_template("devops_ai.html")

    @app.route("/run-container", methods=["GET","POST"])
    def container():

        if "user" not in session:
            return redirect("/login")

        output = ""

        if request.method == "POST":

            name = request.form["name"]
            image = request.form["image"]
            port = request.form["port"]

            output = run_container(name, image, port)

        return render_template("run_container.html", output=output)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")
    