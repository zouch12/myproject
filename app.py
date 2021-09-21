import os

from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session
from flask_mail import Mail, Message
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from functools import wraps

import re

db = sqlite3.connect("football.db")

# create table for applicants info
db.execute("""CREATE TABLE IF NOT EXISTS 'application' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'first' TEXT NOT NULL, 
            'last' TEXT NOT NULL, 'middle' TEXT,  
            'DOB' TEXT NOT NULL, 'Community' TEXT NOT NULL, 'height' NUMERIC, 'weight' NUMERIC, 'position' TEXT NOT NULL,
            'team' TEXT NOT NULL, 'email' TEXT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'contact' TEXT)""")

db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS 'username' ON 'application'('username')""")

# create table for registered playes info
db.execute("""CREATE TABLE IF NOT EXISTS 'registered' ('id' INTEGER NOT NULL UNIQUE, 'first' TEXT NOT NULL, 
            'last' TEXT NOT NULL, 'middle' TEXT,  
            'DOB' TEXT NOT NULL, 'Community' TEXT NOT NULL, 'height' NUMERIC, 'weight' NUMERIC, 'position' TEXT NOT NULL,
            'team' TEXT NOT NULL, 'email' TEXT NOT NULL, 'username' TEXT NOT NULL UNIQUE, 'hash' TEXT NOT NULL, 'contact' TEXT)""")

# create table for coach info
db.execute("""CREATE TABLE IF NOT EXISTS 'Coach' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL,
            'hash' TEXT NOT NULL, 'team' TEXT NOT NULL)""")
db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS 'username' ON 'Coach'('username')""")

# create table for players asking to be released from club
db.execute("""CREATE TABLE IF NOT EXISTS 'release' ('id' INTEGER NOT NULL UNIQUE, 'first' TEXT NOT NULL, 'last' TEXT NOT NULL, 
            'position' TEXT NOT NULL, 'team' TEXT NOT NULL, 'email' TEXT NOT NULL UNIQUE, 'username' TEXT NOT NULL UNIQUE)""")

# Create table for trophies won by clubs
db.execute("""CREATE TABLE IF NOT EXISTS 'Trophies' ('team' TEXT NOT NULL, 'Trophy' TEXT NOT NULL, 'Tournament' TEXT NOT NULL,
            'Year' TEXT NOT NULL)""")

# db.execute("DELETE FROM registered WHERE username = 'that'")
# db.commit()


app = Flask(__name__)

# configure mail system
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config["MAIL_USERNAME"] = os.environ.get('MAIL_USERNAME')
app.config["MAIL_PASSWORD"] = os.environ.get('MAIL_PASSWORD')
app.config["MAIL_PORT"] = 587 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True

mail = Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# requiring login function
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

# index or homepage
@app.route('/')
def index():
    return render_template("layout.html")

