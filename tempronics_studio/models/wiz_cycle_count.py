from odoo import _,models,fields, api
from odoo.exceptions import UserError

class  WizCycleCount(models.TransientModel):
    _name = "wizard.cycle.count.list"
    _description = "Cycle Count List"

    location = fields.Many2one('stock.location', string='Location', required = True)

     
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.cycle.count.list'
        datas['location'] = self.location.id
        if context.get('xls_export'):
            return self.env.ref('tempronics_studio.cycle_count_list').report_action(self, data=datas)

    