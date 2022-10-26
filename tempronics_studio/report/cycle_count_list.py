from odoo import _,models
from datetime import datetime
from random import sample
import pytz


class CycleCountList(models.AbstractModel):
    _name = 'report.tempronics_studio.cycle_count_list'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, lines):
        location = data['location']
        sheet = workbook.add_worksheet('Cycle Count List')
        format_title = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8_border = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_border.set_border()



        format_title.set_align('center')
        format_title.set_border()
        sheet.set_zoom(80)

        sheet.merge_range(0, 0, 0, 3, "Cycle Count List", format_title)

        
        tz = pytz.timezone('US/Arizona')
        time = pytz.utc.localize(datetime.now()).astimezone(tz)
        sheet.merge_range('A4:G4', 'List Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format_title)
        
        sheet.merge_range('A5:J5', 'Product Information', format_title)
        w_col_no = 8
        w_col_no1 = 8
        

        location = self.env['stock.location'].search([('id', '=', location)])
        sheet_title = [
            _('SKU'),
            _('Name'),
            _('Category'),
            _('Classification'),
            _('UM'),
            _(location.display_name)

        ]

        sheet.write_row(5, 0, sheet_title, format_title)
        prod_row = 6
        for product in self.GetData(location):
            sheet.write(prod_row, 0, product['sku'], font_size_8_border)
            sheet.write(prod_row,1, product['name'], font_size_8_border)
            sheet.write(prod_row,2, product['category'], font_size_8_border)
            sheet.write(prod_row,3, product['classification'], font_size_8_border)
            sheet.write(prod_row,4, product['um'], font_size_8_border)
            sheet.write(prod_row,5, product['stock'], font_size_8_border)

            prod_row = prod_row + 1

        #sheet.write(5,count+2,'Reserved',format21)
        #sheet.write(5,count+3,'BAL',format21)
        sheet.set_column(1, 1, 42)
        sheet.set_column(2, 2, 14)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 6)
        sheet.set_column(5, 5, 10)

    def GetData(self,location):
        #buscamos todas las clasificaciones
        classifications = self.env['product.classification'].search([])
        lines = []
        for classification in classifications:
            productsforclass = self.env['product.template'].search([('product_classification','=',classification.id)])
            percent = (classification.percent / 100) 
            percentClass = int(len(productsforclass.ids) * percent)

            MuestraClass = sample(productsforclass.ids,percentClass)

            productsSample = self.env['product.template'].browse(MuestraClass)

            for product in productsSample:
                vals = {
                    'sku': product.default_code,
                    'name': product.name,
                    'category': product.categ_id.name,
                    'classification': product.product_classification.name,
                    'um': product.uom_id.name,
                    'stock': self.getStock(product,location)
                }
                lines.append(vals)
            
        return lines

    def getStock(self,product,location):
        virtual_available = product.with_context({'location': location.id}).virtual_available
        outgoing_qty = product.with_context({'location': location.id}).outgoing_qty
        incoming_qty = product.with_context({'location': location.id}).incoming_qty
        available_qty = virtual_available + outgoing_qty - incoming_qty
        return available_qty
    

        