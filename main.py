from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

URL="https://api.themoviedb.org/3/search/movie"
URL2="https://api.themoviedb.org/3/movie/"


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = SECRET_KEY


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()

class EditForm(FlaskForm):
    rating = StringField("Your rating out of 10 e.g 7.5")
    review = StringField("Your review")
    submit = SubmitField("Done")

class AddForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add movie")

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for n in all_movies:
        n.ranking=len(all_movies)-all_movies.index(n)

    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = EditForm()
    edit_movie= Movie.query.get(request.args.get('id'))
    if form.validate_on_submit():
        edit_movie.rating=float(form.rating.data)
        edit_movie.review=form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, edit_movie=edit_movie)

@app.route("/delete")
def delete():
    deleted_movie = Movie.query.get(request.args.get('id'))
    db.session.delete(deleted_movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["POST", "GET"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        print(form.title.data)
        parameters = {
        "api_key": API,
        "language": "en-US",
        "query": form.title.data
        }
        response = requests.get(url=URL, params=parameters)
        options = response.json()["results"]
        return render_template("select.html", options=options)
    return render_template("add.html", form=form)

@app.route("/select")
def select():
    parameters = {
        "api_key": API,
    }
    URL=f"{URL2}{request.args.get('id')}"
    response = requests.get(url=URL, params=parameters)
    results = response.json()
    new_movie = Movie(title=results["original_title"], year=results["release_date"], description=results["overview"], img_url=f"https://image.tmdb.org/t/p/w500/{results['poster_path']}")
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit", id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
