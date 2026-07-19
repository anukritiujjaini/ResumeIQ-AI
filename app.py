from flask import Flask, render_template, request, jsonify,redirect, session
from db import engine, base, sessionlocal   
import models
import PyPDF2
import docx
import json
import ai

app = Flask(__name__,static_folder="static")    # isse ek Flask application object create hota hai, jisse hum apne web application ke liye use karte hain.



base.metadata.create_all(bind=engine)
  
  # ye line database me tables create karne ke liye hai, agar wo pehle se exist nahi karte hain.
@app.route("/")          #yeh ek route decorator hai jo "/" URL path ko home() function ke saath map karta hai. 
                         # Jab user is URL par visit karega, to home() function execute hoga.
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

#-------SignUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    print("signup route hit!")
    db=sessionlocal()
    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            # Check if the user already exists
            existing_user = db.query(models.User).filter_by(email=email).first()
            if existing_user:
                return "User already exists. Please log in."

            # Create a new user
            user = models.User(email=email, password=password)
            db.add(user)
            db.commit()

            return redirect("/login")

        return render_template("signup.html")
    finally:
        db.close()

@app.route("/test")
def test():
    return render_template("login.html")

#-------Login
@app.route("/login", methods=["GET", "POST"])
def login():
    db = sessionlocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if the user exists
        user = db.query(models.User).filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.email
            session['user_id'] = user.id
            return redirect("/dashboard")
        else:
            return "Invalid email or password."

    return render_template("login.html")

#-------Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'user_id' not in session:
        return redirect("/login")
    
    result= None
    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")

        #filehandling
        if file and file.filename!="":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                        resume_text = text
                except Exception as e:
                    result = f"Error reading PDF file: {str(e)}"
       
            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                    resume_text = text
                except Exception as e:
                    result = f"Error reading DOCX file: {str(e)}"    
                
        if resume_text and user_goal:
            # Call the AI model here (this is a placeholder)
            try:
                result = ai.analyse_resume(resume_text,user_goal)

            
                # Save the report to the database
                db = sessionlocal()
                user = db.query(models.User).filter_by(email=session["user"]).first()
                report = models.Reports(
                    user_id = user.id,
                    resume_text = resume_text,
                    result = json.dumps(result)
                )
                db.add(report)
                db.commit()
            except Exception as e:
                result = {"error": f"AI error: {str(e)}"}    
    return render_template(
            "dashboard.html",
            user=session["user"],
            result=result
        )
   
#history
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    db = sessionlocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()

    reports = db.query(models.Reports).filter_by(user_id = user.id).all()

    #convert JSON string  > dic
    pasred_reports = []
    for r in reports:
        try:
            pasred_result= json.loads(r.result)
        except:
            pasred_result={}

        pasred_reports.append({
            "resume": r.resume_text,
            "result":pasred_result
        })   
    db.close()
    return render_template("history.html",reports=pasred_reports)

#--Logout route
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)


