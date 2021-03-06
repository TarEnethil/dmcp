from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms_components import SelectField as OptGroupSelectField
from wtforms.validators import Length, InputRequired


class CreateCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100), InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    profile_picture = FileField("Logo")
    description = TextAreaField("Description", render_kw={"rows": 15})
    private_notes = TextAreaField("Private Notes (hidden)", render_kw={"rows": 15})
    is_visible = BooleanField("Is publicly visible", default=True)

    submit = SubmitField("Create Character")


class EditCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100), InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    profile_picture = FileField("Logo")
    description = TextAreaField("Description", render_kw={"rows": 15})
    private_notes = TextAreaField("Private Notes (hidden)", render_kw={"rows": 15})
    is_visible = BooleanField("Is publicly visible")

    submit = SubmitField("Save Character")


class JournalForm(FlaskForm):
    title = StringField("Name", validators=[Length(min=0, max=100), InputRequired()])
    is_visible = BooleanField("Is publicly visible")
    content = TextAreaField("Description", render_kw={"rows": 15})
    session = OptGroupSelectField("Belongs to Session", coerce=int)

    submit = SubmitField("Submit")
