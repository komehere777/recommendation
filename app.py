from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField  # 폼 데이터를 다루기 위한 모듈
from wtforms.validators import DataRequired  # 폼 규제사항을 정의

app = Flask(__name__)
app.config["SECRET_KEY"] = "adfaasdgasga13gdsg"


class TaskForm(FlaskForm):
    title = StringField(
        "Title", validators=[DataRequired()]
    )  
    submit = SubmitField("Serch")

@app.route("/", methods=["GET", "POST"])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        return redirect(url_for("recommend", title=form.title.data))
    return render_template("index.html", form=form)


@app.route("/recommend")  # get 방식으로만 접근 가능
def recommend():
    return render_template("recommend.html")



if __name__ == "__main__":
    app.run(debug=True)
