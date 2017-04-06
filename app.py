#! /usr/bin/python3

from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import abort
from flask import session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import time
import os
import random
import string

app = Flask(__name__, template_folder='templates', static_url_path='/static')

app.config['MONGODB_URI'] = os.environ['MONGODB_URI']

app.config['MONGODB_DBNAME'] = os.environ['MONGODB_DBNAME']

mongo = PyMongo(app, config_prefix="MONGODB")

year = time.strftime("%Y", time.gmtime())

app.config['SECRET_KEY'] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(50))

@app.route('/')
def index():
	context = {
		"title" : "4M Labs",
		"year" : year
	}
	return render_template('index.html', context=context)

@app.route('/contact')
def contact():
	context = {
		"title" : "Contact",
		"year" : year
	}
	return render_template('contact.html', context=context)

@app.route('/videos')
def videos():

	categories = [category for category in mongo.db.videos_category.find()]
	videos = [category for category in mongo.db.videos.find()]

	context = {
		"title" : "Videos",
		"categories" : categories,
		"videos" : videos,
		"year" : year
	}
	return render_template('videos.html', context=context)

@app.route('/videos/<id_video>/watch/')
def watch_video(id_video=''):

	autoplay = request.args.get("autoplay", "0")

	videos = mongo.db.videos.find({"_id" : ObjectId(id_video)})
	videos_res = [video for video in videos]

	if videos_res.__len__() < 1:
		abort(404)
	else:
		video = videos_res[0]
		url = video['url'].split("v=")[1]
		if "&" in url:
			url = url.split("&")[0]
		video['url'] = "https://www.youtube.com/embed/" + url

		context = {
			"title" : "Watch Video",
			"video_name" : video['name'],
			"video_desc" : video['description'],
			"video_url" : video['url'],
			"video_autoplay" : autoplay,
			"year" : year
		}
		return render_template('watch_video.html', context=context)

@app.route('/about')
def about():
	context = {
		"title" : "About Me",
		"year" : year
	}
	return render_template("about.html", context=context)

@app.route('/projects')
def projects():

	projects = [project for project in mongo.db.projects.find()]

	context = {
		"title" : "Projects",
		"projects" : projects,
		"year" : year

	}
	return render_template("projects.html", context=context)

@app.route('/music')
def music():
	music = [music for music in mongo.db.music.find()]
	context = {
		"title" : "Music",
		"music" : music,
		"year" : year,
	}
	return render_template("music.html", context=context)

@app.route('/cv')
def cv():
	
	context = {
		"title" : "CV",
		"year" : year,
	}
	return render_template("cv.html", context=context)

@app.errorhandler(404)
def page_not_found(e):
	context = {
			"title" : "Not Found",
			"year" : year
		}
	return render_template('404.html', context=context), 404

@app.route("/control", methods=["GET", "POST"])
def login():

	if request.method == "POST":
		username = request.form.get('username')
		password = request.form.get('password')

		admin = [username for username in mongo.db.admin_user.find({"username" : username, "password" : password})]

		if admin:
			admin = admin[0]
			session['username'] = username
			return redirect(url_for('panel'))
		else:
			return redirect('control')

	else:

		if 'username' in session:
			return redirect(url_for("panel"))
		else:
			
			context = {
				"title" : "Login",
				"year" : year,
			}
			return render_template("login.html", context=context)

@app.route("/panel")
def panel():

	if 'username' in session:
		context = {
			"title" : "Panel",
			"year" : year,
		}
		return render_template("panel.html", context=context)

	else:
		return redirect("control")

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop("username")
		return redirect("control")
	else:
		abort(404)

if __name__ == '__main__':
	
	DEBUG = True
	
	if os.environ['CURRENT_ENV'] == "PROD":
		DEBUG = False
	else:
		pass
	app.run(host='0.0.0.0',debug=DEBUG, port=8000)