from logging import debug
from warnings import resetwarnings
from flask import Flask, render_template, request, redirect,url_for, flash, session, send_from_directory
import mysql.connector
import json
from json import dumps
import os
import string
import random
from dbconfig import * 




@app.route('/', methods = ["GET","POST"])
def index(): 
    if "logged" in session:
        if session["logged"] != "yes": 
            return redirect("/login/") 
    else: 
        return redirect("/login/")    
    if request.method == "POST": 
        content = request.form["content"]
        insert_task = "INSERT INTO tasks (content, status, uid) VALUES ('%s', %s, %s);"%(content, 0, session["id"])
        mycursor.execute(insert_task)
        mydb.commit()
        print(f"json: {json.dumps(insert_task)}")
        return ("Task added!")
    else: 
        return render_template('index.html')

    
@app.route('/login/', methods=["GET", "POST"])
def login_view():
    if request.method == "POST": 
        username = request.form["username"]
        password = request.form["password"]
        check_user = "SELECT * FROM users WHERE username = '%s' AND password = '%s';" %(username, password)
        mycursor.execute(check_user)
        mydb.commit()
        result = mycursor.fetchall()
        if len(result) == 0: 
            session["logged"] = "no"
            return("Incorrect username or password")
        session["logged"] = "yes"
        session["id"] = result[0][0]
        return redirect('/')
    else:
        flash("Login error")
    return render_template('login.html')

@app.route("/logout/")
def logout(): 
    if "logged" in session:
        if session["logged"] != "yes": 
            return("You are not logged in") 
    else: 
        return("You are not logged in")
    session.pop("logged", default=None)
    session.pop("id", default=None)
    return redirect("/login/")

@app.route('/profile/', methods = ["GET" , "POST"])
def profile():
    
    content_get = "SELECT * FROM tasks WHERE uid = {}".format(session["id"])
    mycursor.execute(content_get)
    mydb.commit()
    result = mycursor.fetchall()
    return render_template("profile.html", data = result)

@app.route('/search/', methods = ["GET" , "POST"])
def search(): 
    if request.method == "POST":

        search_data = request.form["search_data"]
        search_query = "SELECT * FROM tasks WHERE content = '%s' AND uid = %s;" %(search_data,session["id"])
        mycursor.execute(search_query)
        mydb.commit()
        result = mycursor.fetchall()
        return render_template("search.html", data = result)

    return render_template("search.html", search_data = "search_data")


@app.route("/update/<int:id>", methods = ["GET" , "POST"])
def update(id): 
    if request.method == "GET":
        search_query = "SELECT * FROM tasks WHERE id = {}".format(id)
        mycursor.execute(search_query)
        mydb.commit()
        result = mycursor.fetchone()
        return render_template("task.html", task=result)
    content = request.form["content"]
    status = request.form["status"]
    search_query = "UPDATE tasks SET content='{}', status='{}' WHERE id = {}".format(content, status, id)
    mycursor.execute(search_query)
    mydb.commit()
    return redirect("/profile/")

@app.route("/delete/<int:id>")
def delete(id): 
    search_query = "DELETE FROM tasks WHERE  id = {};".format(id) 
    mycursor.execute(search_query)
    mydb.commit()
    return redirect("/profile")

@app.route("/export/")
def export(): 
    mycursor.execute("SELECT content, status FROM tasks WHERE uid = {};".format(session["id"]))
    mydb.commit()
    to_export = mycursor.fetchall()
    export = '{"json":  ' + json.dumps(to_export) + '}'
    jsonFile = open("file.json" , "w")
    jsonFile.write(export)
    jsonFile.close()
    return send_from_directory(os.path.abspath(os.getcwd()), "file.json",os.path, as_attachment = True)


@app.route("/import/", methods = ["GET" , "POST"])
def import_file():
    if 'file' in request.files:
        imported_file = request.files["file"]
        if import_file != "": 
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            imported_file.save(name)
            file = open(name, "r")
            data = json.loads(file.read())
            file.close()
            os.remove(name)
            for xy in data["json"]: 
                insert_task = "INSERT INTO tasks (content, status, uid) VALUES ('%s', %s, %s);"%(xy[0],int(xy[1]), session["id"])
                mycursor.execute(insert_task)
                mydb.commit()
            return "Tasks added successfully"

    return render_template("import.html")

if __name__ == "__main__": 
    app.run(debug = True)