from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, desc
from sqlalchemy import text
from geopy.geocoders import Nominatim
import base64
from datetime import datetime, timedelta, time, date
import csv
import io
import random
import requests
import cv2
import numpy as np
from PIL import Image
import json
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fadalytrac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy(app)
