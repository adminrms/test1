# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    supplier_id = fields.Many2many('wizard.temp.report.stock.location', 'temp_supp_wiz_rel', 'wiz', 'supp', invisible=True)


class Category(models.Model):
    _inherit = 'product.category'

    obj = fields.Many2many('wizard.temp.report.stock.location', 'temp_categ_loc_rel', 'loc', 'categ', invisible=True)


class Location(models.Model):
    _inherit = 'stock.location'

    obj = fields.Many2many('wizard.temp.report.stock.location',  'temp_wh_loc_rel', 'loc', 'wh', invisible=True)
    obj_bom = fields.Many2many('wizard.temp.bom.stock.location',  'temp_bom_loc_rel', 'loc', 'wh', invisible=True)
