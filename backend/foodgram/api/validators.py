from django.core.validators import RegexValidator

username_validator = RegexValidator(
    regex=r'^[w.@+-]+Z',
    message='Invalid characters in username',
    code='invalid_username'
)
