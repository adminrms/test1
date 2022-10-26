import requests
from odoo.exceptions import UserError
from odoo import _,api, fields,models

class ProductionLot(models.Model):
    _inherit = "stock.production.lot"


    @api.model
    def create(self,values):

        """
        {
            'name': 'XXX-Testing-001', 
            'product_id': 600, 
            'ref': False, 
            'use_date': False, 
            'removal_date': False, 
            'life_date': False, 
            'alert_date': False, 
            'message_attachment_count': 0
        }
        """
        product = self.env['product.product'].browse(values['product_id'])
        if product.product_tmpl_id.categ_id.id == 4:
            #el ID 4 es Es Raw material //creamos lote en la base de datos...


        raise UserError(_("Datos de crear lote : \n %s" % product.product_tmpl_id.categ_id.id)) #aqui mostrar el error que ocurrio y no continuara con 
            