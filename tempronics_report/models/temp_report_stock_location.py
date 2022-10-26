
from datetime import datetime
from odoo import _,models, fields, api
from odoo.exceptions import UserError

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
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.temp.report.stock.location'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('tempronics_report.stock_xlsx').report_action(self, data=datas)
        

        """

        Algo
        {   'ids': [2], 'model': 'wizard.temp.report.stock.location', 'form': 
            {'id': 7, 'location': [13, 86, 18, 12, 21], 'category': [4], 'document_name': 'Report #1 Master Inventory Data', 'create_uid': 49, 'create_date': 
            datetime.datetime(2021, 2, 18, 23, 19, 37, 430394), 'write_uid': 49, 'write_date': datetime.datetime(2021, 2, 18, 23, 19, 37, 430394), 
            'display_name': 'wizard.temp.report.stock.location,7', '__last_update': datetime.datetime(2021, 2, 18, 23, 19, 37, 430394)}
        }
        Fin algo
        Otro algo wizard.temp.report.stock.location(7,)
        Fin del otro algo

        """