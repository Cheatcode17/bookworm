from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,SubmitField
from wtforms.validators import Email,DataRequired,EqualTo,Length
from flask_wtf.file import FileField, FileRequired,FileAllowed

class RegForm(FlaskForm):
    fullname=StringField("FullName",validators=[DataRequired()])
    email=StringField("Email",validators=[Email(),DataRequired(message='MY Guy Put Email Naaaa....')])
    pwd=PasswordField("Enter Password",validators=[DataRequired()])
    confpwd= PasswordField("Confirm Password",validators=[EqualTo('pwd')])
    
    btnsubmit= SubmitField("Register!")

class DpForm(FlaskForm):
    dp = FileField("Upload a Profile Piture",validators=[FileRequired(),FileAllowed(["jpg","png","jpeg"])])
    btnupload = SubmitField("Upload Picture")

    
class ProfileForm(FlaskForm):
    fullname=StringField("FullName",validators=[DataRequired()])
    btnsubmit = SubmitField("update Profile")

class ContactForm(FlaskForm):
    email=StringField("Email",validators=[Email(),DataRequired()])
    button= SubmitField("Submit!")


