from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email 

class inputQuery(FlaskForm):
    loc = StringField("Location", validators=[DataRequired()])
    proj = StringField("Project Name", validators=[DataRequired()])
    ext = IntegerField("Extent In KMs", validators=[DataRequired()])
    # uname = StringField(" Survey Officer Name: ", validators=[DataRequired()])
    # email = StringField(" Survey Officer Email: ", validators=[DataRequired(),Email()])
    but = SubmitField("Submit")
