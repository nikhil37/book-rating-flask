import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
data = read_csv('books.csv').loc
for i in range(5000):
	isbn=list(book[i])[0]
	new=float(dict(requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"uu2VTnqd3RT32yCnADtevw","isbns":list(data[i])[0]}).json()["books"][0])['average_rating'])
	db.execute('''update books set goodreads_average_rating = :new where isbn = :isbn;''',{'new':new,'isbn':isbn})
	db.commit()