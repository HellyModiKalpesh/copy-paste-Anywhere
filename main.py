
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt
from Table import File,User
Base = declarative_base()
engine = create_engine("mysql://root:#sqlpassword@localhost:3306/collegeproject")
Session = sessionmaker(bind=engine)
session = Session()

from flask import Flask, jsonify, request, make_response, send_from_directory,send_file
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, decode_token
import jwt
import os
import string
import random
import smtplib
import ssl
from email.mime.text import MIMEText

from flask import Flask, request, send_file

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret-key'


def generate(username):
    payload = {"username": username}
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
    return token


@app.route('/signup',methods=['POST'])
@cross_origin()
def signup():
    username=request.json.get('username')
    password=request.json.get('password')
    emailid=request.json.get('emailid')
    user=User(username=username,password=password,emailid=emailid)
    session.add(user)
    session.commit()
    return jsonify({'message':'User created successfully'}),200

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    emailid = request.json.get('emailid')
    password = request.json.get('password')
    user = session.query(User).filter_by(emailid=emailid).first()
    if user is None:
        return jsonify({'message':'invalid user'}),401
    if user.password == password:
        token = generate(user.username)
        response_object = {
            'status': 'True',
            'token': token
        }
        return response_object
    else:
        return jsonify({'message': 'invalid'}), 401

@app.route('/upload',methods=['POST'])
@cross_origin()
def uploadfile():
    token=request.headers.get('Authorization')
    print(token)
    if token:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        username = payload.get('username')
        print(username)
        user = session.query(User).filter_by(username=username).first()
        if user:
            file = request.files.get('file')
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                book = File(filename=filename, token=token)
                session.add(book)
                session.commit()
                send_email(user.emailid,user.username,file.filename,token)

                response_object = {
                    'status': 'success',
                    'message': 'Successfully Added.',
                    'token': token,
                    'filename': filename
                }
                return response_object
            else:
                return jsonify({'error': 'No file was uploaded'}), 400
        else:
            return jsonify({'error':'not a valid user'})
    else:
        return jsonify(({'error':'missing or invalid token'}))



@app.route('/download', methods=['POST'])
@cross_origin()
def download():
    token = request.headers.get('Authorization')
    print(token)
    if token:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        username = payload.get('username')
        print(username)
        user = session.query(User).filter_by(username=username).first()
        if user:
            filename=request.json.get('filename')
            token = request.json.get('token')
            print(token)
            file = session.query(File).filter_by(token=token).first()
            if file:
                path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                print(path)
                return send_file(path,  as_attachment=True)
            else:
                return 'File not found', 404
        else:
            return jsonify({'error':'not a valid user'})
    else:
        return jsonify(({'error':'missing or invalid token'}))


def send_email(email, username,filename, token):
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "Your Email address"
    password = "your app password"
    message = f"""\
    Subject: Token for File Upload

    Dear {username},

    Your file has been uploaded successfully. 
    Here is your token: {token}
    file name is {filename}

    Regards,
    Helly"""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message)

@app.route('/logout', methods=['POST'])
@cross_origin()
def logout():
    token = request.headers.get('Authorization')
    print(token)
    if token:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        username = payload.get('username')
        print(username)
        user = session.query(User).filter_by(username=username).first()
        if user:
            response_object = {
                'status': 200,
                'message':'log out successful'
            }
            return response_object

        else:
            return jsonify({"message": "invalid token"})

    else:
        return jsonify({"message": "token missing"})



if __name__ == '__main__':
    app.run(host='192.168.1.147', port=5000, debug=True)
