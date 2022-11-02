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


    @api.model
    def create(self,values):
        create = super(TricsSerialGroup,self).create(values)
        data = {}
        data['nombre'] = values['name']
        data['id'] = create.id
        data['accion'] = 'create'
        Api = self.env['trics.config.api'].RequestsHttpApi(self._name,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj']))
        return create

    def write(self,values):
        data = {}
        data['nombre'] = values['name']
        data['id'] = self.id
        data['accion'] = 'write'
        Api = self.env['trics.config.api'].RequestsHttpApi(self._name,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj']))

        return super(TricsSerialGroup,self).write(values)

    def unlink(self):
        data = {}
        data['id'] = self.id
        data['accion'] = 'unlink'
        Api = self.env['trics.config.api'].RequestsHttpApi(self._name,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj']))

        return super(TricsSerialGroup,self).unlink()
            
    

           