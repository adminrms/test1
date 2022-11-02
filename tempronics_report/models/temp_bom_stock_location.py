from odoo import _,models, fields, api
from odoo.exceptions import UserError

from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pytz
import json
import io
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
    

class TempBomStockLocation(models.TransientModel):
    _name = "wizard.temp.bom.stock.location"
    _description = "Report MRP BOM stock location"

    location = fields.Many2many('stock.location','temp_bom_loc_rel', 'wh', 'loc', string='Location', required = True)
    bom = fields.Many2one('mrp.bom',string="BOM")
    qty_bom = fields.Integer('Qty to produce', default=1)
    bom_exclude_part = fields.Many2many('product.template')
    document_name = fields.Char('Nombre del documento')


     
    def export_xls(self):
        data = {
            'ids' : self.ids,
            'model' : self._name,
            'location' : self.location.ids,
            'bom' : self.bom.ids,
            'qty_bom' : self.qty_bom,
            'bom_exclude_part' : self.bom_exclude_part.ids,
            'document_name' : self.document_name
        }
        
        return {
            'type': 'ir.actions.report',
            'data': {
                'model' : self._name,
                'options' : json.dumps(data, default=date_utils.json_default),
                'output_format' : 'xlsx',
                'report_name' : self.document_name
            },
            'report_type': 'xlsx'
        }
    
    
    
    
    def get_totals(self,id,locations):
        total = 0
        totals = []
        product = self.env['product.product'].search([('product_tmpl_id', '=', id)])
        for location in locations:
            virtual_available = product.with_context({'location': location.id}).virtual_available
            outgoing_qty = product.with_context({'location': location.id}).outgoing_qty
            incoming_qty = product.with_context({'location': location.id}).incoming_qty
            available_qty = virtual_available + outgoing_qty - incoming_qty
            total = total + available_qty 
            totals.append(available_qty)
        totals.append(total)
        return totals

    def get_seller(self,product):
        vendorname = 'N/A'
        if(product.seller_ids):
            vendorname = product.seller_ids[0].name.name
        return vendorname

    def print_flattened_bom_lines(self, bom, requirements, sheet, row, locations, cell_style,qty_bom):
        i = row
        sheet.write(i, 0, bom.product_tmpl_id.default_code or '',cell_style)
        sheet.write(i, 1, bom.product_tmpl_id.name or '',cell_style)
        sheet.write(i, 2, qty_bom,cell_style)
        sheet.write(i, 3, bom.product_uom_id.name or '',cell_style)
        sheet.write(i, 4, bom.product_tmpl_id.standard_price or '',cell_style)
        sheet.write(i, 5, self.get_seller(bom.product_tmpl_id),cell_style)
        totals = self.get_totals(bom.product_tmpl_id.id,locations)
        sheet.write_row(i,6,totals,cell_style)
        
        #sheet.write(i, 5, bom.code or '')
        i += 1
        for product, total_qty in requirements.items():
            sheet.write(i, 0, product.default_code or '',cell_style)
            sheet.write(i, 1, product.product_tmpl_id.name or '',cell_style)
            sheet.write(i, 2, total_qty or 0.0,cell_style)
            sheet.write(i, 3, product.uom_id.name or '',cell_style)
            sheet.write(i, 4, product.product_tmpl_id.standard_price or 0.0,cell_style)
            sheet.write(i, 5, self.get_seller(product.product_tmpl_id),cell_style)
            totals = self.get_totals(product.product_tmpl_id.id,locations)
            sheet.write_row(i,6,totals,cell_style)
            i += 1
        return i

    def get_xlsx_report(self, data, response):
        locs = data['location']
        id_bom = data['bom']
        qty_bom = data['qty_bom']
        bom_exclude = data['bom_exclude_part']
        document_name = data['document_name']
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        objectBOM = self.env['mrp.bom'].browse(id_bom)

        sheet = workbook.add_worksheet(_('Flattened BOM'))
        sheet.set_landscape()
        sheet.fit_to_pages(0, 1)
        sheet.set_zoom(80)
       
            #sheet.set_column(0, i, 10)

        #sheet.set_column(0, 1, 17)
        sheet.set_column(0, 0, 17)
        sheet.set_column(1, 1, 45)
        sheet.set_column(2, 2, 8)
        sheet.set_column(3, 4, 13)
        sheet.set_column(5, 5, 40)
        sheet.set_column(6, 13, 13)

        title_style = workbook.add_format({'bold': True,
                                           'bottom': 1 ,'align': 'center','border': 1})
        cell_style = workbook.add_format({'border': 1,'align': 'center'})
        #estilo rojo
        cell_red_style = workbook.add_format({'border':1,'align':'center',
                                                'bg_color': '#FFC7CE',
                                                'font_color': '#9C0006'})
        locations = self.env['stock.location'].search([('id', 'in', locs)])
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz)
        time = pytz.utc.localize(datetime.now()).astimezone(tz)
        sheet.merge_range(0, 0, 0, 3, document_name, title_style)
        sheet.merge_range('A4:C4', 'Report Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), title_style)

        sheet_title = [
                       _('Product Reference'),
                       _('Product Name'),
                       _('Quantity'),
                       _('UM'),
                       _('Price'),
                       _('Supplier')
                       ]
        #Requisicion de Ibarra, no quiere los nombres completos de todas las demas locaciones
        #solo estas locaciones necesitan el nombre completo, por que se pueden confundir.
        namesshorts = ['WH/Input','WH/Stock','DGWH/Stock']
        for location in locations:
            name = location.display_name
            if name not in namesshorts:
                name = location.name
            sheet_title.append(_(name))

        sheet_title.append(_('Total'))
        sheet.write_row(5, 0, sheet_title, title_style)
        i = 6

        for o in objectBOM:
            # We need to calculate the totals for the BoM qty and UoM:
            starting_factor = o.product_uom_id._compute_quantity(
                o.product_qty, o.product_tmpl_id.uom_id, round=False)
            totals = self.get_flattened_totals(factor=qty_bom, ObjB = o , bom_exclude= bom_exclude)
            i = self.print_flattened_bom_lines(o, totals, sheet, i, locations, cell_style,qty_bom)

        #Se encarga de seleccionar toda el aera de las cantidades con la condicion si, el valor es < a 0 coloca el estilo rojo
        sheet.conditional_format(2,6,i,len(locations)+6,{'type':     'cell',
                                          'criteria': '<',
                                          'value':    0,
                                          'format':   cell_red_style})
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def get_flattened_totals(self, factor=1, totals=None, ObjB=None, bom_exclude = []):
        """Calculate the **unitary** product requirements of flattened BOM.
        *Unit* means that the requirements are computed for one unit of the
        default UoM of the product.
        :returns: dict: keys are components and values are aggregated quantity
        in the product default UoM.
        """
        ObjB.ensure_one()
        if totals is None:
            totals = {}
        factor /= ObjB.product_uom_id._compute_quantity(
            ObjB.product_qty, ObjB.product_tmpl_id.uom_id, round=False)
        for line in ObjB.bom_line_ids:
            sub_bom = ObjB._bom_find(product=line.product_id)
            if sub_bom and sub_bom.product_tmpl_id.id not in bom_exclude: # no quieren ver el BOM de la cadena
                new_factor = factor * line.product_uom_id._compute_quantity(
                    line.product_qty, line.product_id.uom_id, round=False)
                self.get_flattened_totals(new_factor, totals, sub_bom, bom_exclude)
            else:
                if totals.get(line.product_id):
                    totals[line.product_id] += factor * \
                        line.product_uom_id._compute_quantity(
                            line.product_qty,
                            line.product_id.uom_id,
                            round=False)
                else:
                    totals[line.product_id] = factor * \
                        line.product_uom_id._compute_quantity(
                            line.product_qty,
                            line.product_id.uom_id,
                            round=False)
        return totals