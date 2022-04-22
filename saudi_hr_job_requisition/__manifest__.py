# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Middle East Human Resource Job Requisition",
    'summary': """Human Resource Job Requisition""",
    'description': """
        Job requisition will be created according to job positions and here number of employees will be defined,
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': ['saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_job_requisition.xml',
        'views/hr_job_view.xml',
        'views/res_config_settings_view.xml',
        'menu.xml',
        ],
    # only loaded in demonstration mode
    'demo': ['demo/hr_applicant_demo.xml'],
    'price': 0,
    'currency': "EUR",
    'installable': True,
    'auto_install': False,
}
