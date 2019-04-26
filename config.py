import os
class BaseConfig(object):
	# Flask-Blogging configuration
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))
	MAX_CONTENT_LENGTH = 5 * 4194304 # is 4 mbs in bytes X 5 pictures
	DEBUG = False
	# Flask-Security configurations
	# SECURITY_CONFIRMABLE = True
	# SECURITY_POST_REGISTER_VIEW = "/verify-email"
	# SECURITY_POST_CONFIRM_VIEW = "/seller-signup"
	SECURITY_REGISTERABLE = True
	SECURITY_RECOVERABLE = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USE_TLS = False
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME','')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD','')
	MAIL_FAIL_SILENTLY = False

	# MAIL_SUPPRESS_SEND = True
    # TESTING = True
	SECRET_KEY = 'bogus-123'
	SECURITY_USER_IDENTITY_ATTRIBUTES = ('username','email')
	SECURITY_PASSWORD_HASH = 'bcrypt'
	SECURITY_PASSWORD_SALT = 'bogus-ASalt.addSalsaTooPlease.123'
	SECURITY_RECOVERABLE = True
	RANDOM_PASSWORD_CHARS = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ$!?"
	SECURITY_TRACKABLE = True
	TEMPLATES_AUTO_RELOAD = True
	FLATPAGES_ROOT = "blog"
	FLATPAGES_EXTENSION = ".html"
	STATIC_ROOT = 'static'
	
	API_KEY_STRIPE = os.environ.get('API_KEY_STRIPE','')
	API_KEY_STRIPE_PUBLIC = os.environ.get('API_KEY_STRIPE_PUBLIC','')
	API_KEY_PAYMO  = os.environ.get('API_KEY_PAYMO','')

	COMPANY_ADDRESS1  = os.environ.get('COMPANY_ADDRESS1','')
	COMPANY_ADDRESS2  = os.environ.get('COMPANY_ADDRESS2','')
	COMPANY_PHONE  = os.environ.get('COMPANY_PHONE','')
	COMPANY_URL  = os.environ.get('COMPANY_URL','')



class DevConfig(BaseConfig):
	SECURITY_REGISTERABLE = False
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
	DEBUG = True
	# SERVER_NAME = 'localhost'
	# HOST = 'localhost'
	RECAPTCHA_KEY = ''
	RECAPTCHA_SECRET = ''
	


	CDN_DOMAIN = 'abc-4a26.kxcdn.com'


class LiveConfig(BaseConfig):
	SECURITY_REGISTERABLE = False
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
	DEBUG = False
	SERVER_NAME = 'xxxx.com'
	RECAPTCHA_KEY = os.environ.get('RECAPTCHA_KEY','')
	RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET','')


	CDN_DOMAIN = 'bogus-cdn-url.com'
	CDN_HTTPS = False
	# HOST = 'localhost'
