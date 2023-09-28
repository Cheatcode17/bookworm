import random,string
import os
from flask import render_template,request,abort,redirect,flash,make_response,session,url_for
#local Imports

from bookapp import app,csrf
from bookapp.models import db,Admin,Book,Category
from bookapp.forms import *

@app.route("/admin/login/", methods=["GET","POST"])
def admin_login():
    if request.method=="GET":
        return render_template('admin/login.html')
    else:
        username = request.form.get("username")
        pwd = request.form.get('pwd')
        check = db.session.query(Admin).filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first()
        if check:
            session['adminuser']=check.admin_id
            session['role']='admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Login',category='danger')
            return redirect(url_for('admin_login'))
        
@app.route("/admin", methods=["GET","POST"])
def admin_page():
    if session.get("adminuser")== None:
        return render_template("/admin/login.html")
    else:
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get("adminuser")== None or session.get("role") != 'admin':
        return redirect(url_for('admin_login'))
    else:
        return render_template("admin/dashboard.html")
    

@app.route("/admin/logout")
def admin_logout():
    if session.get("adminuser") !=None or session.get("role") !=None:
        session.get("adminuser",None)
        session.pop("role",None)
        flash("You have logged out", category='info')
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/books/')
def all_books():
    if session.get('adminuser')==None or session.get('role')!='admin':
        return render_template(url_for('admin_login'))
    else:
        book = db.session.query(Book).all()
        return render_template("admin/allbooks.html",book=book)

@app.route("/admin/addbook", methods=["GET","POST"])
def addbook():
    if session.get("adminuser")== None or session.get("role") != 'admin':
        return redirect(url_for('admin_login'))
    else:
        if request.method=="GET":
            cats = db.session.query(Category).all()
            book=db.session.query(Book).all()
            return render_template("admin/addbook.html",cats=cats, book=book)
        else:
            allowed = ['jpg','png']
            fileobj = request.files['cover']
            filename = fileobj.filename
            newname = "default.png" # default cover
            if filename =='': #no file was uploaded
                flash('Book cover not included', category='error')
            else: #file was selected
                pieces = filename.split('.')
                ext = pieces[-1].lower()
                if ext in allowed:
                    newname = str(int(random.random()*10000000000))+filename
                    fileobj.save('bookapp/static/uploads/'+newname)
                else:
                    flash("File extension not allowed", category='error')
                    
            
            title = request.form.get('title')
            category = request.form.get('category')
            status = request.form.get('status')
            description = request.form.get('description')
            yearpub = request.form.get('yearpub')
            bookcover = newname
            bk = Book(book_title=title,book_desc=description,book_publication=yearpub,book_catid=category,book_status=status,book_cover=newname)
            db.session.add(bk)
            db.session.commit()
            if bk.book_id:
                flash("book has been added")
            else:
                flash("Please try again")
            return redirect(url_for('all_books'))
    
    
@app.route("/admin/delete/<id>/")
def book_delete(id):
    book= db.session.query(Book).get_or_404(id)
    #first delete the file before deleting the book from db
    filename = book.book_cover
    if filename != None and filename !='default.png':
        os.remove("bookapp/static/uploads/"+filename)
    
    db.session.delete(book)
    db.session.commit()
    flash("Book has been deleted!")
    return redirect(url_for("all_books"))

@app.route("/admin/edit/book/<id>",methods=["POST","GET"])
def edit_book(id):
    if session.get("adminuser")== None or session.get("role") != 'admin':
        return redirect(url_for('admin_login'))
    else:
        if request.method =="GET":
            deets=db.session.query(Book).filter(Book.book_id==id).first_or_404()
            cats=db.session.query(Category).all()
            return render_template("admin/editbook.html",deets=deets ,cats=cats)
        else:
            book_2update= Book.query.get(id)
            current_filename = book_2update.book_cover
            book_2update.book_title = request.form.get('title')
            book_2update.book_catid = request.form.get('category')
            book_2update.book_status = request.form.get('status')
            book_2update.book_desc = request.form.get('description')
            book_2update.book_publication = request.form.get('yearpub')

            cover = request.files.get('cover')
            if cover.filename !="":
                name,ext=os.path.splitext(cover.filename)
                if ext.lower() in ['.jpg','.png','.jpeg']:
                    newfilename = generate_string(10) + ext
                    cover.save("bookapp/static/uploads/" + newfilename)
                    book_2update.book_cover = newfilename
                else:
                    flash("The extension of the book cover wasnt included")
                    db.session.commit()
                    flash("Book details was updated")
                return redirect("/admin/books/")

            
    
def generate_string(howmany):
    x = random.sample(string.ascii_lowercase,howmany)
    return ''.join(x)
# @app.after_request()
# def after_request(response):
#     response.headers["Cache-Control"]="no-cache, no-store, must-revalidate"
#     return response