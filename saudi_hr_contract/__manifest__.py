# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Middle East Human Resource contract",
    'summary': """ Employee Contract """,
    'description': """ Enhance the feature of base hr_contract module according to Middle East Human Resource. """,
    'author': "erp-bank.",
    'website': "http://www.erp-bank.com",
    'category': 'HR',
    'version': '1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': ['account',
                'hr_contract',
                'saudi_hr',
                # 'sync_hr_payroll',
                'hr_payroll',
                # 'sync_hr_payroll_account',
                'hr_payroll_account',
                # 'saudi_hr_payroll',
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/hr_payroll_data.xml',
        'data/contract_cron.xml',
        'data/contract_template.xml',
        'views/contract_view.xml',
        'report/empcontract_report_qweb.xml',
        'report/newjoin_empcontract_reportqweb.xml',
        'register_qweb_report.xml',
        'menu.xml',
    ],
    'demo': [
        'demo/demo.xml'
        ],
    'images': [],
    "price": 0.0,
    'installable': True,
    'auto_install': False,
    'application': False,
}
