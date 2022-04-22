# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Middle East IT Operations',
    'category': 'Human Resources',
    'description': """
    > Software and Hardware request with demage control and expense
    > Employee Registrations
    > Employee De-registrations
    > Employee Excess Card, Visiting Card Templates
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'version': '1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': [
        'base', 'hr_expense_payment', 'saudi_hr', 'hr_maintenance',
    ],
    'data': [
        'data/it_product_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # 'views/hr_it_operations.xml',
        'views/hr_employee_registration_view.xml',
        # 'views/hr_employee_deregistration_view.xml',
        'views/equipment_request_view.xml',
        'views/maintenance_views.xml',
        'menu.xml'
    ],
    'demo': [
        'data/equipment_registration_data.xml',
        'demo/equipment_request_demo.xml',
        'demo/employee_registration_demo.xml',
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
