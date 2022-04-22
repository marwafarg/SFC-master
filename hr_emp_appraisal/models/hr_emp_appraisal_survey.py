# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SurveyInput(models.Model):
    _inherit = 'survey.user_input'

    appraisal_id = fields.Many2one('hr.emp.appraisal', string="Appriasal id")
    appraisal_plan_id = fields.Many2one('hr.emp.appraisal.plan', string="Appriasal Plan")
