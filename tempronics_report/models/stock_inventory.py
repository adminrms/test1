
from odoo import _,models, fields, api
from odoo.exceptions import UserError


class Inventory(models.Model):
    _inherit = 'stock.inventory'


    def write(self,values):
        #function send email
        res = super(Inventory,self).write(values)
        if self.state == 'done':
            email_template = self.env.ref('tempronics_report.email_template_inventory_adjustment')
            email_template.send_mail(self.id,force_send=True)

        return res

