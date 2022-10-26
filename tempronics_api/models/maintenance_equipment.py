from odoo.exceptions import UserError
from odoo import _,api, fields,models
class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    @api.model
    def create(self,values):
        
        #category = self.env['maintenance.equipment.category'].browse(values['category_id'])
        #team = self.env['maintenance.team'].browse(values['maintenance_team_id'])
        create = super(MaintenanceEquipment,self).create(values)
        if create.next_action_date:
            fechacad = create.next_action_date.strftime("%Y-%m-%d")
        else:
            fechacad = '0000-00-00'

        dataEquipment = {} # Diccionario vacio, de lo que se mandara a la pagina
        
        dataEquipment['accion'] = 'create'
        dataEquipment['id_equip'] = create.id
        dataEquipment['fecha_cad'] = fechacad
        dataEquipment['descripcion'] = create.name
        dataEquipment['categoria'] = create.category_id.name
        dataEquipment['grupo'] = create.maintenance_team_id.name
        dataEquipment['fecha_asig'] = create.assign_date.strftime("%Y-%m-%d")
        dataEquipment['notas'] = create.note
        dataEquipment['vendedor_ref'] = create.partner_ref
        dataEquipment['modelo'] = create.model
        dataEquipment['serial'] = create.serial_no
        dataEquipment['serial_interno'] = create.x_internal_serial
        #raise UserError(_("--Debug message--\n %s" % dataEquipment + "\n--End message--"))
        
        Api = self.env['trics.config.api']
        Api.RequestsHttpApi(self._inherit,Api.jsonconvert(dataEquipment))

        return create

    def write(self,values):

        write = super(MaintenanceEquipment,self).write(values)

        dataEquipment = {} # Diccionario vacio, de lo que se mandara a la pagina
        
        dataEquipment['accion'] = 'write'
        dataEquipment['descripcion'] = self.name
        dataEquipment['categoria'] = self.category_id.name
        dataEquipment['grupo'] = self.maintenance_team_id.name
        dataEquipment['fecha_asig'] = self.assign_date.strftime("%Y-%m-%d")
        dataEquipment['notas'] = self.note
        dataEquipment['vendedor_ref'] = self.partner_ref or 'N/A'
        dataEquipment['modelo'] = self.model or 'N/A'
        dataEquipment['serial'] = self.serial_no or 'N/A'
        dataEquipment['serial_interno'] = self.x_internal_serial
        dataEquipment['id_equip'] = self.id
        if self.next_action_date:
            dataEquipment['fecha_cad'] = self.next_action_date.strftime("%Y-%m-%d")
        else:
            dataEquipment['fecha_cad'] = '0000-00-00'

        dataEquipment['active'] = 0
        if not self.active:
            dataEquipment['active'] = 1
        

        Api = self.env['trics.config.api']
        Api.RequestsHttpApi(self._inherit,Api.jsonconvert(dataEquipment))


        return write


    def unlink(self):
        dataEquipment = {}
        dataEquipment['accion'] = 'unlink'
        dataEquipment['id_equip'] = self.id
        Api = self.env['trics.config.api']
        Api.RequestsHttpApi(self._inherit,Api.jsonconvert(dataEquipment))
        return super(MaintenanceEquipment,self).unlink()


    def sync_data_api(self):
        #sincronizar todo
        maintenance = self.env['maintenance.equipment'].search([('active','=',True)])
        DataSet = {}
        DataSet['accion'] = 'sync'
        Data = []
        for equipment in maintenance:
            dataEquipment = {}
            dataEquipment['descripcion'] = equipment.name
            dataEquipment['categoria'] = equipment.category_id.name
            dataEquipment['grupo'] = equipment.maintenance_team_id.name
            dataEquipment['fecha_asig'] = equipment.assign_date.strftime("%Y-%m-%d")
            dataEquipment['notas'] = equipment.note
            dataEquipment['vendedor_ref'] = equipment.partner_ref or 'N/A'
            dataEquipment['modelo'] = equipment.model or 'N/A'
            dataEquipment['serial'] = equipment.serial_no or 'N/A'
            dataEquipment['serial_interno'] = equipment.x_internal_serial
            dataEquipment['id_equip'] = equipment.id
            if equipment.next_action_date:
                dataEquipment['fecha_cad'] = equipment.next_action_date.strftime("%Y-%m-%d")
            else:
                dataEquipment['fecha_cad'] = '0000-00-00'
            dataEquipment['active'] = 0
            if not equipment.active:
                dataEquipment['active'] = 1
            Data.append(dataEquipment)
            
        DataSet['Data'] = Data

        Api = self.env['trics.config.api']
        Api.RequestsHttpApi(self._inherit,Api.jsonconvert(DataSet))

