import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATABASE_PATH = 'data\\database.db'

def checkid(idnum):
    if idnum=="":
        idnum = -1

    data = None
    with sqlite3.connect(DATABASE_PATH) as db:
        curs = db.cursor()
        curs.execute("SELECT * FROM People WHERE id=?", (idnum,))
        data = curs.fetchall()

    if data == []:
        return True
    else:
        return False
    

# home page for searching, adding , and deleting
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    data = None

    if request.method == 'POST': # some change or search being made
        if request.form['action'] == "Search": # search

            sql = "SELECT * FROM People WHERE 1=1 "
            args = []
            name = request.form['name']
            if name != "":
                sql += "AND name LIKE ? || '%' "
                args.append(name)
            idnum = request.form['id']
            if idnum != "":
                sql += "AND id=? "
                args.append(idnum)
            points = request.form['points']
            if points != "":
                sql += "AND points=? "
                args.append(points)

            print(sql)
            print(name, idnum, points)

            with sqlite3.connect(DATABASE_PATH) as db:
                curs = db.cursor()
                curs.execute(sql, args)
                data = curs.fetchall()

            return render_template('index.html', data=data)
        
        elif request.form['action'] == "Delete": # delete
            name = request.form['name']
            idnum = request.form['id']
            points = request.form['points']

            with sqlite3.connect(DATABASE_PATH) as db:
                curs = db.cursor()
                curs.execute("DELETE FROM People WHERE name=? AND id=? AND points=?", (name, idnum, points))
                db.commit() # save changes
                curs.execute("SELECT * FROM People")
                data = curs.fetchall()

        elif request.form['action'] == "Update": # update
            name = request.form['name']
            idnum = request.form['id']
            points = request.form['points']

            return redirect(url_for('update', name=name, id=idnum, points=points))
        
        elif request.form['action'] == "Add": # add
            name = request.form['name']
            idnum = request.form['id']
            points = request.form['points']

            with sqlite3.connect(DATABASE_PATH) as db:

                curs = db.cursor()
            
                if name=="" or idnum=="" or points=="" or not checkid(idnum):
                    curs.execute("SELECT * FROM People")
                    data=curs.fetchall()

                    return render_template('index.html', data=data)

                curs.execute("INSERT INTO People (name, id, points) VALUES (?, ?, ?)", (name, idnum, points))
                
                db.commit() # save changes
                curs.execute("SELECT * FROM People")
                data = curs.fetchall()
    
        return render_template("index.html", data=data)


    else:

        with sqlite3.connect(DATABASE_PATH) as db:
            curs = db.cursor()
            curs.execute("SELECT * FROM People")
            data = curs.fetchall()
    
        return render_template('index.html', data=data)
    
# page to update information in the database
@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "GET":

        origname = request.args.get('name', None)
        origidnum = request.args.get('id', None)
        origpoints = request.args.get('points', None)

        if origidnum is None or origname is None or origpoints is None:
            return redirect("index.html", data=[])

        return render_template('update.html', data=(origname, origidnum, origpoints))

    if request.method == "POST":

        origname = request.form['origname']
        origidnum = request.form['origid']
        origpoints = request.form['origpoints']

        name = request.form['name']
        idnum = request.form['id']
        points = request.form['points']

        if not checkid(idnum):
            return redirect(url_for('index'))

        if name=="":
            name = origname
        if idnum=="":
            idnum=origidnum
        if points=="":
            points=origpoints

        with sqlite3.connect(DATABASE_PATH) as db:
            curs = db.cursor()
            curs.execute("UPDATE People SET name=?, id=?, points=? WHERE name=? AND id=? AND points=?", (name, idnum, points, origname, origidnum, origpoints))
            db.commit() # save changes
        
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
