import duffel_api
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, make_response, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helper import book_flights, apology, login_required, required_input, date_validate, email_validate, input_validate
import pandas as pd
from flask_weasyprint import HTML, render_pdf


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///visa.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Set global variable:
order = None
hotel = None
Destination = None
Nationalities = []
Residence = None
Visas = []
Purpose = None
typeID = None
d_countries = ['Israel', 'Schengen', 'USA']
Visa_Type = None
require_list = []
user_id = None
countries = pd.read_csv('/workspaces/22214788/project/data/Countries.csv', header = 0).to_dict('records') #Be careful to identify what is the current working directory



################################################
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



################################################
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("homepage.html")



################################################
@app.route("/inquiry", methods=["GET", "POST"])
def inquiry():
    """
    Returning the applicable visa types based on users' input
    """

    global Destination, Nationalities, Residence, Visas, Purpose, Visa_Type, typeID, require_list, countries, d_countries
    if request.method == "POST":
        ##TODO: Input validation:
        if required_input(['Destination', 'Nationality', 'Residence', 'Visa', 'Purpose']) == 'failed':
            return apology('Input missing', 400)
        if input_validate(['Destination', 'Nationality', 'Residence', 'Visa', 'Purpose']) == 'failed':
            return apology('Input contains forbidden characters (,")', 400)

        #Check visa requirements
        Destination = request.form["Destination"]
        Nationalities = []
        Nationalities.append(request.form["Nationality"])
        Residence = request.form["Residence"]
        Visas = []
        Visas.append(request.form["Visa"])
        Purpose = request.form["Purpose"]


        Visa_Type = db.execute("SELECT * FROM Visa_TYPE WHERE Destination = ? AND Purpose = ?", Destination, Purpose)

        typeID = Visa_Type[0]["Visa_Type_ID"]
        require_list = db.execute("SELECT Requirement_Name FROM Visa_Requirement WHERE Visa_Type_ID = ?"
                                  ,typeID)

        return render_template("requirement.html",
                                Nationalities = Nationalities, Residence = Residence,
                                Visas = Visas, Destination = Destination, Purpose=Purpose,
                                typeID = typeID, Visa_Type = Visa_Type, require_list = require_list)
    else:

        print(countries)

        return render_template("inquiry.html", d_countries = d_countries, countries = countries)



################################################
@app.route("/requirement", methods=["GET", "POST"])
def requirement():
    """
    Returning the requirements for the chosen visa types
    """

    global typeID, Destination, Nationalities, Residence, Visas, Purpose, Visa_Type, require_list,  countries, d_countries
    if request.method == "POST":
        #Check visa requirements
        if request.form.get("visa-type"):
            typeID = int(request.form["visa-type"])
            require_list = db.execute("SELECT Requirement_Name FROM Visa_Requirement WHERE Visa_Type_ID = ?"
                                  ,typeID)

        return render_template("requirement.html",
                                Nationalities = Nationalities, Residence = Residence,
                                Visas = Visas, Destination = Destination, Purpose=Purpose,
                                Visa_Type = Visa_Type, typeID = typeID, require_list = require_list)
    else:
        return render_template("inquiry.html", d_countries = d_countries, countries = countries)



################################################
@app.route("/apply", methods=["POST", "GET"])
def apply():
    """
    Creating application for the chosen visa type
    """

    if request.method == "POST":
        ##TODO: Input validation:
        if required_input(['chosen-type']) == 'failed':
            return apology('Input missing', 400)

        #Get list of requirment for the visa type
        global Visa_Type
        typeID = int(request.form["chosen-type"])
        for type in Visa_Type:
            if type["Visa_Type_ID"] == typeID:
                chosen_visa = type["Visa_Type_Name"]
                break

        require_list = db.execute("SELECT Requirement_Name, Requirement_ID FROM Visa_Requirement WHERE Visa_Type_ID = ?"
                                  ,typeID)
        return render_template("apply.html", require_list = require_list, chosen_visa = chosen_visa)
    else:
        require_list = None
        Visa_Type = db.execute("SELECT * FROM Visa_TYPE")
        return render_template("apply.html", require_list = require_list, Visa_Type=Visa_Type)



