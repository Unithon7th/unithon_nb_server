import os
from flask import Flask
from flask_pymongo import PyMongo
from datetime import timedelta
app = Flask(__name__, template_folder=os.path.join(os.pardir, 'templates'), static_url_path='/static',
            static_folder=os.path.join(os.pardir, 'static'))

app.debug = True
app.secret_key = b'\xac\xcd\x0fW0\xe4\xc4\x04\x1b\xa4\x97L\x92\xa8\x85\xe1'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.config['MONGO_HOST'] = 'ec2-13-124-79-245.ap-northeast-2.compute.amazonaws.com'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_DBNAME'] = 'unithon_db'
app.config['MONGO_USERNAME'] = 'unithon_db'
app.config['MONGO_PASSWORD'] = 'qwer1234'
app.config['MONGO_URI'] = 'mongodb://unithon_db:qwer1234@ec2-13-124-79-245.ap-northeast-2.compute.amazonaws.com:27017/unithon_db'
# app.config['UPLOAD_FOLDER'] = '/home/ec2-user/app/chatbrick_admin/src/static'

mongo3 = PyMongo(app)
from .service import *


# location /stylens-tools/ {
#         proxy_pass http://127.0.0.1:8080;
# }

# DB_CHATBRICK_HOST	localhost
# DB_CHATBRICK_USER_NAME	chatbrick
# DB_CHATBRICK_USER_PASSWORD
# DB_CHATBRICK_PORT	27017
# DB_CHATBRICK_NAME	chatbrick