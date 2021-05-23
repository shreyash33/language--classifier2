from flask import Flask, request, render_template,session,redirect,url_for
import pickle
import string 
import bz2
from flask_sqlalchemy import SQLAlchemy

def preprocess(text):   
    preprocessed_text = text.lower().replace('-', ' ')
    
    translation_table = str.maketrans('\n', ' ', string.punctuation+string.digits)
    
    preprocessed_text = preprocessed_text.translate(translation_table)
        
    return preprocessed_text

app2 = Flask(__name__)
f = bz2.BZ2File('model.pkl','rb')
model = pickle.load(f)
vectorizer = pickle.load(open('vectorizer.pkl','rb'))
app2.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vygpczmfkdvota:15966179b44c2d3c80f34d4002c76738ab965f4b4a51828c0d838aa48efbf134@ec2-3-212-75-25.compute-1.amazonaws.com:5432/d7pvq0c8n13r99'
app2.config['SECRET_KEY'] = "Shreyash"

db = SQLAlchemy(app2)

class User(db.Model):
   __tablename__ = 'User'
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   password = db.Column(db.String(50))

   def __init__(self, name, password):
       self.name = name
       self.password = password
    


@app2.route('/')
@app2.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        name = request.form['name']
        password = request.form['password']
        data = User.query.filter_by(name=name, password=password).first()
        if data:
            session['loggedin'] = True
            session['id'] = data['id']
            session['name'] = data['name']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect name / password !'
    return render_template('login.html', msg = msg)

@app2.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app2.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form :
        name = request.form['name']
        password = request.form['password']
        new_user = User(name = name,password = password)
        if not db.session.query(User).filter(User.name == name).count():
            msg = 'Account already exists !'
        elif not name or not password:
            msg = 'Please fill out the form !'
        else:
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app2.route('/predict',methods=['POST'])
def predict():
    
    text = str(request.form.values)
    text = preprocess(text)
    text = [text]
    text_v = vectorizer.transform(text)
    prediction = model.predict(text_v)
    output = str(prediction)
    return render_template('index.html', prediction_text='The language is :{}'.format(output))

    

if __name__ == "__main__":
    db.create_all()
    db.session.commit()
    app2.run(debug=True)
