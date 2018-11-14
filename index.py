from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired
import wtforms

from foot_detector import FootDetector
from game import Game

import webbrowser
import time
import cv2
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DontTellAnyone'
Bootstrap(app)

fd = FootDetector()
g = Game()

class EnterNameForm(Form):
    name = StringField("Name", validators=[InputRequired()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html', game_state=g)

@app.route('/new_game')
def new_game():
    g.restart()
    return redirect('/score')

@app.route('/update_game')
def update_game():
    g.next()
    return redirect('/game')

@app.route('/score')
def score():
    return render_template('score.html', score=0, time_left=30.0)

@app.route('/game_over/<score>', methods=['GET', 'POST'])
def game_over(score):
    form = EnterNameForm()
    if form.validate_on_submit():
        with open('score_history.csv', 'a') as f:
            f.write(form.name.data + "," + str(score))
        return redirect('/highscores')
    return render_template('game_over.html', form=form, score=score)

@app.route('/highscores')
def highscores():
    score_history = csv.reader(open('score_history.csv'), delimiter=',')
    print(score_history)
    sorted_scores = sorted(score_history, key=lambda row:int(row[1]), reverse=True)
    print(sorted_scores)
    return render_template('highscores.html', sorted_scores=sorted_scores)

@app.route('/get_pressed_tiles')
def get_pressed_tiles():
    res = fd.detect()
    res = "".join(map(str, res))
    print(res)
    return jsonify(pressed_tiles=res)

@app.route('/check_game_ongoing')
def check_game_ongoing():
    id = request.args.get('id', '0')
    print("true" if g.ongoing() else "false")
    return jsonify(ongoing="true" if g.ongoing() else "false", id=id)

@app.route('/get_score_data')
def get_score_data():
    if g.start_time is None:
        return jsonify(score=g.score, time_left=30-time.time())
    return jsonify(score=g.score, time_left=30+g.start_time-time.time())

@app.route('/camera')
def camera():
    while True:
        raw_frame, gray_frame, delta_frame, thresh_frame = fd.read()
        if not fd.show_frame(thresh_frame):
            break
        time.sleep(0.05)
    return ""

if __name__ == '__main__':
    app.run(debug=True, threaded=True)