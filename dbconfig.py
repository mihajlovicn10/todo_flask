from logging import debug
from warnings import resetwarnings
from flask import Flask, render_template, request, redirect,url_for, flash, session, send_from_directory
import mysql.connector


app = Flask(__name__)

app.secret_key = "secret1123#"


mydb = mysql.connector.connect( 
    host = "localhost", 
    user = "root", 
    password = "", 
    database = "todo"
)

mycursor = mydb.cursor(buffered=True)