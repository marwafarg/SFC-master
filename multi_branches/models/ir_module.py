# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, modules, tools, _


class Module(models.Model):
    _inherit = "ir.module.module"

    def button_install(self):
        for module in self:
            if 'saudi' in module.name:
                return False
        return super(Module, self).button_install()

    def button_immediate_install(self):
        for module in self:
            if 'saudi' in module.name:
                return False
        return super(Module, self).button_immediate_install()
