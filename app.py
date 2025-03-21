from flask import Flask, render_template, request, send_file
import sqlite3
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
import openpyxl
import os
import random
import uuid
import string
import re

app = Flask(__name__)

# Register the basename filter
from os.path import basename
app.jinja_env.filters['basename'] = basename

# Ensure an 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
                city TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                policy_id TEXT,
                sel TEXT,
                tran_date TEXT,
                time TEXT,
                code TEXT,
                description TEXT,
                loc TEXT
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

            # Validation code (unchanged)
            def has_special_characters(text):
                pattern = r'^[a-zA-Z0-9\s.,-]+$'
                return not bool(re.match(pattern, text))

            fields_to_check = {
                'First Name': first_name,
                'Second Name': second_name,
                'School Name': school_name,
                'Address': addr,
                'City': city
            }
            for field_name, value in fields_to_check.items():
                if has_special_characters(value):
                    msg = f"No special characters allowed in {field_name}"
                    return render_template('result.html', data={"error": msg})

            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return render_template('result.html', data={"error": "Invalid email format"})

            # Insert into database (unchanged)
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO students 
                    (first_name, second_name, age, gender, email, school_name, addr, city) 
                    VALUES (?,?,?,?,?,?,?,?)
                """, (first_name, second_name, age, gender, email, school_name, addr, city))
                policy_id = cur.lastrowid
                policy_id_str = f"POL{policy_id:05d}"

                submission_date = datetime.now().strftime("%d/%m/%Y")
                submission_time = datetime.now().strftime("%H:%M:%S")
                
                def generate_random_sel():
                    return f"{random.randint(10000, 99999):05d}"

                def generate_random_code():
                    return f"B{random.randint(100, 999)}"
                
                transactions = [
                    {
                        "sel": generate_random_sel(),
                        "tran_date": submission_date,
                        "time": submission_time,
                        "code": generate_random_code(),
                        "description": f"Student Registration - {first_name} {second_name}",
                        "loc": "P"
                    },
                    {
                        "sel": generate_random_sel(),
                        "tran_date": submission_date,
                        "time": submission_time,
                        "code": generate_random_code(),
                        "description": f"School Name - {school_name}",
                        "loc": "P"
                    }
                ]
                for tran in transactions:
                    cur.execute("""
                        INSERT INTO transactions (policy_id, sel, tran_date, time, code, description, loc)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (policy_id_str, tran["sel"], tran["tran_date"], tran["time"], tran["code"], tran["description"], tran["loc"]))
                con.commit()

            # Update students.xlsx with only one row per student
            file_path = os.path.join(app.static_folder, 'students.xlsx')
            if not os.path.exists(file_path):
                wb = Workbook()
                ws = wb.active
                ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City', 
                           'SEL', 'Tran Date', 'Time', 'Code', 'Description', 'Loc'])
            else:
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active

            # Write only one row, using the first transaction's data and school_name as description
            tran = transactions[0]  # Use the first transaction
            ws.append([first_name, second_name, age, gender, email, school_name, addr, city,
                       tran["sel"], tran["tran_date"], tran["time"], tran["code"], school_name, tran["loc"]])
            wb.save(file_path)

            detail_data = [
                {
                    "first_name": first_name,
                    "second_name": second_name,
                    "age": age,
                    "gender": gender,
                    "email": email,
                    "school_name": school_name,
                    "addr": addr,
                    "city": city,
                    "sel": transactions[0]["sel"],
                    "tran_date": transactions[0]["tran_date"],
                    "time": transactions[0]["time"],
                    "code": transactions[0]["code"],
                    "description": transactions[0]["description"],
                    "loc": transactions[0]["loc"]
                }
            ]

            data = {
                "policy_id": policy_id_str,
                "first_name": first_name,
                "second_name": second_name,
                "city": city,
                "transactions": transactions,
                "detail_data": detail_data
            }
            return render_template('result.html', data=data)

        except Exception as e:
            if 'con' in locals():
                con.rollback()
            msg = f"Error in the INSERT: {str(e)}"
            return render_template('result.html', data={"error": msg})
        finally:
            if 'con' in locals():
                con.close()

@app.route("/run", methods=['POST'])
def run():
    try:
        rowid = request.form['id']
        with sqlite3.connect("database.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM students WHERE rowid = ?", (rowid,))
            student = cur.fetchone()
            if not student:
                return render_template('result.html', data={"error": "Student not found"})

            policy_id = f"POL{int(rowid):05d}"
            cur.execute("SELECT sel, tran_date, time, code, description, loc FROM transactions WHERE policy_id = ?", (policy_id,))
            transactions = [{"sel": row[0], "tran_date": row[1], "time": row[2], "code": row[3], "description": row[4], "loc": row[5]} for row in cur.fetchall()]
            if not transactions:
                transactions = []

            detail_data = [
                {
                    "first_name": student["first_name"],
                    "second_name": student["second_name"],
                    "age": student["age"],
                    "gender": student["gender"],
                    "email": student["email"],
                    "school_name": student["school_name"],
                    "addr": student["addr"],
                    "city": student["city"],
                    "sel": transactions[0]["sel"],
                    "tran_date": transactions[0]["tran_date"],
                    "time": transactions[0]["time"],
                    "code": transactions[0]["code"],
                    "description": transactions[0]["description"],
                    "loc": transactions[0]["loc"]
                }
            ] if transactions else []

        data = {
            "policy_id": policy_id,
            "first_name": student["first_name"],
            "second_name": student["second_name"],
            "city": student["city"],
            "transactions": transactions,
            "detail_data": detail_data
        }
        return render_template('result.html', data=data)

    except Exception as e:
        return render_template('result.html', data={"error": f"Error in RUN: {str(e)}"})

