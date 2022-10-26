from odoo.exceptions import UserError
from odoo import _,api, fields,models, tools

class productTemplate(models.Model):
    _inherit = 'product.template'

    serial_group = fields.Many2one('trics.serial.group','Serial Group',help="Selecciona un grupo")
    trics_serial = fields.Boolean("Serial para sistema de trazabilidad")
    
    def copy(self,default=None): #self, contiene los datos del ensamble que se va a compiar no del nuevo que se va generar.
        if default is None:
            default = {}
        if 'default_code' not in default: #Aqui creamos otro tipo de numerodeensamble que se insertara en sistema ade trazabilidad
            default['default_code'] = _("%s_copy") % self.default_code
            default['barcode'] =  _("%s_copy") % self.default_code
        copy = super(productTemplate,self).copy(default=default)
        return copy
        

    @api.model
    def create(self, values):
        dataEnsamble = {}
        dataEnsamble['accion'] = 'create'
        dataEnsamble['descripcion'] = values['name']
        dataEnsamble['ensamble'] = values['default_code']
        dataEnsamble['category'] = values['categ_id']
        dataEnsamble['serie'] = 0
        if values.get('trics_serial'):
            dataEnsamble['serie'] = 1
            dataEnsamble['serial_group'] = values['serial_group']
        create = super(productTemplate,self).create(values)
        if not create.categ_id.trics_sincronizar_ensambles:
            return create
        dataEnsamble['id'] = create.id
        Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,dataEnsamble)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 
        return create



    def write(self,values):
        write = super(productTemplate,self).write(values)
        dataEnsamble = {}
        dataEnsamble['accion'] = 'write'
        dataEnsamble['id'] = self.id
        dataEnsamble['ensamble'] = self.default_code
        dataEnsamble['descripcion'] = self.name
        dataEnsamble['category'] = self.categ_id.id
        
        dataEnsamble['active'] = 0
        if not self.active:
            dataEnsamble['active'] = 1
        
        dataEnsamble['serie'] = 0
        if self.trics_serial:
            dataEnsamble['serie'] = 1
            dataEnsamble['serial_group'] = self.serial_group.id
        Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,dataEnsamble)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 
        return write

    def unlink(self):
        dataEnsamble = {}
        dataEnsamble['accion'] = 'unlink'
        dataEnsamble['id'] = self.id
        Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,dataEnsamble)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 

        return super(productTemplate,self).unlink()