################################################
@app.route("/prepare-doc", methods=["POST", "GET"])
def prepare():
    """
    Get user's trip details for flight reservations
    """

    airports = db.execute('SELECT * FROM airports')
    cities = db.execute('SELECT DISTINCT City, Country FROM airports')
    return render_template("prepare-doc.html", airports = airports, cities = cities)




################################################
@app.route("/get-doc", methods=["POST", "GET"])
def get():
    """
    Query Duffle API and return flight reservations based on user's inputted trip details
    Return error handling message if the API fails or there's no flights available to be reserved
    """

    if request.method == "POST":
         ##Input validation:
        if required_input(['flight-from', 'flight-to', 'flight-depart', 'flight-return',
                           'D-O-B', 'title', 'gender', 'first-name', 'last-name']) == 'failed':
            return apology('Input missing', 400)

        if date_validate(['flight-depart', 'flight-return', 'D-O-B']) == 'failed':
            return apology('Invalid date input', 400)

        if input_validate(['flight-from', 'flight-to', 'flight-depart', 'flight-return',
                           'D-O-B', 'title', 'gender', 'first-name', 'last-name']) == 'failed':
            return apology('Input contains forbidden characters (,")', 400)


        #Get the document:
        origin = request.form["flight-from"]
        destination = request.form["flight-to"]
        depart_date = request.form["flight-depart"]
        return_date = request.form["flight-return"]

        born_on = request.form["D-O-B"]
        title = request.form["title"]
        gender = request.form["gender"]
        family_name = request.form["first-name"]
        given_name = request.form["last-name"]
        print(depart_date)

        global order, hotel
        try:
            order = book_flights(origin, destination, depart_date, return_date, born_on, title, gender, family_name, given_name)
            return render_template("get-doc.html",
                                order = order)
        except (duffel_api.http_client.ApiError):
            return render_template("get-doc.html")

    else:
        airports = db.execute('SELECT * FROM airports')
        cities = db.execute('SELECT DISTINCT City, Country FROM airports')
        return render_template("prepare-doc.html", airports = airports, cities = cities)



################################################
@app.route("/register", methods=["POST", "GET"])
def register():
    """
    Allow user to register for an account on the web portal. The account is saved into SQLite DB.
    """

    if request.method == "POST":
         ##TODO: Input validation:
        if required_input(['email', 'password', 'confirmation']) == 'failed':
            return apology('Input missing', 400)
        if email_validate(['email']) == 'failed':
            return apology('Wrong email format', 400)
        if input_validate(['email', 'password', 'confirmation']) == 'failed':
            return apology('Input contains forbidden characters (,")', 400)
        if request.form['password'] != request.form['confirmation']:
            return apology('Password confirmation did not match with password', 400)

         #Insert new user into database
        db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username varchar(50) NOT Null, hash varchar(50) NOT NULL)")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                    request.form["email"], generate_password_hash(request.form["password"]))
        return render_template("login.html")
    else:
        return render_template("register.html")



