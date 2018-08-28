from flask import Blueprint, request
from flask_restful import Resource, Api, marshal_with, fields, reqparse

from ..models import db, RecurringInvoice
from datetime import datetime
api_module = Blueprint('api',__name__,url_prefix='/api')
api = Api(api_module)

recurring_invoice_fields = {
	'client_name' : fields.String,
	'service_name' : fields.String,
	'start_date' : fields.DateTime(dt_format='iso8601'),
}

parser = reqparse.RequestParser()
parser.add_argument('client_name' , location='json')
parser.add_argument('amount'      , location='json')
parser.add_argument('start_date'  , location='json', type=lambda d: datetime.strptime(d,"%m/%d/%Y") if d else None)
parser.add_argument('service_name', location='json')
parser.add_argument('notes', location='json')


class RecurringInvoiceResource(Resource):
	@marshal_with(recurring_invoice_fields)
	def get(self):
		recurring_invoices = RecurringInvoice.query.all()
		return recurring_invoices
	
	@marshal_with(recurring_invoice_fields)
	def post(self):
		args = parser.parse_args()
		print(args)
		print(request.json)
		new_recurring_invoice = RecurringInvoice(
			client_name = args['client_name'],
			amount = args['amount'],
			start_date = args['start_date'],
			service_name = args['service_name'],
			notes = args['notes'],
			)
		db.session.add(new_recurring_invoice)
		db.session.commit()
		return new_recurring_invoice

		

api.add_resource(RecurringInvoiceResource, '/recurring-invoices')