# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_multi_branch = fields.Boolean("Manage multiple branches", implied_group='multi_branches.group_multi_branch',
                                        config_parameter="multi_branches.group_multi_branch")
