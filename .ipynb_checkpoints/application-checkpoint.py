import os

from flask import Flask, session, request, render_template, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	#['user']=None
	return render_template('index.html')
@app.route("/signup")
def signuppage():
	if "user" in session:
		return render_template('logged_in.html')
	else:
		alert=""
		return render_template('registration.html', alert_message=alert)
@app.route('/login')
def login():
	if "user" in session:
		return render_template('logged_in.html')
	else:
		return render_template('signin.html',success="")
@app.route("/adduser",methods = ['POST'])
def adduser():
	username=request.form['username']
	password=request.form['password']
	repassword=request.form['repassword']
	if len(list(db.execute('''select * from users where username=:username''',{'username':username})))!=0:
		return render_template('registration.html',alert_message="Username already taken.")
	if len(str(username))==0:
		return render_template('registration.html',alert_message="Please fill all the attributes")
	if  len(str(password))==0:
		return render_template('registration.html',alert_message="Please fill all the attributes")
	if  len(str(repassword))==0:
		return render_template('registration.html',alert_message="Please fill all the attributes")
	if password!=repassword:
		return render_template('registration.html',alert_message="Passwords do not match.")
	if len(list(db.execute('''select * from users where username=:username''',{'username':username})))!=0:
		return render_template('registration.html',alert_message="Username already taken.")

	db.execute('''insert into users(username,password) values(:username,:password)''',{'username':username,'password':password})
	db.commit()
	return render_template('index.html',success="Registration successful.")
@app.route("/search",methods = ['POST','GET']) #login
def search():
	if request.method=="POST":
		username=request.form["username"]
		password=request.form["password"]
		if len(list(db.execute('''select * from users where username=:username''',{'username':username})))==0:
			return render_template('signin.html',alert="User doesn't exist.")
		elif len(list(db.execute('''select * from users where username=:username and password=:password''',{'username':username,'password':password})))==0:
			return render_template('signin.html',alert="Wrong password.")
		else:
			db.commit()
			session["user"]=username
			return render_template('index.html')
	else:
		if "user" in session:
			return render_template('search.html')
		else:
			return render_template('logged_in.html')

@app.route("/logout")
def logout():
	session.pop("user",None)
	return render_template("index.html")
@app.route("/result", methods=['POST','GET'])
def result():
	if "user" not in session:
		return render_template('logged_in.html')
	search = request.form["search"]
	search = '%'+search.lower()+'%'
	x=db.execute('''select * from books where (lower(isbn) like :search) or (lower(title) like :search) or (lower(author) like :search);''',{'search':search})
	re=list(x)
	db.commit()
	r=[]
	for i in re:
		r.append(list(i))
	if len(r)==0:
		l=0
	else:
		l=1
	return render_template('results.html',result=r,l=l)
	#return """hello"""
@app.route("/book/<string:sisbn>", methods = ['POST','GET'])
def book(sisbn):
	if "user" not in session:
		return render_template('logged_in.html')
	else:
		x=db.execute('''select * from books where isbn = :sisbn;''',{'sisbn':sisbn})
		y=db.execute('''select * from reviews where userid = :user and isbn = :sbn''',{'user':session["user"],'sbn':sisbn})
		z=db.execute('''select * from reviews where review is not null and isbn = :sbn''',{'user':session["user"],'sbn':sisbn})
		db.commit()
		try:
			ca=list(list(z))
			c=list(list(y)[0])
			rated=1
		except:
			rated=0
		try:
			b=list(list(x)[0])
			return render_template('book.html',book=b,rated=rated, reviews=ca)
		except:
			return '''<h1>Book not in database.</h1>'''
@app.route("/rate", methods = ['POST','GET'])
def rate():
	isbn = request.form["url"].split('/')[-1]
	rating = int(request.form["rating"])
	review = request.form["review"]
	user = session["user"]
	db.execute('''insert into reviews(isbn,userid,rating,review) values(:isbn,:userid,:rating,:review);''',{'isbn':isbn,'userid':user,'rating':rating,'review':review})
	x=db.execute('''select total_rating,rating_count from books where isbn = :isbn;''',{'isbn':isbn})
	r=list(list(x)[0])
	r[0]+=rating
	r[1]+=1
	avg=r[0]/r[1]
	db.execute('''update books set total_rating=:a, rating_count=:b, rating=:c where isbn=:isbn ;''',{'a':r[0],'b':r[1],'c':avg,'isbn':isbn})
	db.commit()
	return redirect('/book/'+isbn)
@app.route("/all")
def all():
	if "user" not in session:
		return render_template('logged_in.html')

	x=db.execute('''select * from books;''')
	db.commit()
	re=list(x)
	db.commit()
	r=[]
	for i in re:
		r.append(list(i))
	return render_template('results.html',result=r)
@app.route("/api/<string:sisbn>")
def api(sisbn):
	x=db.execute('''select * from books where isbn = :sis''',{'sis':sisbn})
	y=list(list(x)[0])
	r={"title":y[1],"author":y[2],"year":y[2],"isbn":y[0],"review_count":y[7],"average_rating":y[4]}
	return r
