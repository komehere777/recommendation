# 라이브 서버 안쓰고 플라스크 서버 가동
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField  # 폼 데이터를 다루기 위한 모듈
from wtforms.validators import DataRequired  # 폼 규제사항을 정의

app = Flask(__name__)
# 이부분은 config.py로 따로 빼서 관리하는게 좋음
# secret_key 설정, 하나 하나 만들어 보는 재미가...
app.config["SECRET_KEY"] = "adfaasdgasga13gdsg"
# db 설정, sqlite 사용, 다른 db 사용시 붙여넣기 후 수정
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
# db 수정사항 추적 안함
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db 초기화, 연동
db = SQLAlchemy(app)


# db table 생성
# 일련번호, 할일 내용 컬럼 생성
# Task가 테이블명
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(
        db.String(200), nullable=False
    )  # nullable=False: 필수값 널 허용안함


# 일반적으로 form.py로 따로 빼서 관리하는게 좋음
class TaskForm(FlaskForm):
    title = StringField(
        "Title", validators=[DataRequired()]
    )  #'Title' 레이블, 진자2방식에는 필요
    submit = SubmitField("Add Task")


@app.route("/", methods=["GET", "POST"])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(title=form.title.data)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("index.html", form=form)


@app.route("/tasks")  # get 방식으로만 접근 가능
def tasks():
    tasks = Task.query.all()
    return jsonify([{"id": task.id, "title": task.title} for task in tasks])


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        db.session.commit()
        return redirect(
            url_for("index")
        )  # url_for('index') = '/' 이걸로 만들어짐 => def index() 함수실행
    form.title.data = task.title
    return render_template(
        "edit_task.html", form=form, task_id=task_id, task_title=task.title
    )


@app.route("/delete/<int:task_id>")
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
