import os
import time
import pytz
import dateutil.parser
from datetime import datetime


from itsdangerous import URLSafeSerializer

from flask import Flask, render_template, jsonify, request, url_for, flash, redirect
import requests
import json

# yourdate = dateutil.parser.parse(datestring)



def create_app():
	# If string is passed to Flask(), then templates folder config is not initialized
	app = Flask(__name__)
	app.config.from_object(os.environ['APP_SETTINGS'])
	

	@app.route('/')
	def home():
		res = requests.get(
			"https://app.paymoapp.com/api/me",
			auth = (app.config["API_KEY_PAYMO"],'any-text-here'))
		print res.text
		query = 'where=time_interval in ("2016-08-23T00:00:00Z","2016-09-27T00:00:00Z")'
		query += '&client_id=4927460'
		query += 'include=entries'
		# query+= '&include=entries.id,entries.billed'
		res = requests.get(
			"https://app.paymoapp.com/api/entries?"+query,
			auth = (app.config["API_KEY_PAYMO"],'any-text-here')
			)
		res_dict = json.loads(res.text)
		n_dict = [e for e in res_dict['entries'] if e['billed'] is False]
		total_hours = sum([ int(e['duration']) for e in res_dict['entries']]) / 60.0 / 60.0
		return render_template("index.html", not_billed = n_dict, total_hours=total_hours)

	@app.route('/client/')
	@app.route('/client/<int:client_id>', methods=["GET","POST"])
	def client(client_id=None):
		if not client_id:
			# res = requests.get(
			# 	"https://app.paymoapp.com/api/me",
			# 	auth = (app.config["API_KEY_PAYMO"],'any-text-here'))
			res = requests.get(
				"https://app.paymoapp.com/api/clients",
				auth = (app.config["API_KEY_PAYMO"],'any-text-here')
				)
			res_dict = json.loads(res.text)
			return render_template("clients.html", data=res_dict)
		try:
			date1 = request.form.get('date1',None) if request.method == "POST" else request.args.get('date1',None)
			date2 = request.form.get('date2',None) if request.method == "POST" else request.args.get('date2',None)
			date1 = datetime.strptime(date1,'%m/%d/%Y')
			date1 = pytz.utc.localize(date1)
			date2 = datetime.strptime(date2,'%m/%d/%Y')
			date2 = pytz.utc.localize(date2)
		except:
			date1 = datetime(2018,5,27,0,  0, 0, 0,pytz.UTC)
			date2 = datetime(2018,10,27,23,59,59, 0,pytz.UTC)	
		endpoint = "https://app.paymoapp.com/api/clients/%s?" % client_id
		query = "include=projects.tasks.entries"
		# query paymo API
		res = requests.get(endpoint+query,auth= (app.config["API_KEY_PAYMO"],"any-text-here"))
		res_dict = json.loads(res.text)
		client_name = res_dict['clients'][0]['name']
		projects = res_dict['clients'][0]['projects']
		# get total hours
		total = []
		entries = []
		for p in projects:
			for task in p['tasks']:
				for e in task['entries']:
					if not e['billed'] and e.get('end_time',False): 
						dateEnd = dateutil.parser.parse(e['end_time'])
						if dateEnd >= date1 and dateEnd <= date2:
							entries.append(e)
							total.append(e['duration'])
		total = sum(total) / 60.0 / 60.0
		return render_template('unbilled.html',
			client_name = client_name,
			client_id=client_id,
			not_billed=entries,
			date1 = date1.strftime('%m/%d/%Y'),
			date2 = date2.strftime('%m/%d/%Y'),
			total = total)

	@app.route('/client/<int:client_id>/mark-billed', methods=["POST"])
	def mark_billed(client_id):
		try:
			date1 = request.form.get('date1',None) if request.method == "POST" else request.args.get('date1',None)
			date2 = request.form.get('date2',None) if request.method == "POST" else request.args.get('date2',None)
			date1 = datetime.strptime(date1,'%m/%d/%Y')
			date1 = pytz.utc.localize(date1)
			date2 = datetime.strptime(date2,'%m/%d/%Y')
			date2 = pytz.utc.localize(date2)
		except:
			return redirect(url_for('client', client_id=client_id))
		endpoint = "https://app.paymoapp.com/api/clients/%s?" % client_id
		query = "include=projects.tasks.entries"
		# query paymo API
		res = requests.get(endpoint+query,auth= (app.config["API_KEY_PAYMO"],"any-text-here"))
		res_dict = json.loads(res.text)
		client_name = res_dict['clients'][0]['name']
		projects = res_dict['clients'][0]['projects']
		# get total hours
		total = []
		entries = []
		for p in projects:
			for task in p['tasks']:
				for e in task['entries']:
					# If entry has not been marked billed and has an end_time
					if not e['billed'] and e.get('end_time',False): 
						dateEnd = dateutil.parser.parse(e['end_time'])
						if dateEnd >= date1 and dateEnd <= date2:
							entries.append(e)
							total.append(e['duration'])
		total = sum(total) / 60.0 / 60.0
		import traceback
		try:
			if client_id and request.form.get('mark_billed'):
				for e in entries:
					requests.put(
						"https://app.paymoapp.com/api/entries/%s" % e['id'],
						auth = (app.config["API_KEY_PAYMO"], 'any-text-here'),
						json = { "billed": True }
						)
					time.sleep(0.2)
			flash('%s hours marked billed.' % total)
			# date1=date1.srtftime("%m/%d/%Y"), date2=date2.srtftime("%m/%d/%Y"))
			return redirect(url_for('client', client_id=client_id))
		except:
			traceback.print_exc()
			return 'Error. No entries marked billed.'



	@app.route('/project/')
	@app.route('/project/<int:project_id>')
	def project(project_id=None):
		if not project_id:
			res = requests.get(
				"https://app.paymoapp.com/api/me",
				auth = (app.config["API_KEY_PAYMO"],'any-text-here'))
			print res.text
			query = 'include=tasks.entries'
			query +='&where=time_interval in ("2016-08-23T00:00:00Z","2016-09-27T00:00:00Z")'
			res = requests.get(
				"https://app.paymoapp.com/api/projects?"+query,
				auth = (app.config["API_KEY_PAYMO"],'any-text-here')
				)
			res_dict = json.loads(res.text)
			projects = res_dict['projects']
			return jsonify({'data':projects})
			projects = [str([str(y)+"<br>" for y in x])+"<br>" for x in projects]
			return str(projects)
		return render_template("index.html", not_billed = n_dict, total_hours=total_hours)	


	@app.route('/payment-portal/<customer_info>', methods=["GET","POST"])
	def portal(customer_info):
		import stripe
		stripe.app.config["API_KEY_PAYMO"] =  "sk_test_yfUe13LqHrnhV5onl2xxeIpz"
		if request.method == "POST":
			token = request.form.get("stripeToken")
			# Create or get existing customer
			customers = stripe.Customer.list()
			customer = [x for x in customers['data'] if x['email']==request.form.get('email')]
			if not customer:
				customer = stripe.Customer.create(
					source=token,
					description="New Customer",
					email=request.form.get('email'),
				)
			else:
				customer = customer[0]
			# Subscribe or charge customer
			if request.form.get("type") == "subscription":
				stripe.Subscription.create(
					customer=customer.id,
					plan= request.form.get("plan_id"),
				)
				return 'customer subscribed'
			else:
				try:
					charge = stripe.Charge.create(
						amount = request.form.get("amount"),
						currency="usd",
						source=token,
						description= request.form.get("description")
					)
				except stripe.error.CardError as e:
					print 'there was an error'
				return 'payment made'
			return 'something wrong happened'
		uss = URLSafeSerializer('subscribe123')
		info = uss.loads(customer_info)
		print info
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

