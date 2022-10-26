from odoo.exceptions import UserError
from odoo import _,api, fields,models, tools

class TricsMrpBom(models.Model):
    _name="trics.mrp.bom"
    _rec_name = 'material_product_tmpl_id'
    _order = "id"
    _description = "Traceability BOMs (rutas)"
    trics_bom_id = fields.Many2one('mrp.bom',index=True,ondelete='cascade')
    material_product_tmpl_id = fields.Many2one('product.template','Product(material)',required=True)
    rxp_qty = fields.Integer('Ruta por pieza',default=1,required=True,help="Ruta por pieza")
    lotes_qty = fields.Integer('Cantidad por lote',default=1,required=True,help="Cantidad por lote")
    btn_delete = fields.Boolean("Si esta activo no se puede eliminar", default=False)



    @api.model
    def create(self,values):
        #Numero de ensamble Primario
        #Material numero de ensamble secundario
        #rxp
        #lotes
        #product = self.env['product.template']
        """
        Error en crear una ruta:
        {'rxp_qty': 1, 'lotes_qty': 580, 'material_product_tmpl_id': 728, 'trics_bom_id': 986}
        """
        create = super(TricsMrpBom,self).create(values)
        data = {}
        data['accion'] = 'create'
        data['numeroensamble'] = create.trics_bom_id.product_tmpl_id.default_code
        data['id_ensamble'] = create.trics_bom_id.product_tmpl_id.id
        data['material'] = create.material_product_tmpl_id.default_code
        data['id_material'] = create.material_product_tmpl_id.id
        data['id_bom'] = create.trics_bom_id.id
        data['rxp'] = create.rxp_qty
        data['lotes'] = create.lotes_qty
        data['id'] = create.id
        Api = self.env['trics.config.api'].RequestsHttpApi(self._name,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj']))
        return create

    def write(self,values):
        write = super(TricsMrpBom,self).write(values)
        data = {}
        data['accion'] = 'write'
        data['id'] = self.id
        data['numeroensamble'] = self.trics_bom_id.product_tmpl_id.default_code
        data['id_ensamble'] = self.trics_bom_id.product_tmpl_id.id
        data['material'] = self.material_product_tmpl_id.default_code
        data['id_material'] = self.material_product_tmpl_id.id
        data['rxp'] = self.rxp_qty
        data['lotes'] = self.lotes_qty
        Api = self.env['trics.config.api'].RequestsHttpApi(self._name,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj']))
        return write


    def unlink(self):
        unlink = super(TricsMrpBom,self).unlink()
        data = {}
        data['accion'] = 'unlink'
        data['id'] = self.id
        Api = self.env['trics.config.api'].RequestsHttpApi(self._name,data)
        if not Api:
            raise UserError(_("Ocurrio un error al momento de generarlo para traceability\n %s" % result['msj']))
        return unlink

class MrpBom(models.Model):
    _inherit = ['mrp.bom']
    trics_id = fields.One2many('trics.mrp.bom','trics_bom_id')


    def unlink(self):
        values = self.env['trics.mrp.bom'].search([('trics_bom_id','=',self.id)])
        for value in values:
            value.unlink()
        u = super(MrpBom,self).unlink()
        return u