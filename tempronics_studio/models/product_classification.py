from odoo import _,api,fields,models

class productClassification(models.Model):
    _name = "product.classification"
    _description = "Clasificacion del producto para Ciclo Cuentos"


    name = fields.Char('Nombre')
    product_count = fields.Integer('# Products', compute='_compute_product_count')
    description = fields.Char('Description')
    percent = fields.Float('Porcentaje')


    def _compute_product_count(self):
        results = self.env['product.template'].read_group([('product_classification','in',self.ids)],['product_classification'],['product_classification'])
        group_data = dict((data['product_classification'][0],data['product_classification_count']) for data in results)
        for group in self:
            count = group_data.get(group.id)
            group.product_count = count

