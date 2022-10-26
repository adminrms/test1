from odoo import _,models, fields, api
from odoo.exceptions import UserError

class TempBomStockLocation(models.TransientModel):
    _name = "wizard.temp.bom.stock.location"
    _description = "Report MRP BOM stock location"

    location = fields.Many2many('stock.location','temp_bom_loc_rel', 'wh', 'loc', string='Location', required = True)
    bom = fields.Many2one('mrp.bom',string="BOM")
    qty_bom = fields.Integer('Qty to produce', default=1)
    bom_exclude_part = fields.Many2many('product.template')
    document_name = fields.Char('Nombre del documento')


     
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.temp.bom.stock.location'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('tempronics_report.trics_bom_stock_xlsx').report_action(self, data=datas)
            """
            Datas
            {
                'ids': [2], 
                'model': 'wizard.temp.bom.stock.location', 
                'form': 
                    { 
                        'id': 1, 
                        'location': [13, 7, 12], 
                        'bom': 964, 
                        'qty_bom': 1, 
                        'create_uid': 49, 
                        'create_date': datetime.datetime(2021, 1, 12, 20, 1, 46, 96400), 
                        'write_uid': 49, 
                        'write_date': datetime.datetime(2021, 1, 12, 20, 1, 46, 96400), 
                        'display_name': 'wizard.temp.bom.stock.location,1', 
                        '__last_update': datetime.datetime(2021, 1, 12, 20, 1, 46, 96400)
                    }
            }
            """
    