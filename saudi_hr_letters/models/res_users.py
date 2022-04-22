# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_authorized = fields.Boolean('Is Authorized')
