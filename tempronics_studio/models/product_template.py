from odoo import _,api,fields,models,tools

class productTemplate(models.Model):
    _inherit = 'product.template'
    
    product_classification = fields.Many2one('product.classification','Classification',help="Selecciona una clasificacion")
    