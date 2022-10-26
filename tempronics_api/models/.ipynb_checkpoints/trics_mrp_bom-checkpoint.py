from odoo.exceptions import UserError
from odoo import _,api, fields,models, tools

class TricsMrpBom(models.Model):
    _name="trics.mrp.bom"
    _rec_name = 'material_product_tmpl_id'
    _order = "id"
    _description = "Traceability BOMs (rutas)"
    trics_bom_id = fields.Many2one('mrp.bom',index=True,ondelete='cascade')
    material_product_tmpl_id = fields.Many2one('product.template','Product(material)',required=True)
            
    rxp_qty = fields.Integer('Ruta por pieza',default=1,required=True,help="Ruta por pieza")
    lotes_qty = fields.Integer('Cantidad por lote',default=1,required=True,help="Cantidad por lote")
    
class MrpBom(models.Model):
    _inherit = ['mrp.bom']
    
    trics_id = fields.One2many('trics.mrp.bom','trics_bom_id')