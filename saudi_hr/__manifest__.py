# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Middle East Human Resource",
    'summary': """ Human Resource Management """,
    'description': """
        Human Resource Management specific for middle east companies
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': ['hr_expense',
                # 'saudi_hr_groups_configuration',
                'mail', 'hr_fiscal_year', 'hr_contract',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'data/mail_channel_demo.xml',
        'views/hr_view.xml',
        'views/education.xml',
        'wizard/employee_head_count_report_view.xml',
        'wizard/employee_head_count_report_template.xml',
        'wizard/new_joining_report_view.xml',
        'wizard/new_joining_report_template.xml',
        'views/res_partner_view.xml',
        'views/hr_job_view.xml',
        'views/email_template_view.xml',
        'views/cron.xml',
        'views/res_company_view.xml',
        'menu.xml',
    ],
    'demo': [
        'demo/user_demo.xml',
        'demo/demo.xml',
        'demo/group_configuration_demo.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
