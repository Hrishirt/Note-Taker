from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


print(app.url_map)
'''
@app.route('/') 
def helloworld():
    notes = ["Study MathAcademy", "Finish basic notes app", "Eat Dinner"]
    return render_template('notes.html', notes=notes)
'''

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Note {self.id}: {self.content[:20]}...>'
    
with app.app_context():
    db.create_all()

@app.route("/hello")
def hello():
    name = request.args.get("name", "Flask")
    return f"Hello, {escape(name)}!"

'''
@app.route('/')
def noteform():
    return render_template('form.html')
'''

notes = [] 


@app.route('/', methods =['POST', 'GET'])
def noteTake():
    if request.method == 'POST':
        note = request.form['text']
        if note:
            notes.append(note)
            db.session.add(Note(content=note))
            db.session.commit()
        return redirect(url_for('noteTake'))
    allNotes = Note.query.all()
    print(allNotes)
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
        notes[i] = edited_note
        return redirect(url_for('noteTake'))
    return render_template('form.html', notes=notes, editing_i=i, editing_text=notes[i])

@app.route('/clear_notes', methods=['POST'], endpoint='clear_notes')
def clear_note():
    notes.clear()
    return render_template('form.html', notes=notes)


print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)