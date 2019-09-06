# Project 1

Web Programming with Python and JavaScript

This project is a book review website. Users must first register for an account by inputting a username and password, and then login using these credentials. They are then brought to a home page, where they can search for a book using ISBN numbers, titles, and authors. Users can then choose a book from the results page, which brings them to the book's individual page. The book's page has basic details and previous reviews on the left, and on the right there is space where a review can be submitted. A user can only submit one review per book.

The templates folder contains all the html files for this project. application.py is the application that is run by flask. books.csv are the books used in the website. helpers.py includes methods such as apology, which I used instead of error.html. import.py was used to import the list of books from books.csv to my database.

Tables in Database:
users
books
reviews

Columns in Tables
  users:
    id (serial int)
    username (varchar)
    hash (varchar)
  books:
    id (serial int)
    isbn (varchar)
    title (varchar)
    author (varchar)
    year (int)
  reviews:
    id (serial int)
    bookid (int)
    content (varchar)
    rating (int)
    userid (int)

I was given an extension by Brian Yu.
