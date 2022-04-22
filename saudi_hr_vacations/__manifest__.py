# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Middle East HR Vacations",
    'summary': """ Human Resource Management """,
    'description': """
        Human Resource Management Vacations
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': ['saudi_hr_leaves_management', 'saudi_hr_visa', 'sync_employee_advance_salary','saudi_hr_flight_book'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'view/res_config_view.xml',
        'view/hr_vacations_view.xml',
        'wizard/change_date_wizard_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
