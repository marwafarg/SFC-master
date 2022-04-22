# -*- coding: utf-8 -*-

import logging
from odoo.addons.survey.controllers.main import *

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteSurvey(WebsiteSurvey):

    # Survey start
    @http.route(['/survey/start/<model("survey.survey"):survey>',
                 '/survey/start/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def start_survey(self, survey, token=None, **post):
        super_res = super(WebsiteSurvey, self).start_survey(survey, token, **post)
        cr = request.cr
        cr.execute('SELECT id FROM survey_user_input ORDER BY id DESC LIMIT 1')
        user_input_id = cr.fetchone()[0]

        applicant_obj = request.env['hr.applicant']
        applicant_context = applicant_obj.context_data()
        if applicant_context:
            model = applicant_context.get('object', False)
            if model == 'hr.applicant':
                if applicant_context.get('active_ids', False):
                    applicant_id = applicant_context.get('active_ids', False)[0]
                    # survey_id = applicant_context.get('survey_id', False)  or survey.id
                    # request.cr.execute("UPDATE hr_applicant SET is_survey=True WHERE id = " + str(applicant_id))
                    request.cr.execute("UPDATE survey_user_input SET applicant_id=" + str(applicant_id) + " WHERE id=" + str(user_input_id))
        return super_res
