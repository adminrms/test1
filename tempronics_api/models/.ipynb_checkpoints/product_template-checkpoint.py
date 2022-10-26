import requests
from odoo.exceptions import UserError
from odoo import _,api, fields,models, tools

class productTemplate(models.Model):
    _inherit = 'product.template'

   
    def copy(self,default=None): #self, contiene los datos del ensamble que se va a compiar no del nuevo que se va generar.
        if default is None:
            default = {}
        if 'default_code' not in default: #Aqui creamos otro tipo de numerodeensamble que se insertara en sistema ade trazabilidad
            default['default_code'] = _("%s_copy") % self.default_code
            default['barcode'] =  _("%s_copy") % self.default_code
        copy = super(productTemplate,self).copy(default=default)
        return copy
        

    @api.model_create_multi
    def create(self, vals_list):
        URL = 'http://127.0.0.1:88/api/odoo/ensamble.php'
        
        for vals in vals_list:
            dataEnsamble = {}
            dataEnsamble['accion'] = 'create'
            #Dato importante
            if not vals.get('default_code'):
                raise UserError(_("El campo {Internal Reference} es necesario para poder creearlo en el sistema de producción"))
            dataEnsamble['descripcion'] = vals['name']
            dataEnsamble['ensamble'] = vals['default_code']
            dataEnsamble['categoria_id'] = vals['categ_id']
            
            dataEnsamble['serie'] = 0
            if vals['tracking'] == 'serial':
                dataEnsamble['serie'] = 1
            POST = requests.post(URL,data = dataEnsamble)
            result = POST.json()
            if not result['success']:
                raise UserError(_("Error al crear un nuevo producto en el sistema de produccion: \n %s" % (result['msj'])))
                #aqui va a crear un producto desde 0
        templates = super(productTemplate,self).create(vals_list)
        return templates

                
                
                    
    def write(self,values):
        """
        VALUES To create:
        {'barcode': 'XX-Test', 'default_code': 'XX-Test'} ID: False
        """
        dataEnsamble = {}
        dataEnsamble['accion'] = 'write'
        dataEnsamble['oldEnsamble'] = self.default_code
        dataEnsamble['numeroensamble'] = values.get('default_code')
        dataEnsamble['descripcion'] = values.get('name')
        dataEnsamble['categoria_id'] = values.get('categ_id')
        dataEnsamble['id_categoria'] = self.categ_id.id
        dataEnsamble['baja'] = values.get('active')
        if values.get('tracking'):
            if values.get('tracking') == 'serial':
                dataEnsamble['serie'] = 1
            else:
                dataEnsamble['serie'] = 0
        
        URL = 'http://127.0.0.1:88/api/odoo/ensamble.php'
        POST = requests.post(URL,data = dataEnsamble)
        result = POST.json()
        if not result['success']:
            raise UserError(_("Ocurrio un error al momento de actualizar el ensamble en sistema de produccion \n %s" % (result['msj'])))
        c = super(productTemplate,self).write(values)
        return c

    def unlink(self):
        dataEnsamble = {}
        dataEnsamble['accion'] = 'unlink'
        dataEnsamble['numeroensamble'] = self.default_code
        URL = 'http://127.0.0.1:88/api/odoo/ensamble.php'
        POST = requests.post(URL,data = dataEnsamble)
        result = POST.json()
        if not result['success']:
            raise UserError(_("Ocurrio un error al momento de borrar el ensamble en sistema de produccion \n %s" % result['msj']))
        unlink = super(productTemplate,self).unlink()
        return unlink
