from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector as mariadb
import pandas as pd
import numpy as np
import pickle
import matplotlib.image as mpimg
from PIL import Image
import os

# Variables utiles
config = {
    'user': 'jean',
    'password': 'root',
    'host': 'localhost',
    'database': 'test_user'
}

users = {
    "user": "123",
    "test": "azerty"
}

connected = False

# Instance de Flask
app = Flask(__name__)

# Index
@app.route("/")
def home():
    return render_template("index.html")

# Ex 1
@app.route("/ex1")
def ex1():
    message = "Hello World!"
    return render_template('ex1.html', message=message)

# Ex 2
@app.route("/ex2")
def ex2():
    message = "Hello World!"
    return render_template('ex2.html', message=message)

# Ex 3
@app.route("/ex31")
def ex31():
    return render_template("ex3_1.html")
    
@app.route("/ex32")  
def ex32():
    return render_template("ex3_2.html")

# Ex 4
@app.route("/ex4")
def ex4():
    return render_template("ex4.html")

@app.route('/ex4', methods=['POST'])
def text_box():
    lastname = request.form['lastname']
    firstname = request.form['firstname']
    sex = request.form['sex']
    pseudo = request.form['pseudo']
    ind = ''
    if sex == '1':
        ind = 'Mr'
    else:
        ind = "Mme"
    processed_text = f"Bonjour {ind} {str.capitalize(firstname)} {str.capitalize(lastname)}, votre pseudo est: {pseudo}"
    return render_template("ex4_1.html", message=processed_text)

# Ex 5
@app.route('/ex5')
def ex5():
    return render_template("ex4.html")

@app.route('/ex5/refused')
def refused():
    return render_template("ex5_refused.html")

@app.route('/ex5/accepted')
def accepted():
    return render_template("ex5_accepted.html")

@app.route('/ex5', methods=['POST'])
def post_sql():
    lastname = request.form['lastname']
    firstname = request.form['firstname']
    sex = request.form['sex']
    pseudo = request.form['pseudo']

    # La connection à la base de données
    mariadb_connection = mariadb.connect(**config)
    cursor = mariadb_connection.cursor()

    # Vérification que le pseudo est libre
    # 
    # Je récupère la liste de tous les pseudo
    query = "SELECT pseudo FROM user"
    cursor.execute(query)
    list_pseudo = []

    for registered_pseudo in cursor:   
        list_pseudo.append(registered_pseudo[0])

  
    # Si pseudo dans la base on n'enregistre pas le contenu du formulaire
    if pseudo in list_pseudo:
        print(f"Ce pseudo ({pseudo}) est déjà pris")
        return redirect("/ex5/refused")
    else:
        print(f"Ce pseudo ({pseudo}) n'est pas pris")

        #Enregistrement en bdd
        add_user = ("INSERT INTO user "
                    "(prenom,nom,sexe,pseudo) "
                    "VALUES (%s,%s,%s,%s)")
        data_user = (firstname,lastname,sex,pseudo)
        cursor.execute(add_user,data_user)
        mariadb_connection.commit()

        #Puis message de confirmation
        return redirect("/ex5/accepted")
    
    
    # Fermeture de la connection
    mariadb_connection.close()

# Ex 6
@app.route('/ex6')
def ex6():

    mariadb_connection = mariadb.connect(**config)
    cursor = mariadb_connection.cursor()
    query = "SELECT * FROM user"
    cursor.execute(query)
    list_user = []
    for registered_user in cursor:   
        list_user.append([registered_user[0],registered_user[1],registered_user[3]])
    return render_template("ex6.html", liste = list_user)

# Ex 7
@app.route('/ex7_upload', methods=['GET', 'POST'])
def ex7_upload():
    global connected
    message = ''
    if (connected):
        print("Connected = ",connected)
        if request.method == 'POST':
            print("separateur", request.form.get('sep'))
            if ((request.form.get('sep'))=="2"):
                print('entré poinrt virgule')
                df = pd.read_csv(request.files.get('file'),sep=';')

            elif ((request.form.get('sep'))=="3"):
                print('entré tabulation')
                df = pd.read_csv(request.files.get('file'),sep='\t')
            else:
                print('entré défaut')
                df = pd.read_csv(request.files.get('file'),sep=',')

            if (df.shape[1] == 1):
                print("1 seule colonne")
                message = "Il semble qu'il y ait un problème, au niveau du séparateur csv"
                return render_template('ex7_upload.html', message= message)
            return render_template('ex7_analyse.html', shape=df.shape, data=df)
        return render_template('ex7_upload.html')
    return redirect('/ex7')

@app.route('/ex7', methods=['GET', 'POST'])
def ex7():
    global connected
    if (request.method == 'POST'):
        form_id = request.form.get('identifiant')
        form_pwd = request.form.get('password')
        try:
            if ((users[form_id])==(form_pwd)):
                connected=True
                return redirect('/ex7_upload')
            else:
                return render_template('ex7_index.html',error="Problème d'identification")
        except:
            return render_template('ex7_index.html',error="Problème d'identification")
    return render_template('ex7_index.html')

@app.route('/ex7_disconnected')
def ex7_disconnect():
    global connected
    connected = False
    return render_template('ex7_disconnected.html')

# Ex 8
@app.route('/ex8', methods=['GET', 'POST'])
def ex8():
    if request.method=='POST':
        file = request.files['file']
        file.save(f'static/uploads/{file.filename}')
        filepath = 'static/uploads/'+file.filename
        model = pickle.load(open('model.save', 'rb'))
        img = Image.open(filepath).convert("L")
        img = np.resize(img, (28,28,1))
        im2arr = np.array(img)
        im2arr = im2arr.reshape(1,-1)
        print("shape : ", im2arr.shape)
        y_pred = model.predict(im2arr)
        prediction = y_pred[0]
        print("prediction",prediction)
        return render_template('ex8_predict.html', prediction=prediction, img_path=filepath)
    return render_template('ex8.html')


if __name__ == "__main__":
    app.run(debug=True)