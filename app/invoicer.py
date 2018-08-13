import xlsxwriter
from operator import itemgetter
from itertools import groupby
# import os

inv_data = {
			"company" : "Sample Company", 
			"bill-to" : "[The Store]", 
			"items" : [
						{
						"description":"Apples",
						"qty":2,
						"unit": 'Some Unit',
						"unit_price":3.00,
						"Amount": 6.00,
						"notes": ""},
						{
						"description":"Avocados",
						"qty":5,
						"unit": 'Some Unit',
						"unit_price":3.00,
						"Amount": 15.00,
						"notes": ""},
					],
			"total" : 21.00, 
			"delivery-fee": 00.00,
			}
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value

def write_invoice_to_worksheet(workbook, worksheet, inv_data, company_data):
	# Define Styles Format.
	money = workbook.add_format({'num_format': '$#,##0.00'})

	bordered = workbook.add_format({'border':1})

	decimal = workbook.add_format()
	decimal.set_num_format('0.0')
	font_size_11 = workbook.add_format()
	font_size_11.set_font_size(11)
	font_size_16 = workbook.add_format()
	font_size_16.set_font_size(16)
	font_size_18 = workbook.add_format()
	font_size_18.set_font_size(18)
	font_size_20 = workbook.add_format()
	font_size_20.set_font_size(20)
	font_size_22 = workbook.add_format()
	font_size_22.set_font_size(22)
	font_size_26 = workbook.add_format()
	font_size_26.set_font_size(26)
	font_size_16 = workbook.add_format()
	font_size_16.set_font_size(16)
	font_size_16_bb = font_size_16.set_bottom()
	bottom_border = workbook.add_format()
	bottom_border.set_bottom()
	worksheet.write(0, 0,"",font_size_22)
	worksheet.set_row(0,23)

	merge_format = workbook.add_format({
		'bold':1,
		'align':'center',
		'valign':'vcenter',
		'fg_color':'white',
		'font_color':'#272fa3',
		'font_size':16,
		})
	merge_format_right = workbook.add_format({
		# 'bold':1,
		'align':'right',
		# 'valign':'vcenter',
		# 'fg_color':'white',
		# 'font_color':'#ed2728',
		# 'font_size':22,
		})
	worksheet.merge_range('A4:C5','LosAngelesCoder.com',merge_format)
	# Write In Cells
	# worksheet.write(1, 0,"Invoice",font_size_22)
	worksheet.merge_range('A2:B2', "Invoice",font_size_16_bb)
	# worksheet.write(1, 5,"Invoice #:",font_size_22)
	worksheet.merge_range('E2:F2', "Invoice #",merge_format_right)
	worksheet.write(1, 7,"",font_size_22)
	worksheet.set_row(1,23)

	worksheet.write(2, 5,"Date:",merge_format_right)
	worksheet.write(2, 6, inv_data.get('date','')  , font_size_11)
	worksheet.set_row(2,30)
	# worksheet.write(3, 0, inv_data.get("company", "Sample Company"),font_size_20)
	# worksheet.set_row(3,23)
	worksheet.write(5, 0,company_data['address1'],font_size_11)
	worksheet.write(6, 0,company_data['address2'],font_size_11)
	# worksheet.set_row(5,17)
	worksheet.write(7, 0,company_data['phone'],font_size_11)
	worksheet.write(8, 0,company_data['url'],font_size_11)
	worksheet.write(10, 0,"Bill to:",font_size_11)

	# worksheet.write(11, 0,inv_data.get("bill-to", "The Store"),font_size_26)

	worksheet.merge_range('A11:B11',inv_data.get("bill-to", "The Store"),font_size_26)
	worksheet.set_row(10,30)

	# worksheet.set_row(16,28)
	# worksheet.write(22, 0,"Description",font_size_16_bb)
	worksheet.merge_range('A18:B18', "Description",font_size_16_bb)



	worksheet.write(17, 1,"",font_size_16_bb)

	worksheet.write(17, 2,"",font_size_16_bb)

	worksheet.write(17, 3,"QTY",font_size_16_bb)
	worksheet.write(17, 4,"Unit Type",font_size_16_bb)
	worksheet.write(17, 5,"Unit Price",font_size_16_bb)
	# worksheet.write(17, 6,"",font_size_16_bb)
	worksheet.write(17, 6,"Amount",merge_format_right)
	worksheet.write(17, 7,"Notes",font_size_16_bb)
	# worksheet.set_row(22,20,bottom_border)
	# # Start from cell 25
	first_row_with_line_item = 18
	row = first_row_with_line_item
	col = 0

	for items in inv_data.get('items'):
		# worksheet.write(row, 0, items.get('description'),money)
		worksheet.merge_range('A'+str(row+1)+':B'+str(row+1),
		 items.get('description'),
		 font_size_16_bb)
		worksheet.write(row, 3, items.get('qty'),decimal)
		worksheet.write(row, 4, items.get('unit'))
		worksheet.write(row, 5,items.get('unit_price'),money)
		worksheet.write(row, 6, items.get('Amount'),money)
		worksheet.write(row, 7, items.get('notes'),font_size_16_bb)
		row += 1
		col = 0
	row += 1
	# worksheet.write(row, 5,"Delivery Fee")
	# worksheet.merge_range('E'+str(row+1)+':F'+str(row+1), "Delivery Fee", merge_format_right)	

	worksheet.merge_range('E'+str(row+1)+':F'+str(row+1), "", merge_format_right)	
	
	worksheet.write(row, 6, inv_data.get("delivery-fee",00.00), money)
	row += 1
	worksheet.write(row + 4, 5, "Total", merge_format_right)
	worksheet.write(row + 4, 6, "=SUM(G%s:G%s)" % (first_row_with_line_item+1,row), money)
	worksheet.set_column(1,1,20)
	worksheet.set_column(6,6,20)

	# add borders
	worksheet.conditional_format('A18:G%s' % (row+5), { 'type': 'no_errors', 'format' : bordered })