################################################
@app.route("/login", methods=["POST", "GET"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        ##TODO: Input validation:
        if required_input(['email', 'password']) == 'failed':
            return apology('Input missing', 400)
        if email_validate(['email']) == 'failed':
            return apology('Wrong email format', 400)
        if input_validate(['email', 'password']) == 'failed':
            return apology('Input contains forbidden characters (,")', 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")



################################################
@app.route("/application", methods=["POST", "GET"])
@login_required
def application():
    """
    Return list of applications for the signed-in user
    """

    global user_id
    user_id = int(session["user_id"])
    if request.method == "POST":
        ##TODO: Input validation:
        if required_input(['application']) == 'failed':
            return apology('Input missing', 400)

        # Insert the the application under this user into database
        visa_type = request.form.get("application")
        try:
            db.execute(
                "INSERT INTO applications (ID, User_ID, Visa_Type_Name, Created_Date) VALUES (?, ?, ?, ?)"
                , str(user_id) + '_' + request.form.get("application")
                , user_id, visa_type, datetime.now())

        except ValueError:
            print('Application already exists for this visa type')

    # Redirect user to home page
    global application
    application = db.execute(
        "SELECT * FROM applications A LEFT JOIN Visa_Type T ON T.Visa_Type_Name = A.Visa_Type_Name WHERE User_ID = ?"
        , user_id)

    #Display the application
    for app in application:
        app['require_list'] = db.execute(
                                            "SELECT R.Requirement_Name, R.Requirement_ID "
                                            "FROM Visa_Requirement R "
                                            "LEFT JOIN Visa_Type T ON T.Visa_Type_ID = R.Visa_Type_ID "
                                            "WHERE T.Visa_Type_Name = ?"
                                            , app["Visa_Type_Name"])

        for req in app['require_list']:
            try:
                db.execute(
                        "INSERT INTO Application_Status (ID, Application_ID, Requirement_ID, Acquired) VALUES (?, ?, ?, ?)"
                        , str(app["ID"]) + '_' + str(req["Requirement_ID"])
                        , app["ID"]
                        , req["Requirement_ID"]
                        , 0)
            except ValueError:
                print("Requirement alredy added")

            req['acquired'] = db.execute(
                                          "SELECT Acquired FROM Application_Status WHERE Application_ID = ? AND Requirement_ID = ?"
                                          ,app["ID"]
                                          ,req["Requirement_ID"])


    return render_template("application.html", application = application)



################################################
@app.route("/save-progress", methods=["POST"])
@login_required
def save_progress():
    """
    Change progress of documents preparation for each applications of the signed-in user
    """

    ##Input validation:
    if required_input(['checkedvar']) == 'failed':
            return apology('Input missing', 400)

    #Get user_id
    global user_id
    user_id = int(session["user_id"])

    #Get latest status of requirement for the application
    app_id = request.form['app_id']
    print(app_id)

    #Update Application Status accordingly
    try:
        req_status = request.form.getlist('checkedvar')
        req_list = db.execute("SELECT Requirement_ID FROM Application_Status WHERE Application_ID = ?"
                            ,app_id)

        for i, req in enumerate(req_list):
            if req_status[i] == 'done':
                db.execute("UPDATE Application_Status SET Acquired = 1 WHERE Requirement_ID = ? and Application_ID = ?"
                        ,req['Requirement_ID']
                        ,app_id)
                print('Update acquired status for requirement ', req, ' to 1.')
            else:
                db.execute("UPDATE Application_Status SET Acquired = 0 WHERE Requirement_ID = ? and Application_ID = ?"
                        ,req['Requirement_ID']
                        ,app_id)
                print('Update acquired status for requirement', req, ' to 0.')

    except BaseException as error:
            print(error)

    # Get list of relevant applications
    global application
    application = db.execute(
        "SELECT * FROM applications A LEFT JOIN Visa_Type T ON T.Visa_Type_Name = A.Visa_Type_Name WHERE User_ID = ?"
        , user_id)

    #Display the application
    for app in application:
        app['require_list'] = db.execute(
                                            "SELECT R.Requirement_Name, R.Requirement_ID "
                                            "FROM Visa_Requirement R "
                                            "LEFT JOIN Visa_Type T ON T.Visa_Type_ID = R.Visa_Type_ID "
                                            "WHERE T.Visa_Type_Name = ?"
                                            , app["Visa_Type_Name"])

        for req in app['require_list']:
            req['acquired'] = db.execute(
                                          "SELECT Acquired FROM Application_Status WHERE Application_ID = ? AND Requirement_ID = ?"
                                          ,app["ID"]
                                          ,req["Requirement_ID"])




    return render_template("application.html", application = application)


################################################
#Log user out (source: cs50's week9 template)
@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



################################################
#Output flight itinerary in pdf
@app.route("/get-flight-iti", methods=["POST", "GET"])
@login_required
def get_flight():
    """
    Return pdf format of the flight resevations
    """
    #Put flight information into html:
    global order
    rendered = render_template('flight-itinerary.html'
                                , order = order)

    # Make pdf out of html:
    #Option 1: pdf = pdfkit.from_string(rendered, False)
    #Option 2: https://www.inkit.com/tutorials/pdf-from-html-with-python#:~:text=To%20create%20PDF%20from%20HTML%20using%20Python%2C%20you%20need%20to,is%20automatically%20provided%20for%20Python.
    #Option 3: weasy print

    #Return pdf:
    response = render_pdf(HTML(string = rendered))

    return response




