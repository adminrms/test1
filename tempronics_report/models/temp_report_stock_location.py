
from datetime import datetime
from odoo import _,models, fields, api
from odoo.exceptions import UserError
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
import pytz
import json
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class TempReportStockLocation(models.TransientModel):
    _name = "wizard.temp.report.stock.location"
    _description = "Report Stock Location"

    location = fields.Many2many('stock.location', 'temp_wh_loc_rel', 'wh', 'loc', string='Location')
    category = fields.Many2many('product.category', 'temp_categ_loc_rel', 'categ', 'loc', string='Category')
    document_name = fields.Char('Nombre del documento')
    obsolete = fields.Boolean(default=False)
    product_active = fields.Boolean(string="Product Active",default=True)
    interval = fields.Integer(string='Interval',
                              default=6,
                              help='Interval')
    interval_type = fields.Selection([
        ('day', 'Day(s)'),
        ('week', 'Week(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)')],
        string='Interval type',
        default='month',
        help="Test")

    def export_xls(self):
        
        data = {
            'ids' : self.ids,
            'model' : self._name,
            'location' : self.location.ids,
            'document_name' : self.document_name,
            'obsolete' : self.obsolete,
            'product_active' : self.product_active,
            'interval' : self.interval,
            'category' : self.category.ids,
            'interval_type' : self.interval_type
        }
        
        return {
            'type': 'ir.actions.report',
            'data': {
                'model' : self._name,
                'options' : json.dumps(data, default=date_utils.json_default),
                'output_format' : 'xlsx',
                'report_name' : self.document_name
            },
            'report_type': 'xlsx'
        }
    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        #comp = self.env.user.company_id.name
        sheet = workbook.add_worksheet('Stock Info')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        #estilo rojo
        cell_red_style = workbook.add_format({'border':1,'align':'center',
                                                'bg_color': '#FFC7CE',
                                                'font_color': '#9C0006'})
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        format1.set_border()
        sheet.set_zoom(80)
        w_house = ', '
        cat = ', '
        c = []
        sheet.merge_range(0, 0, 0, 3, data['document_name'], format4)
        d1 = data['category']
        if d1:
            for i in d1:
                c.append(self.env['product.category'].browse(i).name)
            cat = cat.join(c)
            #sheet.merge_range(1, 0, 1, 1, 'Category(s) : ', format4)
            sheet.write(1, 0, 'Category(s) : ', format4)
            #sheet.merge_range(1, 2, 1, 3 + len(d1), cat, format4)
            sheet.write(1, 2, cat, format4)
        
        tz = pytz.timezone('US/Arizona')
        time = pytz.utc.localize(datetime.now()).astimezone(tz)
        sheet.merge_range('A4:G4', 'Report Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format1)
        
        sheet.merge_range('A5:J5', 'Product Information', format1)
        w_col_no = 8
        w_col_no1 = 8
        


        sheet_title = [
            _('SKU'),
            _('Name'),
            _('Category'),
            _('Cost Price'),
            _('UM'),
            _('LT'),
            _('MIN'),
            _('MAX'),
            _('Supplier'),
            _('Country'),

        ]

        namesshorts = ['WH/Input','WH/Stock','DGWH/Stock']
        
        locations = self.env['stock.location'].search([('id', 'in', data['location'])])

        for location in locations:
            name = location.display_name
            if name not in namesshorts:
                name = location.name
            sheet_title.append(_(name))
        sheet_title.append(_('Total'))
        sheet.merge_range(4, 10, 4, len(locations)+10, 'Locations', format1)
        sheet.write_row(5, 0, sheet_title, format1)


        #sheet.write(5,count+2,'Reserved',format21)
        #sheet.write(5,count+3,'BAL',format21)
        sheet.set_column(1, 1, 42)
        sheet.set_column(2, 2, 14)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 6)
        sheet.set_column(5, 5, 3)
        sheet.set_column(6, 6, 6)
        sheet.set_column(7, 7, 6)
        sheet.set_column(8, 8, 34)
        sheet.set_column(9, 9, 7)
        sheet.set_column(10, len(sheet_title), 14)
        prod_row = 6
        prod_col = 0
        font_size_8.set_border()
        font_size_8_l.set_border()
        font_size_8_r.set_border()

        obsolete = self.obsolete
        product_active = self.product_active
        relative = self.get_relativedelta(data['interval'],data['interval_type'])
        relative = time + relative
        sheet.freeze_panes(6,0)

        for product in self.get_producs(d1,obsolete,product_active,relative):
            sheet.write(prod_row, 0, product['sku'], font_size_8)
            sheet.write(prod_row,1, product['name'], font_size_8_l)
            sheet.write(prod_row,2, product['category'], font_size_8)
            sheet.write(prod_row,3, product['cost_price'], font_size_8)
            sheet.write(prod_row,4, product['um'], font_size_8)
            sheet.write(prod_row,5, product['lt'], font_size_8)
            sheet.write(prod_row,6, product['min'], font_size_8)
            sheet.write(prod_row,7, product['max'], font_size_8)
            sheet.write(prod_row,8, product['vendor'], font_size_8)
            sheet.write(prod_row,9, product['country'], font_size_8)
            totals = self.get_totals(product['id'],locations)
            sheet.write_row(prod_row,10,totals,font_size_8)
            prod_row = prod_row + 1

        sheet.conditional_format(6,10,prod_row,len(locations)+10,{'type':     'cell',
                                          'criteria': '<',
                                          'value':    0,
                                          'format':   cell_red_style})
        
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
    
    def get_totals(self,id,locations):
        total = 0
        totals = []
        product = self.env['product.product'].search([('id', '=', id)])
        for location in locations:
            virtual_available = product.with_context({'location': location.id}).virtual_available
            outgoing_qty = product.with_context({'location': location.id}).outgoing_qty
            incoming_qty = product.with_context({'location': location.id}).incoming_qty
            available_qty = virtual_available + outgoing_qty - incoming_qty
            total = total + available_qty 
            totals.append(available_qty)
        totals.append(total)
        return totals
    def get_producs(self, categ_id,obsolete,product_active,relative):
        lines = []
        if categ_id:
            categ_products = self.env['product.product'].search([('categ_id', 'in', categ_id),('active','=',product_active)])

        else:
            categ_products = self.env['product.product'].search([('active','=',product_active)])
        #product_ids = tuple([pro_id.id for pro_id in categ_products])

        if obsolete:
            categ_products = self.get_obsolete(categ_products,relative)

        for obj in categ_products:
            vendor = 'N/A'
            lt = 'N/A'
            vendorname = 'N/A'
            country = 'N/A'
            if(obj.seller_ids):
                vendorname = obj.seller_ids[0].name.name
                lt = obj.seller_ids[0].delay
                country = obj.seller_ids[0].name.country_id.code

            vals = {
                'id': obj.id,
                'sku': obj.default_code,
                'name': obj.name,
                'category': obj.categ_id.name,
                'cost_price': obj.standard_price,
                'lt': lt,
                'min': obj.reordering_min_qty,
                'max': obj.reordering_max_qty,
                'um': obj.uom_id.name,
                'vendor': vendorname,
                'country': country,
            }
            lines.append(vals)
        return lines
    
    def get_relativedelta(self,interval, step):
        if step == 'day':
            return relativedelta(days=-interval)
        elif step == 'week':
            return relativedelta(weeks=-interval)
        elif step == 'month':
            return relativedelta(months=-interval)
        elif step == 'year':
            return relativedelta(years=-interval)


    def get_obsolete(self,categ_products, interval):
        data = []
        for product in categ_products:
            lines = self.env['stock.move.line'].search([('date','>=',interval),('product_id','=',product.id)],count=True,limit=1)
            if lines == 0:
                data.append(product)

        return data