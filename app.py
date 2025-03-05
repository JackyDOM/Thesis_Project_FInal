# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This is a Flask App that uses SQLite3 to
# execute (C)reate, (R)ead, (U)pdate, (D)elete operations

from flask import Flask
from flask import render_template
from flask import request
import sqlite3

app = Flask(__name__)

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

# Route to form used to add a new student to the database
@app.route("/enternew")
def enternew():
    return render_template("student.html")

# Route to add a new record (INSERT) student data to the database
# Route to add a new record (INSERT) student data to the database
@app.route("/addrec", methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            age = request.form['age']
            gender = request.form['gender']
            email = request.form['email']
            school_name = request.form['school_name']
            addr = request.form['add']
            city = request.form['city']
            zip_code = request.form['zip']

            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO students 
                    (first_name, second_name, age, gender, email, school_name, addr, city, zip) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (first_name, second_name, age, gender, email, school_name, addr, city, zip_code))

                con.commit()
                msg = "Record successfully added to database"
        except Exception as e:
            con.rollback()
            msg = f"Error in the INSERT: {str(e)}"
        finally:
            con.close()
            return render_template('result.html', msg=msg)


# Route to SELECT all data from the database and display in a table      
@app.route('/list')
def list():
    # Connect to the SQLite3 datatabase and 
    # SELECT rowid and all Rows from the students table.
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")

    rows = cur.fetchall()
    con.close()
    # Send the results of the SELECT to the list.html page
    return render_template("list.html",rows=rows)

# Route that will SELECT a specific row in the database then load an Edit form 
@app.route("/edit", methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            id = request.form['id']
            # Connect to the database and SELECT a specific rowid
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM students WHERE rowid = " + id)

            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            # Send the specific record of data to edit.html
            return render_template("edit.html",rows=rows)

# Route used to execute the UPDATE statement on a specific record in the database
# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST', 'GET'])
def editrec():
    if request.method == 'POST':
        try:
            # Get values from the form
            rowid = request.form['rowid']
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            age = request.form['age']
            gender = request.form['gender']
            email = request.form['email']
            school_name = request.form['school_name']
            addr = request.form['add']
            city = request.form['city']
            zip_code = request.form['zip']

            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE students 
                    SET first_name = ?, second_name = ?, age = ?, gender = ?, email = ?, 
                        school_name = ?, addr = ?, city = ?, zip = ?
                    WHERE rowid = ?
                """, (first_name, second_name, age, gender, email, school_name, addr, city, zip_code, rowid))

                con.commit()
                msg = "Record successfully edited in the database"
        except Exception as e:
            con.rollback()
            msg = f"Error in the Edit: {str(e)}"
        finally:
            con.close()
            return render_template('result.html', msg=msg)


# Route used to DELETE a specific record in the database    
@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
             # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['id']
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM students WHERE rowid="+rowid)

                    con.commit()
                    msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)
        
if __name__ == "__main__":
    app.run(debug=True)