import os
import time
from datetime import datetime, timedelta
import pytz
import dateutil.parser

from itsdangerous import URLSafeSerializer

from flask import (
	Flask,
	render_template,
	jsonify,
	request,
	url_for,
	flash,
	redirect,
	current_app,
	send_from_directory
	)
import requests
import json

from invoicer import (
	slugify,
	generate_invoice,
	add_to_worksheet,
	prepare_invoice_dictionary,
	)
# yourdate = dateutil.parser.parse(datestring)

from paymo_api import PaymoAPI

def create_app():
	# If string is passed to Flask(), then templates folder config is not initialized
	app = Flask(__name__)
	app.config.from_object(os.environ['APP_SETTINGS'])
	paymo = PaymoAPI(app.config['API_KEY_PAYMO'])

	from models import db, Invoice, RecurringInvoice, RecurringInvoicePaymentRecord
	from mod_api import api_module
	app.register_blueprint(api_module)

	db.init_app(app)

	@app.before_first_request
	def create_user():
		# db.drop_all()
		db.create_all()
		db.session.commit()

	@app.template_filter()
	def add_commas(value):
		return format(int(float(value)), ',d')

	@app.template_filter()
	def add_commas_integer_value(value):
		return format(int(float(value)/100), ',d')
	
	def get_new_invoice_number(customer_str):
		try:
			with open('invoice_count.txt','r+') as cfile:
				data = json.load(cfile)
				invoice_number = int(data.get(customer_str, 0))+1
				data[customer_str] = invoice_number
				cfile.seek(0)
				json.dump(data,cfile)
		except IOError:
			with open('invoice_count.txt','w') as nfile:
				data = {customer_str:1001}
				json.dump(data,nfile)
				invoice_number = 1001
		return customer_str.upper()+'-'+str(invoice_number)


	@app.route('/')
	def index():
		return render_template("index.html")

	@app.route('/client/')
	@app.route('/client/<int:client_id>', methods=["GET","POST"])
	def client(client_id=None):
		if not client_id:
			clients = paymo.clients()
			return render_template("clients.html", data=clients)
		try:
			date1 = request.form.get('date1',None) if request.method == "POST" else request.args.get('date1',None)
			date2 = request.form.get('date2',None) if request.method == "POST" else request.args.get('date2',None)
			date1 = datetime.strptime(date1,'%m/%d/%Y')
			date1 = pytz.utc.localize(date1)
			date2 = datetime.strptime(date2,'%m/%d/%Y')
			date2 = pytz.utc.localize(date2)
		except:
			date1 = datetime.now()
			date1 = date1.replace(day=1)
			date1 = pytz.UTC.localize(date1)
			date2 = date1.replace(month=date1.month+1)
			date2 = date2 - timedelta(days=1)
			date2 = date2.replace(hour=23,minute=59, second=59)
		client_name = paymo.client_name_from_id(client_id)
		entries = paymo.client_unbilled_entries(client_id, date1, date2)
		entries = [dict(entry, client_id=client_id) for entry in entries]
		total = sum([x['duration'] for x in entries]) / 60.00 / 60.00
		
		return render_template('unbilled.html',
			client_name = client_name,
			client_id=client_id,
			not_billed=entries,
			date1 = date1.strftime('%m/%d/%Y'),
			date2 = date2.strftime('%m/%d/%Y'),
			total = total)

	@app.route('/client/<int:client_id>/mark-billed', methods=["POST"])
	def mark_billed(client_id):
		if not request.form.get('mark_billed', False):
			flash("Request form error.")
			return redirect(url_for('client', client_id=client_id))
		try:
			date1 = request.form.get('date1',None) if request.method == "POST" else request.args.get('date1',None)
			date2 = request.form.get('date2',None) if request.method == "POST" else request.args.get('date2',None)
			date1 = datetime.strptime(date1,'%m/%d/%Y')
			date1 = pytz.utc.localize(date1)
			date2 = datetime.strptime(date2,'%m/%d/%Y')
			date2 = pytz.utc.localize(date2)
		except:
			return redirect(url_for('client', client_id=client_id))

		entries = paymo.client_unbilled_entries(client_id, date1, date2)
		total = sum([x['duration'] for x in entries]) / 60.00 / 60.00

		entries_billed = paymo.mark_entries_billed(entries)
		total_billed = sum([x['duration'] for x in entries_billed]) / 60.00 / 60.00

		flash('%s hours marked billed (%s/%s entries).' % (
			total_billed,
			len(entries_billed),
			len(entries))
		)
		flash('Error. No entries marked billed.') if not entries_billed else None		
		return redirect(url_for('client', client_id=client_id))

	@app.route('/client/<int:client_id>/create-invoice', methods=["POST"])
	def create_invoice(client_id):
		if not request.form.get('generate_invoice', False):
			flash("Request form error.")
			return redirect(url_for('client', client_id=client_id))
		try:
			date1 = request.form.get('date1',None) if request.method == "POST" else request.args.get('date1',None)
			date2 = request.form.get('date2',None) if request.method == "POST" else request.args.get('date2',None)
			date1 = datetime.strptime(date1,'%m/%d/%Y')
			date1 = pytz.utc.localize(date1)
			date2 = datetime.strptime(date2,'%m/%d/%Y')
			date2 = pytz.utc.localize(date2)
		except:
			return redirect(url_for('client', client_id=client_id))

		entries = paymo.client_unbilled_entries(client_id, date1, date2)
		total = sum([x['duration'] for x in entries]) / 60.00 / 60.00
		client_name = paymo.client_name_from_id(client_id)		
		date = datetime.today()
		# add project_name to entries
		projects = paymo.get_projects()
		projects = filter(lambda x: x['client_id'] == client_id, projects)

		new_invoice = Invoice()
		new_invoice.number = get_new_invoice_number(client_name)
		# Place project name info in entries
		for entry in entries:
			the_project = next(iter(filter(lambda x: x['id']==entry['project_id'],projects)), None)
			entry['project_name'] = the_project['name'] if the_project else ''

		inv_data = prepare_invoice_dictionary(date, client_name, entries,new_invoice.number)
		the_dir = os.path.dirname(current_app.root_path)
		the_dir = the_dir+"/generated"
		if not os.path.exists(the_dir):
			os.makedirs(the_dir)
		print inv_data['bill-to']
		print date.strftime("%m%d%Y")



		invoice_filename = slugify('inv_%s_%s_%s' % ( 
			inv_data['bill-to'],
			new_invoice.number,
			date.strftime("%m%d%Y") )
		)
		invoice_filename += '.xlsx'

		new_invoice.customer_name = client_name
		new_invoice.amount_due = (sum([x['duration'] * 60.00 for x in entries]) / 60.00 / 60.00 ) * 100
		new_invoice.amount_paid = 0
		new_invoice.generated_filename = invoice_filename
		
		company_data = {
			'address1': current_app.config['COMPANY_ADDRESS1'],
			'address2': current_app.config['COMPANY_ADDRESS2'],
			'phone': current_app.config['COMPANY_PHONE'],
			'url': current_app.config['COMPANY_URL'],
			}
		generate_invoice(inv_data, the_dir+"/"+invoice_filename, company_data)
		db.session.add(new_invoice)
		db.session.commit()
		return redirect(url_for('download_invoice', filename=invoice_filename))

	@app.route('/download-invoice/<path:filename>', methods=["GET"])
	def download_invoice(filename):
		the_dir = os.path.dirname(current_app.root_path)
		the_dir = the_dir+"/generated/"
		return send_from_directory(the_dir,filename)

	@app.route('/toggle-paid/<int:inv_id>', methods=["POST"])
	def toggle_paid(inv_id):
		inv = Invoice.query.get(inv_id)
		if not inv.amount_paid or inv.amount_paid != inv.amount_due:
			inv.amount_paid = inv.amount_due
		else:
			inv.amount_paid = 0
		db.session.commit()
		return redirect(url_for('invoices'))


	@app.route('/project/')
	@app.route('/project/<int:project_id>')
	def project(project_id=None):
		return render_template("index.html", not_billed = n_dict, total_hours=total_hours)	


	@app.route('/payment-portal/<customer_info>', methods=["GET","POST"])
	def portal(customer_info):
		import stripe
		stripe.app.config["API_KEY_PAYMO"] =  "sk_test_yfUe13LqHrnhV5onl2xxeIpz"
		if request.method == "POST":
			token = request.form.get("stripeToken")
			# Create or get existing customer
			customers = stripe.Customer.list()
			customer = [x for x in customers['data'] if x['email']==request.form.get('email','').trim()]
			customer = customer[0] if customer else stripe.Customer.create(
									source=token,
									description="New Customer",
									email=request.form.get('email'),
									)
			stripe_result = None
			try:
				if request.form.get("type") == "subscription":
					stripe_result = stripe.Subscription.create(
						customer=customer.id,
						plan= request.form.get("plan_id"),
					)
				else:
					stripe_result = stripe.Charge.create(
						amount = request.form.get("amount"),
						currency="usd",
						source=token,
						description= request.form.get("description")
					)
			except stripe.error.CardError as e:
				print 'there was an error'
			except Exception as e:
				raise Exception(e)
			print(stripe_result)
			flash("Transaction was successful.")
			return redirect(url_for('index'))

		uss = URLSafeSerializer('subscribe123')
		info = uss.loads(customer_info)
		return render_template("payment.html", info=info, customer_info=customer_info)

	@app.route('/portal-generator', methods=['GET','POST'])
	def generator():
		import stripe
		stripe.api_key =  app.config["API_KEY_STRIPE"]
		res = stripe.Plan.list()
		if request.method == "POST":
			if request.form.get('subscription'):
				plans = res['data']
				the_plan = [x for x in res['data'] if x["id"] == request.form.get('subscription') ][0]
				info = {
					"email" : request.form.get('email'),
					"name"  : request.form.get('name'),
					"service"  : the_plan['name'],
					"plan_id"  : the_plan['id'],
					"amount"  : the_plan['amount'],
					"type" : "subscription"
				}
			elif request.form.get('description') and request.form.get('amount'):
				info = {
					"email" : request.form.get('email'),
					"name"  : request.form.get('name'),
					"service"  : request.form.get('description'),
					"plan_id"  : "",
					"amount"  : request.form.get('amount'),
					"type" : "payment",
				}
			else:
				return 'Missing subscription, or service and amount'
			uss = URLSafeSerializer('subscribe123')
			serialized_info = uss.dumps(info)
			print(serialized_info)
			return '<a href="'+url_for('portal', customer_info=serialized_info)+'">the link</a>'
		else:
			res = stripe.Plan.list()
			plans = res['data']
			return render_template("portal-generator.html", plans = plans)

	@app.route('/invoices')
	def invoices():
		invoices = Invoice.query.all()
		return render_template("invoices.html", invoices=invoices)

	@app.route('/recurring')
	def recurring():
		recurring = RecurringInvoice.query.all()
		return render_template("recurring.html", recurring=recurring)

	@app.route('/recurring/delete/<int:r_id>', methods=["POST"])
	def recurring_delete(r_id):
		inv = RecurringInvoice.query.get(r_id)
		if inv:
			db.session.delete(inv)
			db.session.commit()
			flash("Recurring profile deleted.")
		return redirect(url_for('recurring'))

	@app.route('/recurring/mark_paid/<int:r_id>', methods=["POST"])
	def recurring_mark_paid(r_id):
		inv = RecurringInvoice.query.get(r_id)
		if inv:
			inv.payments.append(RecurringInvoicePaymentRecord())
			db.session.commit()
			flash("Added paid record.")
		return redirect(url_for('recurring'))

	@app.route('/recurring/mark_unpaid/<int:r_id>', methods=["POST"])
	def recurring_mark_unpaid(r_id):
		inv = RecurringInvoice.query.get(r_id)
		if inv and inv.payments:
			most_recent_payment = inv.payments.first()
			db.session.delete(most_recent_payment)
			db.session.commit()
			flash("Most recent period marked unpaid.")
		return redirect(url_for('recurring'))

	@app.route('/stripe/calc/<amount>')
	def stripe_calc(amount):
		try:
			x = float(amount)
			# ( y - .30 ) / 0.029 = x
			y  = ( x + 0.30 ) / (1.00 - 0.029)
			flash("Then you should charge $%0.2f" % y)
			return "Charge $%0.2f to get $%0.2f" % (y, x)
		except:
			return "usage: /striper/&lt;amount&gt;"
	return app

if __name__ == '__main__':
	app.run(debug=True)

