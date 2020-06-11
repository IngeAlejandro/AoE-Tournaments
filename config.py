class Config:

    SECRET_KEY = '$tH1sIsa#sUp2rm@gAul7rATu8bo5ecretke4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///AoET.db'


    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'mail@gmail.com'
    MAIL_PASSWORD = 'password'

    # Flask-User settings
    USER_CORPORATION_NAME = 'Álex Frausto'
    USER_COPYRIGHT_YEAR = 2020
    USER_APP_NAME = "AoE II DE Tournaments"
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "aguilarfrausto@gmail.com"
    USER_APP_VERSION = '1.1'
    USER_ENABLE_CHANGE_PASSWORD = True
    USER_ENABLE_CHANGE_USERNAME = True
    USER_ENABLE_CONFIRM_EMAIL = True
    USER_ENABLE_FORGOT_PASSWORD = True
    USER_ENABLE_REGISTRATION = True
    USER_REQUIRE_RETYPE_PASSWORD = True
    USER_ENABLE_USERNAME = True
    USER_AFTER_LOGOUT_ENDPOINT = 'main.home'
