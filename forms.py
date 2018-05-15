from flask_security.forms import RegisterForm, LoginForm, StringField, Required


class ExtRegisterForm(RegisterForm):
    full_name = StringField('Name', [Required()])