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
	customer_name = db.Column(db.String(128),
		info={
		'label': 'Customer Name',
		# 'validators' : Length(min=1,max=31), 
		})
	number = db.Column(db.String(128), unique=True, info={'label': 'Number'})
	amount_due = db.Column(db.Integer(), info={'label': 'Amount Due'})
	amount_paid = db.Column(db.Integer(), info={'label': 'Amount Paid'})
	void = db.Column(db.Boolean(), default=False, info={'label': 'Voided'})
	generated_filename = db.Column(db.String(128), default=False, info={'label': 'Generated Filename'})

	date_due = db.Column(db.DateTime)

	def __repr__(self):
		return self.name

class RecurringInvoice(Base):
	client_name = db.Column(db.String(128),
		info={
		'label': 'Customer Name',
		})
	paymo_client_id = db.Column(db.Integer(), info={'label': 'Paymo Client ID'})
	service_name = db.Column(db.String(128),
		info={'label': 'Service Name',})
	period_type = db.Column(db.String(128),
		info={'label': 'Period Type',})
	notes = db.Column(db.String(512),
		info={'label': 'Notes',})
	start_date = db.Column(db.DateTime)
	amount = db.Column(db.Integer(), info={'label': 'Amount'})
	stripe_amount = db.Column(db.Integer(), info={'label': 'Stripe Amount'})

	payments = db.relationship('RecurringInvoicePaymentRecord',
		backref='recurring_invoice', lazy='dynamic',
		order_by="RecurringInvoicePaymentRecord.date_modified.desc()")

	@hybrid_method
	def current(self):
		if not self.payments.all() or not self.start_date:
			return False
		temp = self.start_date
		temp.replace(year=datetime.today().year)
		if temp - self.payments.first() >= 0:
			return True
		return False


	def __repr__(self):
		return '<RecurringInvoice:%s>' % self.id

class RecurringInvoicePaymentRecord(Base):
	recurring_invoice_id = db.Column(db.Integer, db.ForeignKey('recurring_invoice.id'))
	def __repr__(self):
		return '<%s%s object at %s, date: %s>' % (
		# self.__class__.__module__,
		'',
		self.__class__.__name__,
		hex(id(self)),
		self.date_create.strftime("%m/%d/%Y") if self.date_create else "",
		)
