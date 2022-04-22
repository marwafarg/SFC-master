# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class ResCountry(models.Model):
    _inherit = 'res.country'

    arabic_country_name = fields.Char('Arabic Name', size=50)
