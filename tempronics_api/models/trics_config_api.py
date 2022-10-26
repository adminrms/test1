from odoo.exceptions import UserError
from odoo import _,api, fields,models
import requests
import json
class TricsConfigApi(models.Model):
    _name = "trics.config.api"
    _description = "Configuracion de URL para el Api de tempronics WEB"


    name = fields.Char('Nombre')
    url = fields.Char('URL Api')
    model = fields.Many2one('ir.model','Modelos')
    active = fields.Boolean('Accion')


    def getconfigapi(self,fmodel):
        vmodels = self.env['ir.model'].search([('model','=',fmodel)])
        apiconfig = self.env['trics.config.api'].search([('model','=',vmodels.id)])
        return apiconfig

    def RequestsHttpApi(self,fmodel,data):
        self = self.env['trics.config.api'].getconfigapi(fmodel)
        if not self.active: #Si no hay configuracion de API, ejecutara la funcion super
            #raise UserError(_("Entro en el if y ejecuta la funcion return super \n %s" % api))
            return True
        try:
            POST = requests.post(self.url,data = data)
            resultText = POST.text
            result = json.loads(resultText)
            if result['success']:
                return True
            else:
                raise UserError(_("Se genero un error en sistema de trazabilidad (API) \n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara
        except requests.exceptions.RequestException as err:
            raise UserError(_("Ocurrio un error en realizar la peticion al servidor remoto \n %s" % err))
        except json.JSONDecodeError as e:
            raise UserError(_("No se recibio un formato correcto para convertir \n %s \n %s" % (e,resultText)))
    
    
    def jsonconvert(self,data):
        return json.dumps(data)

    def sync_data_api(self):
        namemodel = self.model.model
        modelv = self.env[namemodel]
        modelv.sync_data_api()