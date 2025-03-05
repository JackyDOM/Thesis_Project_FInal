# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This is a Flask App that uses SQLite3 to
# execute (C)reate, (R)ead, (U)pdate, (D)elete operations

from flask import Flask, render_template, request, send_file
import sqlite3
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
import openpyxl  # Add this line to fix the issue
import os

app = Flask(__name__)

# Initialize the database (create table if it doesn’t exist)
def init_db():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                first_name TEXT,
                second_name TEXT,
                age INTEGER,
                gender TEXT,
                email TEXT,
                school_name TEXT,
                addr TEXT,
                city TEXT,
                zip TEXT
            )
        """)
        con.commit()

# Call this once to set up the database
init_db()

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

# Route to form used to add a new student to the database
@app.route("/enternew")
def enternew():
    return render_template("student.html")

# Route to add a new record (INSERT) student data to the database and export to Excel
@app.route("/addrec", methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            # Get data from the form
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
                print(f"Database: Added {first_name} {second_name}")

            # Create/Open the Excel file (students.xlsx) and add the data
            file_path = os.path.join(app.static_folder, 'students.xlsx')
            print(f"Excel file path: {file_path}")

            if not os.path.exists(file_path):  # If file doesn't exist, create a new one with headers
                wb = Workbook()
                ws = wb.active
                ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City', 'Zip Code'])
                print("Excel: Created new file with headers")
            else:  # If file exists, load it to preserve existing data
                try:
                    wb = openpyxl.load_workbook(file_path)
                    ws = wb.active
                    print(f"Excel: Loaded file with {ws.max_row} rows")
                except Exception as excel_load_error:
                    raise Exception(f"Failed to load Excel file: {str(excel_load_error)}")

            # Append new student record to the Excel sheet
            ws.append([first_name, second_name, age, gender, email, school_name, addr, city, zip_code])
            print(f"Excel: Appended {first_name} {second_name}, total rows now: {ws.max_row}")

            # Save the file
            try:
                wb.save(file_path)
                print("Excel: File saved successfully")
            except Exception as excel_save_error:
                raise Exception(f"Failed to save Excel file: {str(excel_save_error)}")

            msg = "Record successfully added to the database and Excel file"
        except Exception as e:
            if 'con' in locals():
                con.rollback()
            msg = f"Error in the INSERT: {str(e)}"
            print(f"Error: {msg}")
        finally:
            if 'con' in locals():
                con.close()
            return render_template('result.html', msg=msg)

# Route to SELECT all data from the database and display in a table      
@app.route('/list')
def list():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")
    rows = cur.fetchall()
    con.close()
    return render_template("list.html", rows=rows)

# Route that will SELECT a specific row in the database then load an Edit form 
@app.route("/edit", methods=['POST', 'GET'])
def edit():
    if request.method == 'POST':
        try:
            id = request.form['id']
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM students WHERE rowid = ?", (id,))
            rows = cur.fetchall()
        except:
            rows = []
        finally:
            con.close()
            return render_template("edit.html", rows=rows)

# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST', 'GET'])
def editrec():
    if request.method == 'POST':
        try:
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
@app.route("/delete", methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("DELETE FROM students WHERE rowid=?", (rowid,))
                con.commit()
                msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"
        finally:
            con.close()
            return render_template('result.html', msg=msg)

if __name__ == "__main__":
    app.run(debug=True)