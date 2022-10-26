from odoo.exceptions import UserError
from odoo import _,api, fields,models, tools

class TricsSerialGroup(models.Model):
    _name="trics.serial.group"
    _description = "Grupo de seriales"
    

    name = fields.Char('Category name',index=True,required=True)
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count')
    
    def _compute_product_count(self):
        results = self.env['product.template'].read_group([('serial_group','in',self.ids)],['serial_group'],['serial_group'])
        group_data = dict((data['serial_group'][0], data['serial_group_count']) for data in results)
        for group in self:
            count = group_data.get(group.id)
            group.product_count = count
    
    def create(self,vals_list):
        URL = 'http://127.0.0.1:88/api/odoo/serial_group.php'
            
            
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    serial_group = fields.Many2one('trics.serial.group','Serial Group',help="Selecciona un grupo", compute='_compute_serial_group',readonly=False,store=True)
    
    @api.depends('tracking')
    def _compute_serial_group(self):
        for rec in self:
            if rec.tracking == 'none' or rec.tracking == 'lot':
                rec.serial_group = None
           