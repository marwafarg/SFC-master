# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Employee Appraisal',
    'summary': """ Roll out appraisal plans and get the best of your workforce """,
    'description': """ Roll out appraisal plans and get the best of your workforce """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'summary': 'HR Employee Appraisal',
    'depends': ['base', 'saudi_hr', 'survey'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/mail_template.xml',
        'data/cron.xml',
        'views/hr_emp_appraisal.xml',
        'views/hr_emp_appraisal_survey.xml',
    ],
    'demo': ['demo/demo.xml'],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
