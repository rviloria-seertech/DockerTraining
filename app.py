from flask import Flask, redirect, url_for, \
				  request, render_template, json
from pymongo import MongoClient
import pymongo
import os
import socket
from bson import ObjectId



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


client = MongoClient('mongodb://backend:5432/dockerdemo')
db = client.blogpostDB

app = Flask(__name__)

@app.route("/")
def landing_page():
    posts = get_all_posts()
    
    return render_template('blog.html', posts=json.loads(posts))


@app.route('/add_post', methods=['POST'])
def add_post():

    new()
    return redirect(url_for('landing_page'))


@app.route('/update_post/<obj_id>', methods=['POST'])
def update_post(obj_id):

    update(obj_id)
    return redirect(url_for('landing_page'))


@app.route('/delete_post/<obj_id>', methods=['POST'])
def delete_post(obj_id):

    delete(obj_id)
    return redirect(url_for('landing_page'))


@app.route('/remove_all')
def remove_all():
    db.blogpostDB.delete_many({})

    return redirect(url_for('landing_page'))




## Services

@app.route("/posts", methods=['GET'])
def get_all_posts():
    posts = get_posts()
    return JSONEncoder().encode(posts)


@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'title': request.form.get('title', ''),
        'post': request.form.get('post', '')
    }
    _res = methodCU(*(item_doc,))
    return JSONEncoder().encode({'_id': str(_res.inserted_id)})


@app.route('/update/<obj_id>', methods=['PATCH'])
def update(obj_id):
    item_doc = {
        'title': request.form.get('title', ''),
        'post': request.form.get('post', '')
    }
    _res = methodCU(
        *({'_id': ObjectId(obj_id)}, {'$set': item_doc}),
        method='update_one'
    )
    return JSONEncoder().encode({'update_count': _res.modified_count})


@app.route('/delete/<obj_id>', methods=['DELETE'])
def delete(obj_id):
    _res = delete_post({'_id': ObjectId(obj_id)})
    return JSONEncoder().encode({'deleted_count': _res.deleted_count})


### Insert function here ###
def methodCU(*args, **kwargs):
    params = list(args)
    method = kwargs.get('method', 'insert_one')

    return getattr(db.blogpostDB, method)(*params)


def delete_post(filter):
    return db.blogpostDB.delete_one(filter)


def get_posts():
    return list(db.blogpostDB.find())


############################



if __name__ == "__main__":

    app.run(host='0.0.0.0', debug=True)
