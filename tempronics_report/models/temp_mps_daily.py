from odoo import _,models,fields, api
from odoo.exceptions import UserError

class  TempMpsDaily(models.TransientModel):
    _name = "wizard.temp.mrps.daily"
    _description = "Report MRS Daily"


    product_id = fields.Many2one('product.product')
    date_from = fields.Date('Date From')
    date_to= fields.Date('Date To')
    document_name = fields.Char('Nombre del documento')

     
    def export_xls(self):
        saleOrders = self.get_sales(self.date_from,self.date_to,self.product_id.ids)
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.temp.mrps.daily'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        datas['sale_orders'] = saleOrders.ids
        if context.get('xls_export'):
            return self.env.ref('tempronics_report.trics_mps_daily_report').report_action(self, data=datas)


    def get_sales(self,d_from,d_to,p_ids):
        so = self.env['sale.order.line'].search([('commitment_date','>=',d_from),('commitment_date','<=',d_to),('order_id.state','=','sale'),('display_type','=',False)],order="order_id desc,name asc ")
        if p_ids:
            so = so.search([('commitment_date','>=',d_from),('commitment_date','<=',d_to),('product_id','in',p_ids),('order_id.state','=','sale'),('display_type','=',False)],order="order_id desc,name asc ")
        return so
        