# register
@app.route("/register", methods=['GET', 'POST'])
def register():
    
    Team = ['18+', 'Whitehouse', 'Calor', 'DCYO', 'UnderRock', 'Hilltop Ballers']
    com = ['Dennery North', 'Dennery South', 'Micoud North', 'Micoud South']
    pos = ['Goal Keeper', 'Right Fullback', 'Left Fullback', 'Centerback/Sweeper', 
            'Holding Midfielder', 'Right Midfielder', 'Left Milfielder', 'Center Midfielder', 
            'Attacking Midfielder', 'Striker/Center Forward']

    # regular expression confirmation
    # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s01.html
    pattern = re.compile(r"\A[\w!#$%&'*+/=?`{|}~^-]+(?:\.[\w!#$%&'*+/=?`{|}~^-]+)*@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,6}\Z")
    dob = re.compile(r"(19|20)\d\d[- \/.](0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])")

    # regular expression for password
    pat = re.compile(r"\A[A-Za-z]+[\w]+[\d]{8,}\Z")

    if request.method == "GET":
        return render_template("registration.html", Team=Team, com=com, pos=pos)
    
    else:
        with sqlite3.connect('football.db') as con:
            con.row_factory = dict_factory
            db = con.cursor()

            first = request.form.get('firstname')
            middle = request.form.get('middlename')
            last = request.form.get('lastname')
            DOB = request.form.get('DOB')
            height = request.form.get('height')
            weight = request.form.get('weight')
            team = request.form.get('team')
            community = request.form.get('community')
            position = request.form.get('position')
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            confirm = request.form.get('confirm')
            contact = request.form.get('contact')

            if not first:
                flash("enter first name")
                return redirect("/register")
            if not last:
                flash("enter last name")
                return redirect("/register")
            if not middle:
                middle = None 
            if not DOB or not dob.search(DOB):
                flash("enter date of birth/ DOB.")
                return redirect("/register")
            if not height:
                height = None
            if not weight:
                weight = None
            if not team or team not in Team:
                flash("enter valid team")
                return redirect("/register")
            if not community or community not in com:
                flash("enter valid community")
                return redirect("/register")
            if not position or position not in pos:
                flash("enter valid position")
                return redirect("/register")
            if not email or not pattern.search(email):
                flash("enter valid email address")
                return redirect("/register")
            if not username:
                flash("enter username")
                return redirect("/register")
            if not password or password != confirm or re.fullmatch(pat, password):
                flash("password or password confirmation is wrong or doesnt exist")
                return redirect("/register")
            if not contact:
                contact = None

            # checking if username or email of application already exist in applications pending
            db.execute("""SELECT username, email FROM application WHERE username = (?) OR email = (?)""", (username, email,))
            applicant = db.fetchall()

            # checking if username or email already exist for player
            db.execute("""SELECT username , email FROM registered WHERE username = (?) OR email = (?)""", (username, email,))
            reg = db.fetchall()

            if applicant:
                flash("username and/or email already exist for applicant!")
                return redirect("/register")
            elif reg:
                flash("username and/or email already exist for active player!")
                return redirect("/register")
            else:
                hashed = generate_password_hash(password)

                db.execute("""INSERT INTO application (first, last, middle, DOB, height, weight, team, Community, position,
                            email, username, hash, contact) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", (first, last, middle, DOB,
                            height, weight, team, community, position, email, username, hashed, contact))
                con.commit()

                message = Message(subject="Application for football team", body="you have applied for " + team + ", and awaiting confirmation.",
                                    recipients=[email])
                mail.send(message)
                flash("you have applied for team and will be receiving an email")
                return redirect("/")


# layout route        
@app.route("/layout.html")
def home():
    return redirect("/")

# 18+ team
@app.route("/about18")
def about18():
    return render_template("18/about18.html")

@app.route("/trophies18")
def trophies18():
    team = "18+"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        db.execute("""SELECT Trophy, Tournament, Year FROM Trophies WHERE team = (?)""", (team,))
        Trophies = db.fetchall()

        if not Trophies:
            return render_template("trophy.html", team=team)
        else:
            return render_template("trophy.html", Trophies=Trophies, team=team)

@app.route("/fball18")
def fball18():
    team = "18+"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()
        
        db.execute("""SELECT first, last, DOB, position, Community FROM registered WHERE team = (?)""", (team,))
        TeamPlayers = db.fetchall()

    if TeamPlayers:
        return render_template("team.html", TeamPlayers=TeamPlayers, team=team)
    else:
        return render_template("team.html", team=team)

# whitehouse team
@app.route("/aboutWhite")
def aboutWhite():
    return render_template("Whitehouse/aboutWhite.html")

@app.route("/trophiesWhite")
def trophiesWhite():
    team = "Whitehouse"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        db.execute("""SELECT Trophy, Tournament, Year FROM Trophies WHERE team = (?)""", (team,))
        Trophies = db.fetchall()

        if not Trophies:
            return render_template("trophy.html", team=team)
        else:
            return render_template("trophy.html", Trophies=Trophies, team=team)

@app.route("/fballWhite")
def fballWhite():
    team = "Whitehouse"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()
        
        db.execute("""SELECT first, last, DOB, position, Community FROM registered WHERE team = (?)""", (team,))
        TeamPlayers = db.fetchall()

    if TeamPlayers:
        return render_template("team.html", TeamPlayers=TeamPlayers, team=team)
    else:
        return render_template("team.html", team=team)

# DCYO team
@app.route("/aboutDcyo")
def aboutDcyo():
    return render_template("DCYO/aboutDcyo.html")

@app.route("/trophiesDcyo")
def trophiesDcyo():
    team = "DCYO"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        db.execute("""SELECT Trophy, Tournament, Year FROM Trophies WHERE team = (?)""", (team,))
        Trophies = db.fetchall()

        if not Trophies:
            return render_template("trophy.html", team=team)
        else:
            return render_template("trophy.html", Trophies=Trophies, team=team)

@app.route("/fballDcyo")
def fballDcyo():
    team = "DCYO"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()
        
        db.execute("""SELECT first, last, DOB, position, Community FROM registered WHERE team = (?)""", (team,))
        TeamPlayers = db.fetchall()

    if TeamPlayers:
        return render_template("team.html", TeamPlayers=TeamPlayers, team=team)
    else:
        return render_template("team.html", team=team)

# UnderRock team
@app.route("/aboutUnder")
def aboutUnder():
    return render_template("UnderRock/aboutUnder.html")

@app.route("/trophiesUnder")
def trophiesUnder():
    team = "UnderRock"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        db.execute("""SELECT Trophy, Tournament, Year FROM Trophies WHERE team = (?)""", (team,))
        Trophies = db.fetchall()

        if not Trophies:
            return render_template("trophy.html", team=team)
        else:
            return render_template("trophy.html", Trophies=Trophies, team=team)

@app.route("/fballUnder")
def fballUnder():
    team = "UnderRock"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()
        
        db.execute("""SELECT first, last, DOB, position, Community FROM registered WHERE team = (?)""", (team,))
        TeamPlayers = db.fetchall()

    if TeamPlayers:
        return render_template("team.html", TeamPlayers=TeamPlayers, team=team)
    else:
        return render_template("team.html", team=team)

# Hilltop Ballers
@app.route("/aboutHilltop")
def aboutHilltop():
    return render_template("Hilltop/aboutHilltop.html")

@app.route("/trophiesHilltop")
def trophiesHilltop():
    team = "Hilltop Ballers"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        db.execute("""SELECT Trophy, Tournament, Year FROM Trophies WHERE team = (?)""", (team,))
        Trophies = db.fetchall()

        if not Trophies:
            return render_template("trophy.html", team=team)
        else:
            return render_template("trophy.html", Trophies=Trophies, team=team)

@app.route("/fballHilltop")
def fballHilltop():
    team = "Hilltop Ballers"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()
        
        db.execute("""SELECT first, last, DOB, position, Community FROM registered WHERE team = (?)""", (team,))
        TeamPlayers = db.fetchall()

    if TeamPlayers:
        return render_template("team.html", TeamPlayers=TeamPlayers, team=team)
    else:
        return render_template("team.html", team=team)

# Calor
@app.route("/aboutCalor")
def aboutCalor():
    return render_template("Calor/aboutCalor.html")

@app.route("/trophiesCalor")
def trophiesCalor():
    team = "Calor"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        db.execute("""SELECT Trophy, Tournament, Year FROM Trophies WHERE team = (?)""", (team,))
        Trophies = db.fetchall()

        if not Trophies:
            return render_template("trophy.html",team=team)
        else:
            return render_template("trophy.html", Trophies=Trophies, team=team)

@app.route("/fballCalor")
def fballCalor():
    team = "Calor"
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()
        
        db.execute("""SELECT first, last, DOB, position, Community FROM registered WHERE team = (?)""", (team,))
        TeamPlayers = db.fetchall()

    if TeamPlayers:
        return render_template("team.html", TeamPlayers=TeamPlayers, team=team)
    else:
        return render_template("team.html", team=team)

# Tournament
@app.route("/tournament")
def tournament():
    return render_template("tournament.html")

# Contact
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/trophy", methods=["GET", "POST"])
@login_required
def TROPHY():
    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        db.execute("""SELECT team, username FROM Coach WHERE id = (?)""", (session["coach"],))
        Team = db.fetchall()

        db.execute("""SELECT Trophy, Tournament, Year FROM Trophies WHERE team = (?)""", (Team[0]["team"],))
        Trophies = db.fetchall()

        if request.method == "GET":
            if not Trophies:
                return render_template("trophy.html", team=Team[0]["username"])
            else:
                return render_template("trophy.html", Trophies=Trophies, team=Team[0]["username"])
        else:
            checkyear = re.compile(r"(19|20)\d\d") 
            trophy = request.form.get("trophy")
            Tournament = request.form.get("Tournament")
            Year = request.form.get("Year")
            team = Team[0]["team"]

            if not trophy:
                flash("enter trophy.")
                return redirect("/trophy")
            if not Tournament:
                flash("enter tournament.")
                return redirect("/trophy")
            if not Year or Year.isnumeric() == False or not checkyear.search(Year):
                flash("enter valid year.")

            db.execute("""INSERT INTO Trophies (team, Trophy, Tournament, Year) VALUES(?, ?, ?, ?)""", 
                        (team, trophy, Tournament, Year,))
            con.commit()

            flash("entry added to Trophies table.")
            return redirect("/trophy")


# release pages
@app.route("/release", methods=["GET", "POST"])
@login_required
def release():

    heads = ["first", "last", "position", "team", "email", "username"]

    with sqlite3.connect('football.db') as con:
        con.row_factory = dict_factory
        db = con.cursor()

        if request.method == "GET":
            if not session["coach"]:
                return render_template("release.html")
            else:
                # selecting info from registered players from coach team 
                db.execute("""SELECT first, last, position, team, email, username FROM registered WHERE team = (SELECT team FROM Coach WHERE id = (?)) """, 
                            (session["coach"],))
                data = db.fetchall()

                # selecting info of players who ask for release from coach team
                db.execute("""SELECT first, last, position, team, email, username FROM release WHERE team = (SELECT team FROM Coach WHERE id = (?)) """, 
                (session["coach"],))
                releas = db.fetchall()

                return render_template("release.html", heads=heads, data=data, releas=releas)

        else:
            db.execute("""SELECT email, username, team FROM release WHERE id = (?)""", (session["user_id"],))
            USERS = db.fetchall()

            # player asking to be released
            if request.form.get("release"):
                # db.execute("""SELECT email, username, team FROM release WHERE id = (?)""", (session["user_id"],))
                # USERS = db.fetchall()

                # player has not asked for release insert them into the release table so coaches could see request
                if not USERS:
                    db.execute("""INSERT INTO release SELECT id, first, last, position, team, email, username FROM registered WHERE id = (?) """, 
                                (session["user_id"],))
                    con.commit()

                    db.execute("""SELECT email FROM registered WHERE id = (?)""", (session["user_id"],))
                    users = db.fetchall()
                    
                    message = Message(subject="Application for release", body="you have applied for release from team, and is awaiting confirmation.",
                                    recipients=[users[0]["email"]])
                    mail.send(message)

                    flash("you have applied for your release from the club")
                    return redirect("/release")
                
                else:
                    flash("you have already applied for your release from the club. Wait patiently for your coach's response.")
                    return redirect("/release")

                # user cancelled application for release    
            elif request.form.get("cancel"):
                message = Message(subject="Cancel application release", body="you have cancelled application for release from team.",
                                recipients=[USERS[0]["email"]])
                mail.send(message)

                db.execute("""DELETE FROM release WHERE id = (?)""", (session["user_id"],))
                con.commit()

                flash("you have cancelled your application for release from club.")
                return redirect("/release")

            # only coaches
            else:
                releaseApp = request.form.getlist("releaseApp")   # info from players who applied for release
                releaseCur = request.form.getlist("releaseCur")   # info from current list of all players registered

                if request.form.get("rel"):
                    # player is released as requested
                    if releaseApp:
                        for user in releaseApp:
                            # getting player team and email
                            db.execute("""SELECT email FROM release WHERE username = (?)""", (user,))
                            player = db.fetchall()

                            # email to player
                            message = Message(subject="Application for release", body="your release have been granted from team. Well wishes from us.",
                                    recipients=[player[0]["email"]])
                            mail.send(message)

                            db.execute("""DELETE FROM release WHERE username = (?)""", (user,))
                            db.execute("""DELETE FROM registered WHERE username = (?)""", (user,))
                            con.commit()

                        return redirect("/release")

                    # coach decides to release player although they didnt apply         
                    elif releaseCur:
                        for User in releaseCur:
                            # getting player team and email
                            db.execute("""SELECT email FROM registered WHERE username = (?)""", (user,))
                            Player = db.fetchall()

                            # email to player
                            message = Message(subject="Urgent information to you!", body="You have been released from team. Well wishes from us.",
                                    recipients=[Player[0]["email"]])
                            mail.send(message)

                            db.execute("""DELETE FROM registered WHERE username = (?)""", (User,))
                            con.commit()
                            return redirect("/release")
                    else:
                        flash("select player to release from current team.")
                        return redirect("/release")
                
                # coach decides not to grant release though requested
                elif request.form.get("deny"):
                    if releaseApp:
                        for USER in releaseApp:
                            # getting player team and email
                            db.execute("""SELECT email FROM release WHERE username = (?)""", (USER,))
                            PLAYER = db.fetchall()

                            message = Message(subject="Urgent information to you!", body="You application for release from team has been denied. Contact coach for more details.",
                                    recipients=[PLAYER[0]["email"]])
                            mail.send(message)

                            db.execute("""DELETE FROM release WHERE username = (?)""", (USER,))
                            con.commit()
                            return redirect("/release")
                    else:
                        flash("select player to deny release.")
                        return redirect("/release")


# request page for coach making decision
@app.route("/requestt", methods=["GET", "POST"])
@login_required
def requestt():
    headingss = ['first', 'last', 'middle', 'DOB', 'Community', 'height', 'weight', 'position', 'team',
                'email', 'username', 'contact']

    #access database
    with sqlite3.connect('football.db') as con: 
        con.row_factory = dict_factory
        db = con.cursor()

        # query team for current logged in coach
        db.execute("""SELECT team FROM Coach WHERE id = (?)""", (session["user_id"],))
        team = db.fetchall()

        # query applications for team of current coach
        db.execute("""SELECT * FROM application WHERE team = (?)""", (team[0]["team"],))
        info = db.fetchall()

        # shows applicants pending 
        if request.method == "GET":
            return render_template("requestt.html", headingss=headingss, info=info)

        else:
            # selection of applicants approved for by coach and now can log in
            if request.form.get("confirm"):
                regist = request.form.getlist("regist")

                for user in regist:
                    db.execute("""INSERT INTO registered SELECT * FROM application WHERE username = (?) """, (user,))
                    con.commit()

                    db.execute("""SELECT email FROM application WHERE username = (?)""", (user,))
                    applicant = db.fetchall()

                    # email confirmation to player
                    message = Message(subject="Urgent information to you!", body="You application to join team is approved. Contact coach for more details.",
                                    recipients=[applicant[0]["email"]])
                    mail.send(message)

                    db.execute("""DELETE FROM application WHERE username = (?)""", (user,))
                    con.commit()

                return redirect("/requestt")

            # applicants rejected by coach
            if request.form.get("delete"):
                regist = request.form.getlist("regist")

                for user in regist:
                    db.execute("""SELECT email FROM application WHERE username = (?)""", (user,))
                    Applicant = db.fetchall()

                    # email confirmation to player
                    message = Message(subject="Urgent information to you!", body="You application to join team is approved. Contact coach for more details.",
                                    recipients=[Applicant[0]["email"]])
                    mail.send(message)

                    db.execute("""DELETE FROM application WHERE username = (?)""", (user,))
                    con.commit()
                return redirect("/requestt")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    else:
        """Log user in"""

        # Forget any user_id
        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("enter username")
            return redirect("/login")

        # Ensure password was submitted
        if not password:
            flash("enter password")
            return redirect("/login")

        # Query database for username
        with sqlite3.connect('football.db') as con:

            con.row_factory = dict_factory
            db = con.cursor()

            db.execute("""SELECT * FROM registered WHERE username = (?)""", (username,))
            player = db.fetchall()

            db.execute("""SELECT * FROM Coach WHERE username = (?)""", (username,))
            coach = db.fetchall()

        # Ensure username exists and password is correct and whether it is a coach or player
        if len(player) == 1 and check_password_hash(player[0]["hash"], password):
            session["user_id"] = player[0]["id"]
            session["coach"] = None
            flash("Welcome " + player[0]['first'] + ", You are logged in")
            return redirect("/")

        elif len(coach) == 1 and check_password_hash(coach[0]["hash"], password):
            session["user_id"] = coach[0]["id"]
            session["coach"] = coach[0]["id"]
            flash("Welcome " + coach[0]['username'] + ", You are logged in!")
            return redirect("/")

        else:
            flash("incorrect username and/or password")
            return redirect("/login")


# Logout
@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash("logged out")
    # Redirect user to login form
    return redirect("/")




if __name__ == '__main__':
    app.run(debug=True)