def add_to_worksheet(inv_data, filepath, workbook):
	# workbook = xlsxwriter.Workbook(filepath)
	print('BILLTOOOO: '+inv_data['bill-to'])
	worksheet = workbook.add_worksheet(slugify(inv_data['bill-to']))
	write_invoice_to_worksheet(workbook, worksheet, inv_data)
	return workbook
	# workbook.close()

def generate_invoice(inv_data, filepath, company_data):
	# Create a workbook and add a worksheet.
	# os.remove(filepath)
	workbook = xlsxwriter.Workbook(filepath)
	worksheet = workbook.add_worksheet()
	write_invoice_to_worksheet(workbook, worksheet, inv_data, company_data)
	workbook.close()

def prepare_invoice_dictionary(date, client_name, entries):
	# items_total = sum([ i.ext_price for i in items if i.ext_price != None])
	# items.sort(key=lambda x: x.product.name if x and x.product else '')
	items = []
	entries.sort(key=lambda x: x['project_id'])
	for key, group in groupby(entries, lambda x: x['project_id']):
		# groups.append(list(group))
		# keys.append(key)
		# temp_group = list([x for x in group])
		temp_group = list(group)

		temp_dict = temp_group[0]
		temp_dict['description'] = str(key) if not temp_group[0]['project_name'] else temp_group[0]['project_name']
		temp_dict['qty'] = sum([entry['duration'] for entry in temp_group]) / 60.00 / 60.00
		temp_dict['unit'] = 'hrs'
		temp_dict['unit_price'] = '60'
		temp_dict['Amount'] = 60.00 * temp_dict['qty']
		temp_dict['notes'] = ''
		items.append(temp_dict)
	items_total = sum([x['Amount'] for x in items])

	inv_data = {
		"company" : "LosAngelesCoder.com",
		"date" : date.strftime("%m/%d/%Y"),
		"bill-to" : client_name,
		"items" : [
			{
			'description': i['description'],
			'qty'     :    i['qty'],
			'unit'    :    i['unit'],
			'unit_price' : i['unit_price'],
			'Amount': i['Amount'],
			'notes' : ''
			} for i in items
		],
		"total" : items_total,
		"delivery-fee" : ""
	}
	return inv_data