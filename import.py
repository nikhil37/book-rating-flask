import requests
from pandas import read_csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
db.execute('create table books(isbn varchar(20) primary key,title varchar(100),author varchar(50), year int, rating float, goodreads_average_rating float, total_rating int, rating_count int);')

x_csv=["isbn","title","author","year"]
data = read_csv('books.csv').loc
bookdata=[]
for i in range(5000):
	temp={}
	temp[x_csv[0]]=str(list(data[i])[0])
	temp[x_csv[1]]=str(list(data[i])[1])
	temp[x_csv[2]]=str(list(data[i])[2])
	temp[x_csv[3]]=int(list(data[i])[3])
	temp["rating"]=0

	try:
		temp["goodreads_average_rating"] = float(dict(requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"uu2VTnqd3RT32yCnADtevw","isbns":list(data[i])[0]}).json()["books"][0])['average_rating'])
	except:
		temp["goodreads_average_rating"] = None
	temp["total_rating"]=0
	temp["rating_count"]=0
	bookdata.append(temp)
	#os.system('clear')
	#print(str(i/50)+"%") #progress bar

#print("=====================================================")
#x_csv=['isbn', 'title', 'author', 'year', 'rating' , 'goodreads_average_rating', 'total_rating', 'rating_count', 'review_count']

for i in bookdata:
	#print(i["goodreads_average_rating"])
	db.execute("insert into books(isbn,title,author,year,rating,goodreads_average_rating,total_rating,rating_count) values(:isbn,:title,:author,:year,:rating,:goodreads_average_rating, :total_rating,:rating_count)",i)
#print(len(bookdata))
db.commit()