from flask import Blueprint, request
from flask_restful import Resource, Api, marshal_with, fields, reqparse

from ..models import db, RecurringInvoice, Invoice
from datetime import datetime
api_module = Blueprint('api',__name__,url_prefix='/api')
api = Api(api_module)

class CustomDateField(fields.Raw):
	def format(self, value):
		return value.strftime("%m/%d/%Y") if type(value) == datetime and datetime else ""

class DollarAmountField(fields.Raw):
	def format(self, value):
		return "${0:,.2f}".format(float(value)/100) if value and value > 0 else '$0.00'

recurring_invoice_fields = {
	'client_name' : fields.String,
	'service_name' : fields.String,
	'start_date' : CustomDateField,
	'amount' : DollarAmountField,
	'current' : fields.Boolean
}

invoice_fields = {
	'customer_name' : fields.String,
	'number' : fields.String,
	'amount_due' : DollarAmountField,
	'amount_paid' : DollarAmountField,
	'void' : fields.String,
	'generated_filename' : fields.String,
	'date_due' : CustomDateField,
}

parser = reqparse.RequestParser()
parser.add_argument('client_name' , location='json')
parser.add_argument('amount'      , location='json')
parser.add_argument('start_date'  , location='json', type=lambda d: datetime.strptime(d,"%m/%d/%Y") if d else None)
parser.add_argument('service_name', location='json')
parser.add_argument('period_type' , location='json')
parser.add_argument('notes', location='json')
parser.add_argument('recurring_invoice_id', type=int)


class RecurringInvoiceResource(Resource):
	@marshal_with(recurring_invoice_fields)
	def get(self):
		args = parser.parse_args()
		if args['recurring_invoice_id']:
			return [RecurringInvoice.query.get(args['recurring_invoice_id'])]
		else:
			return RecurringInvoice.query.all()
	
	@marshal_with(recurring_invoice_fields)
	def post(self):
		args = parser.parse_args()
		new_recurring_invoice = RecurringInvoice(
			client_name = args['client_name'],
			amount = args['amount'],
			start_date = args['start_date'],
			service_name = args['service_name'],
			period_type = args['period_type'],
			notes = args['notes'],
			)
		db.session.add(new_recurring_invoice)
		db.session.commit()
		return new_recurring_invoice

	@marshal_with(recurring_invoice_fields)
	def put(self):
		args = parser.parse_args()
		recurring_invoice = RecurringInvoice.query.get(args['recurring_invoice_id'])
		for k,v in filter(lambda k,v: k in [], args):
			setattr(recurring_invoice, k, v)
		db.session.commit()
		return recurring_invoice


class InvoiceResource(Resource):
	@marshal_with(invoice_fields)
	def get(self):
		invoices = Invoice.query.order_by(Invoice.date_due.desc()).all()
		return invoices
	


api.add_resource(RecurringInvoiceResource, '/recurring-invoices')
api.add_resource(InvoiceResource, '/invoices')