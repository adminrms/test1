from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64


class TempronicsReport(models.Model):
    _name = 'tempronics.report'
    _description = 'Tempronics report'


    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
    color = fields.Integer('Color index', default=0)
    view_wiz = fields.Many2one('ir.ui.view','View')
    d_locations = fields.Many2many('stock.location')
    d_categorys = fields.Many2many('product.category')
    obsolete = fields.Boolean(default = False)
    #Solo para reporte numero dos
    bom_exclude_part = fields.Many2many('product.template',string=" Part to Exclude ")



     
    def call_wizard(self):
        #raise UserError(_("Ocurrio un error al cambiar el estado a cancelado \n %s" % self))
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.view_wiz.model,
            'view_id': self.view_wiz.id,
            'target': 'new',
            'context': {
                'default_location': self.d_locations.ids,
                'default_category': self.d_categorys.ids,
                'default_bom_exclude_part': self.bom_exclude_part.ids,
                'default_document_name': self.name,
                'default_obsolete': self.obsolete
            }
        }

    def _cron_send_email_report_1(self,categorys=[]):
        #6,4,5,16
        report = self.env['tempronics.report'].browse(2)
        values = {
            'form':{
                'location' : report.d_locations.ids,
                'category' : categorys,
                'document_name' : report.name,
                'obsolete' : report.obsolete,
                'product_active' : True,
                'interval' : 6,
                'interval_type' : 'month'
            }
        }

        wizard = self.env['wizard.temp.report.stock.location'].create(values['form'])
        #creamos el excel
        archivo = self.env.ref('tempronics_report.stock_xlsx').render_xlsx(wizard.id,values)
        #convertimos el archivo a Base64 para poder enviarlo por correo
        archivo = base64.b64encode(archivo[0])

        email_template_id = self.env.ref('tempronics_report.email_template_report_stock_month').id
        email_template = self.env['mail.template'].browse(email_template_id)
        email_template.attachment_ids = False
        attachment_values = {
            'name' : report.name,
            'datas' : archivo,
            'datas_fname' : 'monthly_stock_report_tempronics.xlsx',
            'type' : 'binary'
        }
        attachment = self.env['ir.attachment'].create(attachment_values)
        email_template.attachment_ids = [(attachment.id)]
        email_template.send_mail(report.id,force_send=True)
        attachment.unlink()
        