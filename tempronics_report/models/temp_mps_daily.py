from odoo import _,models,fields, api
from odoo.exceptions import UserError

from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
import pytz
import json
import io
import string
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class  TempMpsDaily(models.TransientModel):
    _name = "wizard.temp.mrps.daily"
    _description = "Report MRS Daily"


    product_id = fields.Many2one('product.product')
    date_from = fields.Date('Date From')
    date_to= fields.Date('Date To')
    document_name = fields.Char('Nombre del documento')

     
    def export_xls(self):
        saleOrders = self.get_sales(self.date_from,self.date_to,self.product_id.ids)
        data = {
            'ids' : self.ids,
            'model' : self._name,
            'product_id' : self.product_id,
            'date_from' : self.date_from,
            'date_to' : self.date_to,
            'document_name' : self.document_name,
            'sale_orders' : saleOrders
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


    def get_sales(self,d_from,d_to,p_ids):
        so = self.env['sale.order.line'].search([('commitment_date','>=',d_from),('commitment_date','<=',d_to),('order_id.state','=','sale'),('display_type','=',False)],order="order_id desc,name asc ")
        if p_ids:
            so = so.search([('commitment_date','>=',d_from),('commitment_date','<=',d_to),('product_id','in',p_ids),('order_id.state','=','sale'),('display_type','=',False)],order="order_id desc,name asc ")
        return so.ids

    def GetColExcel(self,Col):
        Abc = list(string.ascii_uppercase)
        LenAbc = len(Abc)
        if Col >= LenAbc:
            x = int((Col / LenAbc) - 1)
            y = Col % LenAbc
            letra = Abc[x] + Abc[y] #Llega a romperse en la secuencia ZZ -> AAA Numpero maximo de columnas 702
        else: 
            letra = Abc[Col]
        return letra

    def getweekend(self,date):
        date = datetime.strptime(date,'%Y-%m-%d')
        d = 5 - date.isoweekday()
        r = date + timedelta(days=d)
        return str(r.date())



    def rangeDate(self,date_from,date_to,week_days,col):
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        days_between = date_to - date_from
        TitlesDates = []
        Dates = {}
        Data = {}
        for i in range(days_between.days+1):
            new_day = date_from + timedelta(days=i)
            if new_day.isoweekday() == 5:
                iso = new_day.isocalendar()
                week = iso[1]
                if str(new_day.date()) not in Dates:
                    strweek =  'W-' + str(week)
                    TitlesDates.append(strweek)
                    Dates[str(new_day.date())] = col
                    col += 1
        Data['Dates'] = Dates
        Data['TitlesDates'] = TitlesDates
        return Data

    def CreateDic(self,objOrders):
        """
        -Orden #1
            -Product #
                -Fecha -- Solo Viernes 
                    - Qty
                -Fecha
                    - Qty
            -Product #
                -Fecha
                    - Qty
        -Orden #2
            -Product #
                -Fecha
                    - Qty
        """
        OrderData = {}
        for order in objOrders:
            strDate = str(order.commitment_date.date())
            weekend = self.getweekend(strDate)
            
            Product = {}
            DateAux = {}
            if order.order_id.name in OrderData: #verificamos si existe orden
                Product = OrderData[order.order_id.name]
                if order.product_id.id in Product: #Verificamos si existe ya el producto en product
                    DateAux = Product[order.product_id.id]['Dates']
                    if weekend in DateAux:
                        #Ya existe la fecha en el producto actual
                        #obtenemos la cantidad que tenga y la sumamos
                        DateAux[weekend] += order.product_uom_qty
                    else:
                        #Si no existe la creamos con su cantidad actual
                        DateAux[weekend] = order.product_uom_qty
                    Product[order.product_id.id]['Dates'] = DateAux
                else:
                    DateAux = {weekend : order.product_uom_qty }
                    Product[order.product_id.id] = {'product':order.product_id.default_code, 'Dates': DateAux ,'Obj':order}
            else:
                DateAux = {weekend : order.product_uom_qty }
                Product[order.product_id.id] = {'product':order.product_id.default_code, 'Dates': DateAux ,'Obj':order}
                
            OrderData[order.order_id.name] = Product
        

        return OrderData

    def get_xlsx_report(self, data, response):
        idsSale = data['sale_orders']
        saleOrders = self.env['sale.order.line'].browse(idsSale)
        document_name = data['document_name']
        date_from = data['date_from']
        date_to = data['date_to']
        sheet_title = ['No.','Part No.','Description','SO #','Qty']
        weekdays = 5
        DataDates = self.rangeDate(date_from,date_to,weekdays,len(sheet_title)+1)
        arrDate = DataDates['TitlesDates']
        ColDates = DataDates['Dates']
        sheet_title = sheet_title + list(ColDates)
        row = 6
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(_('MPS'))

        title_style = workbook.add_format({ 
                                            'bold': True,
                                            'border': 1,
                                            'align': 'left',
                                            'font_size': 14
                                         })

        title_table_style = workbook.add_format({
                                                    'border': 1,
                                                    'bold': True,
                                                    'align': 'center',
                                                    'font_size': 12    
                                                })

        title_table_date_format_style = workbook.add_format({
                                                    'border': 1,
                                                    'bold': True,
                                                    'align': 'center',
                                                    'font_size': 12    
                                                })
                                                

        info_table_style = workbook.add_format({
                                                    'border': 1,
                                                    'font_size': 11    
                                                })

        info_table_center_style = workbook.add_format({
                                                    'border': 1,
                                                    'align': 'center',
                                                    'font_size': 11 
                                                })

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 6)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 40)
        sheet.set_column(4, 4, 8)
        sheet.set_column(5, 5, 8)
        sheet.set_zoom(80)
        sheet.set_column(6, len(sheet_title), 13)
        sheet.freeze_panes(6,6)


        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz)
        time = pytz.utc.localize(datetime.now()).astimezone(tz)

        sheet.write(1,1,document_name,title_style)
        sheet.write(2,1,'Report Date: '+ str(time.strftime("%Y-%m-%d %H:%M %p")),title_style)

        
        sheet.write_row(5, 1, sheet_title, title_table_style)
        sheet.write_row(4, 6, arrDate,title_table_style)
        DataOrders = self.CreateDic(saleOrders)
        
        MaxCol = self.GetColExcel(len(sheet_title))

        for okey,products in DataOrders.items(): #Nivel orden
            for lkey,line in products.items(): #Nivel Producto
                #pintar los cuadros vacios
                for y in range(len(sheet_title)):
                    sheet.write(row,y+1,None,info_table_center_style)
                sheet.write(row,1,row-5,info_table_center_style)
                sheet.write(row,2,line['product'],info_table_center_style)
                sheet.write(row,3,line['Obj'].product_id.name,info_table_style)
                sheet.write(row,4,okey,info_table_center_style)
                #sheet.write(row,5,0.0,info_table_center_style)
                strSuma = '=SUM(G'+str(row+1)+':'+MaxCol+str(row+1)+')'
                sheet.write_formula(row,5,strSuma,info_table_center_style)
                #com_date = str(line['Obj'].commitment_date.date())
                for fecha,qty in line['Dates'].items():
                    sheet.write(row,ColDates[fecha],qty,info_table_center_style)
                row += 1
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()