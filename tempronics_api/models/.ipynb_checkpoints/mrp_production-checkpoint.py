import requests
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
        
        dataProduction['qty_multiple'] = qty
        dataProduction['product_qty'] = values['product_qty']
        dataProduction['date_planned_start'] = values['date_planned_start']
        dataProduction['product'] = product

        create = super(MrpProduction,self).create(values)
        
        dataProduction['name_production'] = values['name'] 
        URL = 'http://204.17.62.87/api/odoo/crear_orden.php' #Pagina que hara la consulta .. Se esta viendo la posibilidad de hacer esta pagina dinamica, guardandola en la base de datos de odoo (Proximamente)
        post = requests.post(URL, data = dataProduction) #Hace la consulta por metodo POST
        result = post.json() 
        """ El valor obtenido de la pagina lo convierte a un json para poder manipuarlo mas facilmente
            en caso que el texto no este en formato para convertir, lansara un error mas grande en odoo """

        if not result['success']:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj'])) #aqui mostrar el error que ocurrio y no continuara con 
            
        
        return create
