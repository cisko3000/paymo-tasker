from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
	UserMixin, RoleMixin, login_required
from datetime import date
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import or_, and_

db = SQLAlchemy()

class Base(db.Model):
	__abstract__ = True
	id 				= db.Column(db.Integer, primary_key=True)
	date_create		= db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified 	= db.Column(db.DateTime, default=db.func.current_timestamp(),
											onupdate = db.func.current_timestamp())	

class Invoice(Base):
	customer_name = db.Column(db.String(128), unique=True, 
		info={
		'label': 'Customer Name',
		# 'validators' : Length(min=1,max=31), 
		})
	number = db.Column(db.String(128), info={'label': 'Number'})
	amount_due = db.Column(db.Integer(), info={'label': 'Amount Due'})
	amount_paid = db.Column(db.Integer(), info={'label': 'Amount Paid'})
	void = db.Column(db.Boolean(), default=False, info={'label': 'Amount Paid'})

	date_due = db.Column(db.DateTime)

	def __repr__(self):
		return self.name
