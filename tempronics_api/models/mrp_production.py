import requests
import json
from odoo.exceptions import UserError
from odoo import _,api, fields,models

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def create(self,values):
        
        dataProduction = {} # Diccionario vacio, de lo que se mandara a la pagina
        stock_ware = self.env['stock.warehouse.orderpoint'].search([('product_id','=',values['product_id'])]) #Obtenemos el qty_multiple en caso de tener....
        product = self.env['product.product'].browse(values['product_id']).default_code #obtiene el coodigo del producto para identificarlo en traceability
        qty = 1.0
        if stock_ware:
            qty = stock_ware.qty_multiple
        
        dataProduction['accion'] = 'create'
        dataProduction['qty_multiple'] = qty
        dataProduction['product_qty'] = values['product_qty']
        dataProduction['date_planned_start'] = values['date_planned_start']
        dataProduction['product'] = product
        create = super(MrpProduction,self).create(values)
        dataProduction['name_production'] = values['name']
        dataProduction['id_bom'] = values['bom_id']
        Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,dataProduction)
        if not Api:
            raise UserError(_("Ocurrio un error al momento se generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 

        return create

    def write(self,values):
        #{'state': 'cancel', 'is_locked': True}

        if values.get('state') == 'cancel' and values.get('is_locked'):
            dataProduccion = {}
            dataProduccion['accion'] = 'unlink' # se mandara a eliminar, por que no nos servira tener el registro, si ya se encuentra en Odoo
            dataProduccion['name_production'] = self.name
            Api = self.env['trics.config.api'].RequestsHttpApi(self._inherit,dataProduccion)
            if not Api:
                raise UserError(_("Ocurrio un error al cambiar el estado a cancelado"))

        return super(MrpProduction,self).write(values)