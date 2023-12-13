from flask_wtf import FlaskForm
from wtforms.fields import DecimalRangeField, SelectField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length, NumberRange, Optional

class ReviewForm(FlaskForm):
    #id will be created by the database
    product_id = SelectField ("Product: ", validators = [InputRequired()])
    rating = DecimalRangeField ("Rating: ", places=1, validators= [NumberRange(min=0.0, max= 5.0, 
                                                                               message= "Please enter a value between 0 and 5"), InputRequired()])
    #user_id will be retrieved from the database
    review_text = TextAreaField(validators=[Length(max=500), Optional()])
    submit = SubmitField("Submit")
    