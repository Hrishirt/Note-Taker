from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape

app = Flask(__name__) 
print(app.url_map)
'''
@app.route('/') 
def helloworld():
    notes = ["Study MathAcademy", "Finish basic notes app", "Eat Dinner"]
    return render_template('notes.html', notes=notes)
'''
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
        return redirect(url_for('noteTake'))
    return render_template('form.html', notes=notes)

@app.route('/delete/<int:i>', methods=['POST'], endpoint="delete_note")
def delete_note(i):
    if 0 <= i < len(notes):
        notes.pop(i)
    return redirect(url_for('noteTake'))
   
print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)