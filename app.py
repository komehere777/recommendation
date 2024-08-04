from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
import numpy as np
from surprise import SVD, Dataset, Reader, accuracy
from surprise.dataset import DatasetAutoFolds
import logging

logging.getLogger('flask_wtf.csrf').setLevel(logging.DEBUG)

# CSV 파일 경로 설정
ratings_file_path = r"D:\pythonProject\recommendation\ml-latest-small\ratings.csv"
movies_file_path = r"D:\pythonProject\recommendation\ml-latest-small\movies.csv"

# ratings 데이터 로드
ratings = pd.read_csv(ratings_file_path)

# DatasetAutoFolds 클래스를 ratings.csv 파일 기반으로 생성
reader = Reader(line_format="user item rating timestamp", sep=",", rating_scale=(0.5, 5.0))
data_folds = DatasetAutoFolds(
    ratings_file=r"D:\pythonProject\recommendation\ml-latest-small\ratings_noh.csv",
    reader=reader,
)

# 전체 데이터를 학습 데이터로 생성
trainset = data_folds.build_full_trainset()
algo = SVD(n_epochs=20, n_factors=50, random_state=0)
algo.fit(trainset)

# movies 데이터 로드
movies = pd.read_csv(movies_file_path)

def get_unseen_surprise(ratings, movies, userId):
    seen_movies = ratings[ratings["userId"] == int(userId)]["movieId"].tolist()
    total_movies = movies["movieId"].tolist()
    unseen_movies = [movie for movie in total_movies if movie not in seen_movies]
    print(f"평점 매긴 영화수: {len(seen_movies)}, 추천대상 영화수: {len(unseen_movies)}, 전체 영화수: {len(total_movies)}\n")
    return unseen_movies

def recomm_movie_by_surprise(algo, userId, unseen_movies, top_n=10):
    predictions = [algo.predict(str(userId), str(movieId)) for movieId in unseen_movies]

    def sortkey_est(pred):
        return pred.est

    predictions.sort(key=sortkey_est, reverse=True)
    top_predictions = predictions[:top_n]

    top_movie_ids = [int(pred.iid) for pred in top_predictions]
    top_movie_titles = movies[movies.movieId.isin(top_movie_ids)]["title"]
    top_movie_rating = [np.round(pred.est, 3) for pred in top_predictions]

    top_movie_preds = [
        (id, title, rating)
        for id, title, rating in zip(top_movie_ids, top_movie_titles, top_movie_rating)
    ]

    return top_movie_preds

app = Flask(__name__)
app.config["SECRET_KEY"] = "adfaasdgaasdfwsdfsdf23sdfsfdfasa323sga13gdsg"
csrf = CSRFProtect(app)

class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Search")

@app.route("/", methods=["GET", "POST"])
def index():
    form = TaskForm()

    print("Form submitted:", form.is_submitted())
    print("Form validated:", form.validate())
    print("validate_on_submit:", form.validate_on_submit())

    if form.validate_on_submit():
        title = form.title.data
        print("title: ", title)
        seen_movies = ratings[ratings["userId"] == int(title)]["movieId"].tolist()
        print(seen_movies)
        unseen_movies = get_unseen_surprise(ratings, movies, str(title))
        top_movie_preds = recomm_movie_by_surprise(algo, title, unseen_movies, top_n=10)

        # 세션에 데이터 저장
        session['title'] = title
        session['top_movie_preds'] = top_movie_preds

        return redirect(url_for('recommend'))
    else:
        print("Form errors:", form.errors)

    return render_template("index.html", form=form)

@app.route("/recommend")
def recommend():
    title = session.get('title')
    top_movie_preds = session.get('top_movie_preds')

    if not title or not top_movie_preds:
        return redirect(url_for('index'))

    return render_template("recommend.html", title=title, top_movie_preds=top_movie_preds)

if __name__ == "__main__":
    app.run(debug=True)