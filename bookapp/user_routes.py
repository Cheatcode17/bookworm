from flask import render_template,request,abort,redirect,flash,make_response,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash
import json,string,random,requests
#local Imports
from functools import wraps
from bookapp import app,csrf,mail,Message
from bookapp.models import db,Book,User,Category,State,Lga,Reviews,Contact,Donation
from bookapp.forms import *





@app.route('/sendmail')
def send_email():
    msg = Message(subject="Test Email from book worm",recipients=["thugginonthesehoes@gmail.com"],body="Thank you for contacting us", sender="From Bookworm website" )
    mail.send(msg)
    return "Done" 

@app.route("/checkusername/")
def checkusername():
    email = request.args.get('username')
    query = db.session.query(User).filter(User.user_email==email).first()
    if query:
        return "Email is taken"
    else:
        return "Email is good, please go ahead"

   
@app.route("/contact")
def ajax_contact():
    data = "I am a string coming from the server"
    return render_template("user/ajax_test.html",data=data)

@app.route("/submission")
def ajax_submit():
    user = request.args.get('fullname')
    if user != "" and user != None:
        return f"Thank you {user} for completing the form."
    else:
        return "Please complete the form nigga "


@app.route("/favourite")
def favourite_topics():
    bootcamp = {'name':'olusegun','topics':['html','css','python']}
    category = []
    cats = db.session.query(Category).all()
    
    return json.dumps(category)

@app.route("/register/", methods=["GET","POST"])
def register():
    regform = RegForm()
    if request.method =="GET":
        return render_template("user/signup.html",regform=regform)
    else:
        if regform.validate_on_submit():
            #retrieve the form data here and insert into user table
            fullname = regform.fullname.data
            email = regform.email.data
            pwd = regform.pwd.data
            hashed_pwd = generate_password_hash(pwd)
            u=User(user_fullname=fullname,user_email=email,user_pwd=hashed_pwd)
            db.session.add(u)
            db.session.commit()
            flash("An account has been created for you. Please login")
            return redirect("/login")
        else:
            return render_template("user/signup.html",regform=regform)
@app.route("/logout")
def logout():
    if session.get('userloggedin')!=None:
        session.pop('userloggedin',None)
    return redirect("/")

@app.route("/login/", methods=["POST","GET"])
def login():
    if request.method=="GET":
        return render_template("user/loginpage.html")
    else:
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        deets = db.session.query(User).filter(User.user_email==email).first()
        if deets != None:
            hashed_pwd = deets.user_pwd
            if check_password_hash(hashed_pwd,pwd) == True:
                session['userloggedin'] = deets.user_id
                return redirect("/dashboard")
        else:
           flash("invalid credentials, try again")
           return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if session.get('userloggedin')!=None:
        id= session.get('userloggedin')
        userdeets=User.query.get(id)
        return render_template('user/dashboard.html', userdeets=userdeets)
    else:
        flash('You need to login to access the page')
        redirect('/login')


@app.route("/dependent")
def dependent_dropdown():
    states = db.session.query(State).all()
    return render_template("user/show_states.html",states=states)

@app.route("/lga/<stateid>")
def load_lgas(stateid):
    records = db.session.query(Lga).filter(Lga.state_id==stateid).all()
    str2return = "<select class='form-control' name='lga'>"
    for r in records:
        optstr = f"<option value='{r.lga_id}'>"+r.lgn_name+"</option>"
        str2return = str2return + optstr
    str2return = str2return + "</select>"

    return str2return
@app.route("/submit_review/",methods=["POST"])
def submit_review():
    title = request.form.get('title')
    content = request.form.get('content')
    userid = session['userloggedin']
    book = request.form.get('book')
    br = Reviews(rev_title=title,rev_text=content,rev_userid=userid,rev_bookid=book)
    db.session.add(br)
    db.session.commit()

    retstr=f"""<article class="blog-post">
    <h5 class="blog-post-title">{title}</h5>
    <p class="blog-post-meta">Reviwed on January 1, 2021 by <a href="#">{br.reviewby.user_fullname}</a></p>
    <p>{content}</p>
    <hr> 
    </article>"""
    return retstr

@app.route("/")
def home_page():
    books=db.session.query(Book).filter(Book.book_status=="1").limit(4).all()
    return render_template("user/home_page.html",book=books)

@app.route("/book/details/<id>")
def book_details(id):
    book= Book.query.get_or_404(id)
    return render_template("user/reviews.html",book=book)

def login_required(f):
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get("userloggedin") !=None: 
            return f(*args,**kwargs)
        else:
            flash("Access Denied")
            return redirect('/login')
    return login_check

