from odoo.exceptions import UserError
from odoo import _,api, fields,models, tools

class productCategory(models.Model):
    _inherit = 'product.category'

    trics_sincronizar_ensambles = fields.Boolean('Sincronizar a Sistema de Produccion (Ensambles)')


    @api.model
    def create(self, values):
        data = {}
        create = super(productCategory,self).create(values)
        data['accion'] = 'create'
        data['id'] = create.id
        data['name'] = create.name
        Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 
        return create

    def write(self,values):
        data = {}
        write = super(productCategory,self).write(values)
        data['accion'] = 'write'
        data['id'] = self.id
        data['name'] = self.name
        Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 
        return write
    
    def unlink(self):
        data = {}
        data['accion'] = 'unlink'
        data['id'] = self.id
        Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 
        return super(productCategory,self).unlink()