@app.route('/list')
def list():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")
    rows = cur.fetchall()
    con.close()
    return render_template("list.html", rows=rows)

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

            # Update the database
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE students 
                    SET first_name = ?, second_name = ?, age = ?, gender = ?, email = ?, 
                        school_name = ?, addr = ?, city = ?
                    WHERE rowid = ?
                """, (first_name, second_name, age, gender, email, school_name, addr, city, rowid))
                policy_id = f"POL{int(rowid):05d}"
                # Fetch existing transactions for this student
                cur.execute("SELECT sel, tran_date, time, code, description, loc FROM transactions WHERE policy_id = ?", (policy_id,))
                transactions = [{"sel": row[0], "tran_date": row[1], "time": row[2], "code": row[3], "description": row[4], "loc": row[5]} for row in cur.fetchall()]
                con.commit()

            # Update students.xlsx with only one row per student
            file_path = os.path.join(app.static_folder, 'students.xlsx')
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            # Remove old rows for this student (match by name as a simple approach)
            rows_to_keep = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] != first_name or row[1] != second_name:
                    rows_to_keep.append(row)

            # Rewrite the Excel file
            ws.delete_rows(1, ws.max_row)  # Clear all rows
            ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City', 
                       'SEL', 'Tran Date', 'Time', 'Code', 'Description', 'Loc'])
            for row in rows_to_keep:
                ws.append(row)

            # Add updated student data with one row, using the first transaction
            tran = transactions[0]  # Use the first transaction
            ws.append([first_name, second_name, age, gender, email, school_name, addr, city,
                       tran["sel"], tran["tran_date"], tran["time"], tran["code"], school_name, tran["loc"]])
            wb.save(file_path)

            msg = "Record successfully edited in the database and Excel file"
            data = {"message": msg}

        except Exception as e:
            if 'con' in locals():
                con.rollback()
            msg = f"Error in the Edit: {str(e)}"
            data = {"error": msg}
        finally:
            if 'con' in locals():
                con.close()
            return render_template('result.html', data=data)

@app.route("/delete", methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            policy_id = f"POL{int(rowid):05d}"
            file_path = os.path.join(app.static_folder, 'students.xlsx')

            # Delete from database
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("DELETE FROM students WHERE rowid=?", (rowid,))
                cur.execute("DELETE FROM transactions WHERE policy_id=?", (policy_id,))
                con.commit()

                # Fetch remaining students and their transactions
                cur.execute("SELECT first_name, second_name, age, gender, email, school_name, addr, city, rowid FROM students")
                students = cur.fetchall()

            # Rewrite students.xlsx with one row per student
            wb = Workbook()
            ws = wb.active
            ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City', 
                       'SEL', 'Tran Date', 'Time', 'Code', 'Description', 'Loc'])

            for student in students:
                first_name, second_name, age, gender, email, school_name, addr, city, student_rowid = student
                student_policy_id = f"POL{student_rowid:05d}"
                cur.execute("SELECT sel, tran_date, time, code, description, loc FROM transactions WHERE policy_id = ?", (student_policy_id,))
                transactions = cur.fetchall()
                tran = transactions[0]  # Use the first transaction
                ws.append([first_name, second_name, age, gender, email, school_name, addr, city,
                           tran[0], tran[1], tran[2], tran[3], school_name, tran[5]])  # Use school_name as description

            wb.save(file_path)

            data = {"message": "Record successfully deleted from the database and Excel file"}
        except Exception as e:
            if 'con' in locals():
                con.rollback()
            data = {"error": f"Error in the DELETE: {str(e)}"}
        finally:
            if 'con' in locals():
                con.close()
            return render_template('result.html', data=data)


# when user upload file and click on submit so it go to displayverify.html file
@app.route("/upload", methods=["GET", "POST"], endpoint="upload")
def upload_file():
    if request.method == "POST":
        try:
            # Check if a file is uploaded
            if "file" not in request.files:
                return render_template("upload.html", error="No file uploaded")
            
            file = request.files["file"]
            
            # Check if the file is empty or not an .xlsx file
            if file.filename == "":
                return render_template("upload.html", error="No file selected")
            if not file.filename.lower().endswith(".xlsx"):
                return render_template("upload.html", error="Only .xlsx files are allowed!")
            
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(upload_path)
            
            # Render upload.html with file details
            return render_template("upload.html", filename=file.filename, file_path=upload_path, message="File uploaded successfully!")
        
        except Exception as e:
            return render_template("upload.html", error=f"Error uploading file: {str(e)}")
    
    # For GET request, render the upload form
    return render_template("upload.html")

# @app.route("/delete_uploaded", methods=["POST"])
# def delete_uploaded():
#     try:
#         file_path = request.form.get("file_path")
#         if file_path and os.path.exists(file_path):
#             os.remove(file_path)
#             return render_template("upload.html", message="File deleted successfully")
#         else:
#             return render_template("upload.html", error="File not found")
#     except Exception as e:
#         return render_template("upload.html", error=f"Error deleting file: {str(e)}")

# @app.route("/serve_uploaded_file/<path:file_path>")
# def serve_uploaded_file(file_path):
#     full_path = os.path.join(UPLOAD_FOLDER, file_path)
#     if os.path.exists(full_path):
#         return send_file(full_path, as_attachment=False)  # Opens in browser if supported, or downloads
#     else:
#         return render_template("upload.html", error="File not found")
    

# for verify data when user submit the file xlsx
# @app.route("/verify")
# def verify():
#     return render_template("verifyResult.html")

# for route Result
@app.route("/displayResult")
def displayResult():
    return render_template("displayResult.html")

if __name__ == "__main__":
    app.run(debug=True)