@app.route("/changedp/", methods=["POST","GET"])
@login_required
def changedp():
    id = session.get("userloggedin")
    userdeets = db.session.query(User).get(id)
    dpform = DpForm()
    if request.method =="GET":
        return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)
    else:
        if dpform.validate_on_submit():
            pix = request.files.get('dp')
            filename = pix.filename
            pix.save(app.config['USER_PROFILE']+filename)
            userdeets.user_pix = filename
            db.session.commit()
            flash("Profile picture updated")
            return redirect(url_for('dashboard'))
        else:
            return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)

@app.route("/ajaxopt",methods=["GET","POST"])
def ajax_options():
    cform = ContactForm()
    if request.method=='GET':
        return render_template("user/ajax_options.html",cform=cform)
    else:
        email = request.form.get('email')
        cont = Contact.query.filter(Contact.contact_email==email).first()
        if cont:
            msg2return = {}
        return f"Thank You, your email has been added {email}"
    

@app.route("/myreviews")
def myreviews():
    id = session['userloggedin'] 
    userdeets = db.session.query(User).get(id)
    return render_template("user/myreviews.html",userdeets=userdeets)

        
@app.route("/viewall/")
def viewall():
    books = db.session.query(Book).all()
    return render_template("user/viewall.html", books= books)

@app.route("/profile",methods=["POST","GET"])
@login_required
def edit_profile():
    id = session.get("userloggedin")
    userdeets = db.session.query(User).get(id)
    pform = ProfileForm()
    if request.method =="GET":
        return render_template("user/edit_profile.html",pform=pform,userdeets=userdeets)
    else:
        if pform.validate_on_submit():
            fullname = request.form.get('fullname')
            userdeets.user_fullname = fullname
            db.session.commit()
            flash("Fullname changed")
            return redirect(url_for('dashboard'))
        else:
            return render_template("user/edit_profile.html",pform=pform,userdeets=userdeets)



@app.route("/landing")
def landing_page():
    refno = session.get('trxno')
    transaction_deets = db.session.query(Donation).filter(Donation.don_refno==refno).first()
    url ="https://api.paystack.co/transaction/verify/"+transaction_deets.don_refno
    headers = {"Content-Type":"application/json","Authorization":"Bearer sk_test_593895b0d375c0b63d043e7005a857c2393ca74b"}
    response = requests.get(url,headers=headers)
    rspjson = json.loads(response.text)
    if rspjson['status'] == True:
        paystatus = rspjson['data']['gateway_response']
        transaction_deets.don_status = "Paid"
        db.session.commit()
        return redirect('/dashboard')
    else:
        return redirect('Payment failed ')



@app.route('/donation/', methods=['GET', 'POST'])
def donate():
    if request.method == 'GET':
        deets = db.session.query(User).get(session['userloggedin'])
        return render_template("user/donation.html", deets=deets)
    elif request.method == 'POST':
        amt = request.form.get('amount')
        donor = request.form.get('fullname')
        email = request.form.get('email')
        # Generate a transaction reference for this transaction
        ref =  'BW'+str(generate_string(8))
        # Insert into the database
        donation = Donation(don_amt=amt, don_userid=session['userloggedin'], don_email=email, don_fullname=donor, don_status='pending', don_refno=ref)
        db.session.add(donation)
        db.session.commit()
        # Save the reference no in session
        session['trxno'] = ref
        # Redirect to a confirmation page
        return redirect('/confirm_donation/')
    else:
        deets=db.session.query(User).get(session['userloggedin'])
        return render_template("user/donation.html",deets=deets)


@app.route('/confirm_donation/')
@login_required
def confirm_donation():
    deets= db.session.query(User).get(session['userloggedin'])
    if session.get('trxno')==None:
        flash('Please Complete this form', catergory='error')
        return redirect("/donate/")
    else:
        donation_deets=Donation.query.filter(Donation.don_refno==session['trxno']).first()
        return render_template("user/donation_confirmation.html",donation_deets=donation_deets, deets=deets)
    
@app.route("/intialize/paystack/")
@login_required
def initialize_paystack():
    deets = User.query.get(session['userloggedin'])
    #trasaction details 
    refno = session.get('trxno')
    transaction_deets = db.session.query(Donation).filter(Donation.don_refno==refno).first()
    #make a curl request to the paystack endpoint
    url="https://api.paystack.co/transaction/initialize"
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_593895b0d375c0b63d043e7005a857c2393ca74b"}
    data= {"email": deets.user_email, "amount": transaction_deets.don_amt, "reference": refno}
    response =requests.post(url,headers=headers,data=json.dumps(data))
    rspjson = response.json()
    if rspjson['status'] == True:
        redirectURL = rspjson['data']['authorization_url']
        return redirect(redirectURL)
    else:
        flash("Please complete the form again")
        return redirect('/donation')


    
def generate_string(howmany):
    x= random.sample(string.digits,howmany)
    return ''.join(x)