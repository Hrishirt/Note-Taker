from flask import Flask, render_template, request, redirect, url_for, flash, session
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import bcrypt
import time

load_dotenv()
app = Flask(__name__) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.secret_key = os.getenv('SECRET_KEY')
print(app.url_map)
'''
@app.route('/') 
def helloworld():
    notes = ["Study MathAcademy", "Finish basic notes app", "Eat Dinner"]
    return render_template('notes.html', notes=notes)
'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(300), nullable = False)

    def __repr__(self):
        return f'<user {self.id}: email: {self.email}>'
    
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    def __repr__(self):
        return f'<Note {self.id}: {self.content[:20]}...>'
    
with app.app_context():
    db.create_all()

@app.route("/signup", methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        print("POST request received")
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Email received: {email}")
        print(f"Password before encryption: {password}\nPassword after encryption: {hashed_password}")
        if email:
            emailCheck = User.query.filter_by(email=email).first()
            print(emailCheck)
            if emailCheck:
                flash("User already exists", "error")
            else:
                new_user = User(email=email, password=hashed_password)
                print(f"User created: {new_user}")
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                print("User committed to database")
                flash("Account successfully created", "success")
                return redirect(url_for('noteTake'))
    return render_template('signup.html')


@app.route("/signin", methods = ['POST', "GET"])
def signin(): 
    if request.method == 'POST': 
        email = request.form['email']
        password = request.form['password']
        emailCheck = User.query.filter_by(email=email).first()
        print(emailCheck)
        if emailCheck:
            passwordcheck = bcrypt.check_password_hash(emailCheck.password, password)
            print(f"Password check: {passwordcheck}")
            if passwordcheck:
                flash("Sign in Successful", "success")
                time.sleep(2)
                session['user_id'] = emailCheck.id
                return redirect(url_for('noteTake'))

            else:
                flash("Incorrect password", "error")
        else:
            flash("Incorrect Email or password", "error")

    return render_template('signin.html')

@app.route("/hello")
def hello():
    name = request.args.get("name", "Flask")
    return f"Hello, {escape(name)}!"

'''
@app.route('/')
def noteform():
    return render_template('form.html')
'''
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('signin'))

def loginCheck():
    if 'user_id' not in session:
        flash("Please login to view this page", "error")
        return redirect(url_for('signin'))
    return None

@app.route('/transfer')
def transfer():
    return redirect(url_for('signup'))

@app.route('/guest')
def guest_user():
    session['user_id'] = 100000
    return redirect(url_for('noteTake'))


@app.route('/', methods =['POST', 'GET'])
def noteTake():
    authCheck = loginCheck()
    if authCheck:
        return authCheck
    
    if request.method == 'POST':
        note = request.form['text']
        if note:
            user_id = session['user_id']
            db.session.add(Note(content=note, user_id=user_id))
            db.session.commit()
        return redirect(url_for('noteTake'))
    user_id = session['user_id']
    allNotes = Note.query.filter_by(user_id=user_id).all()

    # print(allNotes)
    return render_template('form.html', notes=allNotes)

@app.route('/delete/<int:i>', methods=['POST'], endpoint="delete_note")
def delete_note(i):
    Note.query.filter_by(id=i).delete()
    db.session.commit()
    return redirect(url_for('noteTake'))

@app.route('/edit/<int:i>', methods=['GET', 'POST'], endpoint="edit_note")
def edit_note(i):
    if request.method == 'POST':
        edited_note = request.form["text"]
        print("Request form worked")
        dbNote = Note.query.get(i)
        dbNote.content = edited_note
        db.session.commit()
        return redirect(url_for('noteTake'))
    user_id = session['user_id']
    allNotes = Note.query.filter_by(user_id=user_id).all()
    noteContent = Note.query.get(i)
    return render_template('form.html',notes=allNotes, editing_i=i, editing_text= noteContent.content)

@app.route('/clear_notes', methods=['POST'], endpoint='clear_notes')
def clear_note():
    db.session.query(Note).delete()
    db.session.commit()
    allNotes = Note.query.all()
    return render_template('form.html', notes=allNotes)


print(app.url_map)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=False)
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)