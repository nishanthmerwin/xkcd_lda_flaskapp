
from datetime import datetime
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.fields.html5 import DecimalRangeField
import json
from scipy.spatial.distance import cdist
from scipy.spatial import distance
import numpy as np

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


def create_vector(comic):
    idxs = [0,2,3,4,7,8]
    return np.asarray([comic['score_map'][idx] for idx in idxs])

def create_query_vector(data):
    order = ['people', 'cables', 'barrels', 'gold', 'politics', 'chess']
    return np.asarray([data[x] for x in order])

def load_comics():
    with open("../data/annotated_comics.json") as fp:
        comics = json.load(fp)
    for comic in comics:
        score_map = {}
        for score in comic['scores']:
            score_map[score['topic']] = score['score']
        if len(score_map) != 10:
            continue
        comic['score_map'] = score_map

    comics = [x for x in comics if 'score_map' in x]
    for comic in comics:
        vector = create_vector(comic)
        comic['vector'] = vector
    return comics

def get_top_n(query, comics, n=5):
    for comic in comics:
        comic['score'] = distance.cityblock(query, comic['vector'])
    comics = sorted(comics, key=lambda x:x['score'])
    for comic in comics:
        comic['score'] = round(comic['score'], 3)
    return comics[:n]



def get_data(form):
    people = float(form['people'])
    cables = float(form['cables'])
    barrels = float(form['barrels'])
    gold = float(form['gold'])
    politics = float(form['politics'])
    chess = float(form['chess'])
    data = dict(people=people, cables=cables, barrels=barrels,
            gold=gold, politics=politics, chess=chess)
    return [dict(key=k,value=v) for k,v in data.items()]

@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html')

def format_query_html(data):
    string = "Query<br>"
    string += "<table><tr>"
    keys = list(data.keys())
    for key in keys:
        string += "<th>{key}</th>"
    string += "</tr><tr>"
    for key in keys:
        string += "<td>{data['key']}</td>"
    string += "</tr></table>"
    return string


@app.route("/query", methods=['POST'])
def results():
    data = get_data(request.form)
    comics = load_comics()
    query_vector = create_query_vector({x['key']:x['value'] for x in data})
    top5 = get_top_n(query_vector, comics, n=5)
    return render_template('result.html', data=data, top5=top5)


if __name__ == "__main__":
    app.run()



