from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, InputRequired

class CreateCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})

    submit = SubmitField("submit")

class EditCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM Notes (hidden)", render_kw={"rows": 15})

    submit = SubmitField("submit")

class EditCharacterFormAdmin(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM Notes (hidden)", render_kw={"rows": 15})

    submit = SubmitField("submit")