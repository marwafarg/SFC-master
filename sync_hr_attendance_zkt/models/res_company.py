# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    biotime_id = fields.Integer('BioTime ID')
