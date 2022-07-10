# Import of all the library used in this project
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
import requests, random, string
from flask_mail import Mail, Message

# Configure app
app = Flask(__name__)

# Configuration Of Auto Reload Of All The Templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connection With SQLITE Database
db = SQL("sqlite:///login.db")

# Requires that "Less secure app access" be on
# https://support.google.com/accounts/answer/6010255
app.config["MAIL_DEFAULT_SENDER"] = "cs50.anime@gmail.com"
app.config["MAIL_PASSWORD"] = "ftbipcwfbwlwhmoo"
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "cs50.anime"
mail = Mail(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# This route this the main entry point of this web application where user enter it's credentials
@app.route("/", methods=["GET", "POST"])
def login():
    """Log user in"""
    # This try and except block check if any session found
    # If session is found then user is simply redirected to homepage of ANIME web application
    try:
        if session["email"] or session["user_id"]:
            return redirect("/index")
    except:
        pass
    # Getting user input from login.html page
    email = request.form.get("email")
    password = request.form.get("password")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure required fields are submitted
        if email == "" and password == "":
            return render_template("login.html", message="Please Provide All Required Details")

        # Ensure username was submitted
        if not email:
            return render_template("login.html", message="Please Provide Email")

        # Ensure password was submitted
        if not password:
            return render_template("login.html", message="Please enter a password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return render_template("login.html", message="Incorrect email or password!")

        # Remember which user and other detail of user has logged in
        session["user_id"] = rows[0]["id"]
        session["fname"] = rows[0]["fname"]
        session["lname"] = rows[0]["lname"]
        session["email"] = rows[0]["email"]
        session["pass"] = password

        # Redirect user to home page and executes the query
        db.execute("INSERT INTO time (user_id) VALUES (?)", session["user_id"])
        return redirect("/index")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
         return render_template("login.html")


# This route will delete the session if any found
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id if found
    try:
        session.clear()
        del session["user_id"]
        del session["fname"]
        del session["lname"]
        del session["email"]
        del session["pass"]
    except:
        pass
    # Redirect user to login form
    return redirect("/")

# This route will show an html page (hug.html) with dynamic content fetch from an API
@app.route("/hug")
def hug():
    ''' Hug Page '''
    # Check if user is already logged in
    try:
        if session["user_id"] is None:
            return render_template("login.html", message="Please Login First")
        else:
            hugurl='https://api.waifu.pics/sfw/hug'
            response = requests.get(url=hugurl)
            warning_res = response.json()
            baseurl = warning_res["url"]
            return render_template("hug.html",hugurl=baseurl)
    except:
        pass
    flash("Please Login First")
    return redirect("/")

# This route will show an html page (dance.html) with dynamic content fetch from an API
@app.route("/dance")
def dance():
    ''' Dance Page '''
    # Check if user is already logged in
    try:
        if session["user_id"] is None:
            return render_template("login.html", message="Please Login First")
        else:
            danceurl='https://api.waifu.pics/sfw/dance'
            response = requests.get(url=danceurl)
            warning_res = response.json()
            baseurl = warning_res["url"]
            return render_template("dance.html",danceurl=baseurl)
    except:
        pass
    flash("Please Login First")
    return redirect("/")

# This route will show an html page (quotes.html) with dynamic content fetch from an API
@app.route("/quotes", methods=["POST", "GET"])
def quotes():
    ''' Quotes Page '''
    # Check if user is already logged in
    try:
        if session["user_id"] is None:
            return render_template("login.html", message = "Please Login First")

        # User reached route via POST (as by submitting a form via POST)
        else:
            if request.method=="POST":
                name = request.form.get("name")
                random_choice = random.randint(1, 25)
                searchurl = f'https://animechan.vercel.app/api/quotes/anime?title={name}&page={random_choice}'
                response = requests.get(url=searchurl)
                dataurl = response.json()
                message={}
                try:
                    message["data"] = dataurl["error"]
                    error = message["data"]
                    return render_template("quotes.html", message=error + " Please correct name!")
                except:
                    pass
                try:
                    return render_template("quotes.html", dataurl=dataurl)
                except:
                    pass
            # User reached route via GET method
            else:
                quoteurl = 'https://animechan.vercel.app/api/quotes'
                response = requests.get(url=quoteurl)
                warning_res = response.json()
                return render_template("quotes.html",baseurl=warning_res)
    except:
        pass
    flash("Please Login First")
    return redirect("/")

# This route will show an html page (slap.html) with dynamic content fetch from an API
@app.route("/slap")
def slap():
    ''' Slap Page '''
    # Check if user is already logged in    
    try:
        if session["user_id"] is None:
            return render_template("login.html", message="Please Login First")
        else:
            slapurl='https://api.waifu.pics/sfw/slap'
            response = requests.get(url=slapurl)
            warning_res = response.json()
            baseurl = warning_res["url"]
            return render_template("slap.html",slapurl=baseurl)
    except:
        pass
    flash("Please Login First")
    return redirect("/")

# This route will show the details of the user and last 10 login timestamp
@app.route("/profile")
def profile():
    ''' Profile Page '''
    # Check if user is already logged in
    try:
        if session["user_id"] is None:
            return render_template("login.html", message="Please Login First")
        else:
            values1 = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
            values2 = db.execute("SELECT * FROM time WHERE user_id = ? ORDER BY timimg DESC LIMIT 10", session["user_id"])
            values3 = db.execute("SELECT * FROM time WHERE user_id = ? ORDER BY timimg DESC LIMIT 1", session["user_id"])
            return render_template("profile.html", values1=values1, values2=values2, values3=values3)
    except:
        pass
    flash("Please Login First")
    return redirect("/")

# This route will do the signup process with validation checks
@app.route("/signup", methods=["POST","GET"])
def signup():
    ''' Signup Page '''
    # Check if user is already logged in
    try:
        if session["email"] or session["user_id"]:
            return redirect("/index")
    except:
        pass
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        # User input validation
        if fname == "" and email == "" and email == "" and password == "" and confirm_password == "":
            return render_template("signup.html", message="Please Enter All Required Details")

        elif not fname:
            return render_template("signup.html", message="Please Enter First Name")

        elif not email:
            return render_template("signup.html", message="Please Enter An Email")

        elif not password:
            return render_template("signup.html", message="Please Enter Password")
        
        if len(password) < 8 or len(password) > 12:
            return render_template("signup.html",message="Password must be between 8-12 characters")

        # For password checking and making the password hard to guess
        countupper = countletter = countDigits = countSpec = countWS = 0

        for i in password:

            if i in string.ascii_uppercase or i in string.ascii_lowercase:countletter += 1

            if i in string.ascii_uppercase:countupper += 1

            if i in string.digits:countDigits += 1

            if i in string.punctuation:countSpec += 1

            if i in string.whitespace:countWS += 1


        if not countletter:
            return render_template("signup.html", message="Invalid Password!! No alphabets were found")

        if not countupper:
            return render_template("signup.html", message="Invalid Password!! No uppercase were found")

        if not countDigits:
            return render_template("signup.html", message="Invalid Password!! No digits were found")

        if not countSpec:
            return render_template("signup.html", message="Invalid Password!! No Special Character is found")

        if countWS:
            return render_template("signup.html", message="Invalid Password!! No white space is allowed")

        elif not confirm_password:
            return render_template("signup.html", message="Please Enter Confirm Password")

        elif password != confirm_password:
            return render_template("signup.html", message="Password Must Match")
        session["send_email"] = email
        session["send_pass"] = password
        # Password hash generating process
        hash = generate_password_hash(password)
        rows = db.execute("SELECT * FROM users ")
        user_already_email = []
        for row in rows:
            user_already_email.append(row["email"])
        if email in user_already_email:
            return render_template("signup.html",message=f'The email "{email}" is already registered kindly use another email')
        # Try to insert values in the database
        try:
            mess = """ Hurray! You are now registered with us."""
            # bodi = """ Now you can login and have fun.\nFeel free to use the website for entertaintment purpose.\nHope you will enjoy and get touched with us :)"""
            message = Message(mess, recipients=[email])
            message.html = render_template("greeting.html")
            message.body = message.html
            mail.send(message) 
        except:
            pass
        try:
            db.execute("INSERT INTO users (fname, lname, hash, email) VALUES (?, ?, ?, ?)", fname, lname, hash, email)
            flash("Signup Success")
            return redirect("/")
            # return render_template("login.html", message = "Signup Success")
        except:
            pass

    else:
        return render_template("signup.html")


# This route will display any random anime details with the help of an API call
@app.route("/details")
def detail():
    ''' Anime Detail Page '''
    # Check if user is already logged in
    try:
        if session["user_id"] is None:
            return render_template("login.html", message="Please Login First")
        else:
            random_choice = random.randint(1, 10000)
            computer_url = 'https://api.jikan.moe/v4/anime/{}/'.format(random_choice)
            response = requests.get(computer_url)
            values = response.json()
            incoming={}
            incoming["value"] = values
            try:
                url = incoming["value"]["data"]["url"]
                jpg_url = incoming["value"]["data"]["images"]["jpg"]["image_url"]
                title_eng = incoming["value"]["data"]["title_english"]
                title = incoming["value"]["data"]["title"] 
                title_jap = incoming["value"]["data"]["title_japanese"] +" , "
                anime_type = incoming["value"]["data"]["type"]
                anime_status = incoming["value"]["data"]["status"]
                date_aired = incoming["value"]["data"]["aired"]["string"]
                studio = incoming["value"]["data"]["studios"][0::]
                genre = incoming["value"]["data"]["genres"][0::]  
                studios = ""
                genres = ""
                for stu in studio:studios += stu["name"] + " "
                for gen in genre: genres += gen["name"] + ", "
                scores = incoming["value"]["data"]["score"]
                rating = incoming["value"]["data"]["rating"]
                duration = incoming["value"]["data"]["duration"]
                title_syn = incoming["value"]["data"]["title_synonyms"]
                title_synonyms=""
                for syn in title_syn: title_synonyms += syn + ", "
                rank = incoming["value"]["data"]["rank"]
                description = incoming["value"]["data"]["synopsis"]

                return render_template("details.html", url=url, jpg_url=jpg_url, title_eng=title_eng, title_jap=title_jap,
                                    anime_type=anime_type, anime_status=anime_status, date_aired=date_aired,
                                    studios=studios, genres=genres, scores=scores, rating=rating, title_synonyms=title_synonyms,
                                    rank=rank, description=description, title=title, duration=duration)
            except:
                pass
            try:
                mess = incoming["value"]["message"]
                return render_template("details.html",message=mess + " Please refresh browser")                  
            except:
                pass
            return render_template("details.html")
    except:
        pass
    flash("Please Login First")
    return redirect("/")

# This route will show the homepage of the web application after user logged in
@app.route("/index")
def home():
    ''' Anime Home Page'''
    # Check if user is already logged in
    try:
        if session["user_id"] is None:
            return render_template("login.html", message="Please Login First")
        else:

            try:
                ''' Random anime working here '''
                trending_anime = f'https://kitsu.io/api/edge/anime?page[offset]={random.randint(1, 17000)}'
                trending_anime_response = requests.get(trending_anime)            
                trending_anime_json = trending_anime_response.json()
                incoming_trend_anime={}
                incoming_trend_anime["values"] = trending_anime_json
                trending_anime_title = []
                trending_anime_yturl = []
                trending_anime_jpgurl = []
                trending_anime_type = []
                trending_anime_views = []
                trending_anime_episode = []
                trending_anime_agerating = []
                trending_anime_url = []
                for value in incoming_trend_anime["values"]["data"]:trending_anime_title.append(value["attributes"]["canonicalTitle"])
                for value in incoming_trend_anime["values"]["data"]:trending_anime_yturl.append(value["attributes"]["youtubeVideoId"])
                for value in incoming_trend_anime["values"]["data"]:trending_anime_jpgurl.append(value["attributes"]["posterImage"]["original"])
                for value in incoming_trend_anime["values"]["data"]:trending_anime_type.append(value["attributes"]["showType"])
                for value in incoming_trend_anime["values"]["data"]:trending_anime_views.append(value["attributes"]["userCount"])
                for value in incoming_trend_anime["values"]["data"]:trending_anime_episode.append(value["attributes"]["episodeCount"])
                for value in incoming_trend_anime["values"]["data"]:trending_anime_agerating.append(value["attributes"]["ageRating"])
                for value in incoming_trend_anime["values"]["data"]:trending_anime_url.append(value["links"]["self"])

                anime_converted_title = [str(i) for i in trending_anime_title[0:6]]
                anime_converted_yturl = [str(i) for i in trending_anime_yturl[0:6]]
                anime_converted_jpgurl = [str(i) for i in trending_anime_jpgurl[0:6]]
                anime_converted_type = [str(i) for i in trending_anime_type[0:6]]
                anime_converted_view = [str(i) for i in trending_anime_views[0:6]]
                anime_converted_episode = [str(i) for i in trending_anime_episode[0:6]]
                anime_converted_agerating = [str(i) for i in trending_anime_agerating[0:6]]
                anime_converted_url = [str(i) for i in trending_anime_url[0:6]]


                ''' Random manga working here '''
                trending_manga = f'https://kitsu.io/api/edge/manga?page[offset]={random.randint(1, 17000)}'
                trending_manga_response = requests.get(trending_manga)            
                trending_manga_json = trending_manga_response.json()
                incoming_trend_manga={}
                incoming_trend_manga["values"] = trending_manga_json
                trending_manga_title = []
                trending_manga_jpgurl = []
                trending_manga_type = []
                trending_manga_views = []
                trending_manga_avg_rating = []
                trending_manga_age_rating = []
                trending_manga_link = []
                for value in incoming_trend_manga["values"]["data"]:trending_manga_title.append(value["attributes"]["canonicalTitle"])
                for value in incoming_trend_manga["values"]["data"]:trending_manga_jpgurl.append(value["attributes"]["posterImage"]["original"])
                for value in incoming_trend_manga["values"]["data"]:trending_manga_type.append(value["attributes"]["ageRatingGuide"])
                for value in incoming_trend_manga["values"]["data"]:trending_manga_views.append(value["attributes"]["userCount"])
                for value in incoming_trend_manga["values"]["data"]:trending_manga_avg_rating.append(value["attributes"]["averageRating"])
                for value in incoming_trend_manga["values"]["data"]:trending_manga_age_rating.append(value["attributes"]["ageRating"])
                for value in incoming_trend_manga["values"]["data"]:trending_manga_link.append(value["links"]["self"])

                manga_converted_title = [str(i) for i in trending_manga_title[0:6]]
                manga_converted_jpgurl = [str(i) for i in trending_manga_jpgurl[0:6]]
                manga_converted_type = [str(i) for i in trending_manga_type[0:6]]
                manga_converted_view = [str(i) for i in trending_manga_views[0:6]]
                manga_converted_avgrating = [str(i) for i in trending_manga_avg_rating[0:6]]
                manga_converted_agerating = [str(i) for i in trending_manga_age_rating[0:6]]
                manga_converted_link = [str(i) for i in trending_manga_link[0:6]]

                return render_template("index.html", anime_converted_title=anime_converted_title,
                                        anime_converted_yturl=anime_converted_yturl, anime_converted_url=anime_converted_url,
                                        anime_converted_jpgurl=anime_converted_jpgurl, anime_converted_type=anime_converted_type, 
                                        anime_converted_agerating=anime_converted_agerating, anime_converted_view=anime_converted_view, 
                                        anime_converted_episode=anime_converted_episode, manga_converted_title=manga_converted_title, 
                                        manga_converted_jpgurl=manga_converted_jpgurl, manga_converted_type=manga_converted_type, 
                                        manga_converted_view=manga_converted_view, manga_converted_avgrating=manga_converted_avgrating,
                                        manga_converted_agerating=manga_converted_agerating, manga_converted_link=manga_converted_link)
            except:
                pass
            return render_template("index.html")
    except:
        pass
    flash("Please Login First")
    return redirect("/")

# This route will update details of the user via an POST method 
@app.route("/update", methods=["POST","GET"])
def update():
    ''' Update Profile Page '''
    # Check if user is already logged in
    try:
        if session["user_id"] is None:
            render_template("login.html", message="Please Login First")
        else:
            # Executes if request is POST
            if request.method=="POST":
                fname = request.form.get("fname")
                lname = request.form.get("lname")
                email = request.form.get("email")
                
                # Validation of the input
                if fname == "" and email == "":
                    return render_template("update.html", message="Please Provide Necessary Details")
                if fname == "":
                    return render_template("update.html", message="Please Provide First Name")
                if email == "":
                    return render_template("update.html", message="Please Provide Email")
                db.execute("UPDATE users SET fname = ?,lname = ?,email = ?  WHERE  id = ?", 
                            fname, lname, email, session["user_id"])
                mess = "Your Email Was Changed!"
                messi = Message(mess, recipients=[email])
                session["updated_email"] = email
                messi.html = render_template("updateprofile.html")
                messi.body = messi.html
                mail.send(messi) 
                flash("Profile Updated Successfully")
                return redirect('/profile')
            # Executes if the request is GET
            else:
                rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
                first_name = rows[0]["fname"]
                last_name = rows[0]["lname"]
                user_email = rows[0]["email"]
                return render_template("update.html", message="Be Sure To Enter Correct Details ", note =  "You Will Get An Email Even If You Don't Change Email" ,
                                        first_name=first_name, last_name=last_name, user_email=user_email)
    except:
        pass
    flash("Please Login First")
    return redirect("/")


# Handlig the error code 404 with a customize html page
@app.errorhandler(404)
def page_not_found(e):
    ''' Customize page for error code 404 '''
    return render_template("404.html")


# Handlig the error code 500 with a customize html page
@app.errorhandler(500)
def page_not_found(e):
    ''' Customize page for error code 500 '''
    return render_template("500.html")


# Handling the error code 503 with a customize page
@app.errorhandler(503)
def page_not_found(e):
    ''' Customize page for error code 503 '''
    return render_template("503.html")

# For auto reload of the python
if __name__ == "__main__":
    app.run(debug=True)
    app.debug=True
    app.run(use_reloader=True)
