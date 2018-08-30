import requests, json

class PaymoAPI(object):
	def __init__(self, api_key):
		self.api_key = api_key

	def clients(self):
		res = requests.get("https://app.paymoapp.com/api/clients",
			auth = (self.api_key,'any-text-here'))
		res = json.loads(res.text)
		res['clients'] = sorted(res['clients'], key=lambda client: client['name'])
		return res

	def client_entries(self, client_id, start, end, **kwargs):
		# kwargs : total_hours (Bool), billed (Bool)
		# query = 'where=time_interval in ("2016-08-23T00:00:00Z","2016-09-27T00:00:00Z")'
		start, end = pytz.utc.localize(start), pytz.utc.localize(end)
		start, end = start.isoformat(), end.isoformat()
		query = 'where=time_interval in ("%s","%s")&client_id=%sinclude=entries' % (
					start, end, client_id
					)
		response = requests.get(
			"https://app.paymoapp.com/api/entries?"+query,
			auth= (self.api_key, 'any-text-here')
			)
		response_data = json.loads(res.text)
		if "billed" in kwargs and (kwargs["billed"] == True or kwargs["billed"] == False):
			return [e for e in response_data['entries'] if e['billed'] is kwargs["billed"]]
		else:
			return response_data['entries']

	def client_unbilled_entries(self,client_id, date1, date2):
		endpoint = "https://app.paymoapp.com/api/clients/%s?" % client_id
		query = "include=projects.tasks.entries"

		res = requests.get(endpoint+query, auth=(self.api_key,"any-text-here"))
		res_dict = json.loads(res.text)
		
		entries = []
		for p in res_dict['clients'][0]['projects']:
			for task in p['tasks']:
				task['entries'] = filter(lambda x: True if not x['billed'] else False,
					task['entries'])
				task['entries'] = filter(lambda x: x.get('end_time', False),
					task['entries'])
				task['entries'] = filter(lambda x: \
					dateutil.parser.parse(x['end_time']) >= date1 and \
					dateutil.parser.parse(x['end_time']) <= date2,
					task['entries'])
				entries += [x for x in task['entries']]
		return entries


	def client_name_from_id(self, client_id):
		endpoint = "https://app.paymoapp.com/api/clients/%s?" % client_id
		query = "include=projects"
		res = requests.get(endpoint+query, auth=(self.api_key,"any-text-here"))
		res_dict = json.loads(res.text)
		return res_dict['clients'][0]['name']

	def get_projects(self, client_id=None):
		res = requests.get(
			"https://app.paymoapp.com/api/projects",
			auth = (self.api_key,'any-text-here')
			)
		res_dict = json.loads(res.text)
		projects = res_dict['projects']
		# list of dictionaries with: code, id, client_id, name
		return projects



	def mark_entries_billed(self,entries):
		results = []
		for entry in entries:
			try:
				update_result = requests.put(
				"https://app.paymoapp.com/api/entries/%s" % entry['id'],
				auth = (self.api_key, 'any-text-here'),
				json = { "billed": True }
				)
				results.append(dict(entry, update_result=update_result))
				time.sleep(0.2)
			except:
				import traceback
				traceback.print_exc()
		return results