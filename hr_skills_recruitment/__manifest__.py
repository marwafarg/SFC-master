# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'HR Skills Recruitment',
    'summary': 'HR Skill Recruitment',
    'description': """
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'version': '1.0',
    'sequence': 20,
    'category': 'HR',
    'license': 'OPL-1',
    'depends': ['sync_hr_skill', 'saudi_hr_recruitment_custom'],
    'data': [
        'security/ir.model.access.csv',
        'views/email_template_view.xml',
        'views/hr_skills_recruitment_view.xml',
        'data/cron.xml',
        'data/mail_template.xml',
    ],
    'demo': [],
    'price': 0,
    'currency': "EUR",
    'installable': True,
    'auto_install': False,
}
