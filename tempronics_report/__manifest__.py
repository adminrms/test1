{
    'name': 'Tempronics Reports',
    'version': '12.0.0.0.0',
    'category': 'Warehouse',
    'summary': 'Direct access to Tempronics reports',
    'author': "Jose Monroy",
    'website': 'https://www.tempronics.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mrp',
        'product',
        'stock',
        'report_xlsx',
        'mail',
        'contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/tempronics_report_views.xml',
        'wizard/wizard_temp_report_stock_location_view.xml',
        'wizard/wizard_temp_report_bom_location_view.xml',
        'wizard/wizard_temp_report_mps_view.xml',
        'data/email_template_report_stock_month.xml',
        'data/email_template_inventory_adjustment.xml',
    ],
    'application': True,
}

