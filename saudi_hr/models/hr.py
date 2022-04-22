# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.osv import expression



class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    certificate_id = fields.Many2one('education.certificate', string='Certificate Level', groups="hr.group_hr_user", tracking=True)
    study_id = fields.Many2one('education.study', string='Field of Study', groups="hr.group_hr_user", tracking=True)
    school_id = fields.Many2one('education.school', string='School', groups="hr.group_hr_user", tracking=True)

    city = fields.Char()
    building_no = fields.Char(string="Building no",help="Building No")
    district = fields.Char(string="District",  help="District")
    additional_no = fields.Char(string="Additional no", help="Additional No")
    street = fields.Char()
    zip = fields.Char()

    @api.depends('birthday')
    def _get_age(self):
        """
            Calculate age of Employee depends on Birth date.
        """
        for employee in self:
            if employee.sudo().birthday:
                employee.age = relativedelta(
                    fields.Date.from_string(fields.Date.today()),
                    fields.Date.from_string(employee.sudo().birthday)).years
            else:
                employee.age = 0

    # @api.onchange('department_id')
    # def _onchange_department(self):
    #     if self.department_id:
    #         self.job_id = False
    #     self.coach_id = self.department_id.manager_id
    #     return super(HrEmployee, self)._onchange_department()

    @api.constrains('birthday')
    def _check_birthday(self):
        """
            check the Employee age, eligible for doing a job or not.
            If Gender is male, He is age greater than 18.
            If Gender is female, She is age greater than 21.
        """
        for employee in self:
            if employee.birthday and employee.gender:
                diff = relativedelta(datetime.today(), datetime.strptime(str(employee.birthday), DEFAULT_SERVER_DATE_FORMAT))
                if employee.gender == "male" and abs(diff.years) < 18:
                    raise ValidationError(_("Male employee's age must be greater than 18"))
                elif employee.gender == 'female' and abs(diff.years) < 21:
                    raise ValidationError(_("Female Employee's age must be greater than 21."))

    @api.depends('date_of_join', 'date_of_leave')
    def _get_months(self):
        """
            Calculating Duration depends on `Date of Join`, `Date of Leave`
        """
        for employee in self:
            if employee.date_of_join:
                try:
                    join_date = datetime.strptime(str(employee.date_of_join), DEFAULT_SERVER_DATE_FORMAT)
                    to_date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
                    current_date = datetime.strptime(str(to_date), DEFAULT_SERVER_DATE_FORMAT)
                    employee.duration_in_months = (current_date.year - join_date.year) * 12 + current_date.month - join_date.month
                except:
                    employee.duration_in_months = 0.0
            else:
                employee.duration_in_months = 0.0

    @api.model
    def get_employee(self):
        """
            Get Employee record depends on current user.
        """
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return employee_ids[0] if employee_ids else False

    # ================Fields of HR employee=======================
    arabic_name = fields.Char('Arabic Name', size=120)
    date_of_join = fields.Date('Joining Date', track_visibility='onchange')
    date_of_leave = fields.Date('Leaving Date')
    employee_status = fields.Selection([('active', 'Employment/Active'),
                                        ('inactive', 'Inactive'),
                                        ('long_term_secondment', 'Long Term Secondment'),
                                        ('probation', 'Probation'),
                                        ('notice_period', 'Notice Period'),
                                        ('terminate', 'Terminated/Inactive')
                                        ], string='Employment Status', default='active', track_visibility='onchange')
    middle_name = fields.Char(size=64, string='Middle Name')
    last_name = fields.Char(size=64, string='Last Name')
    code = fields.Char(string='Code')
    age = fields.Float(compute='_get_age', compute_sudo=True, string="Age", store=False, readonly=True)
    religion = fields.Selection([('muslim', 'Muslim'), ('non-muslim', 'Non Muslim')], 'Religion')
    spouse_number = fields.Char('Spouse Phone Number', size=32)
    is_saudi = fields.Boolean('Is Saudi')
    branch_id = fields.Many2one('res.branch', 'Office', track_visibility='onchange')
    ksa_address_id = fields.Many2one('res.partner', 'Address in KSA')
    duration_in_months = fields.Float(compute='_get_months', string='Month(s) in Organization')
    total_service_year = fields.Char(compute='_get_service_year', string="Total Service Year")
    service_year = fields.Integer(compute='_get_service_year', string="Service Year",store=True)
    is_hod = fields.Boolean('Is HOD', help='Head of Department')
    manager = fields.Boolean(string='Is a Manager')
    profession = fields.Char(string='Profession')
    nominee_id = fields.Many2one('res.partner', 'Name of Nominee', track_visibility='onchange')
    sponsored_by = fields.Selection([('company', 'Company'), ('other', 'Other')], string='Sponsored By',
                                    default="company")
    reference_by = fields.Char(string='Reference By')
    iqama_number = fields.Char()
    country_code = fields.Char(related='country_id.code')

    _sql_constraints = [
        ('unique_emp_code', 'unique(code)', 'Employee Code must be unique!'),
    ]
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)



    @api.constrains('iqama_number','identification_id')
    def _onchange_id_iqama(self):
        for rec in self:
            if rec.iqama_number !=False :
                if list(rec.iqama_number)[0] !='2':
                    raise ValidationError(_('Please start Iqama NO by number 2'))

            if rec.identification_id !=False:
                if  list(rec.identification_id)[0] !='1':
                   raise ValidationError(_('Please start Identification NO by number 1'))


    @api.onchange('date_of_leave')
    def onchange_leave_date(self):
        """
            CHeck the Date of Leave must greater than Date of Join
        """
        warning = {}
        if self.date_of_leave and self.date_of_join and self.date_of_leave < self.date_of_join:
            warning.update({
                'title': _('Information'),
                'message': _("Leaving Date Must Be Greater Than Joining Date.")})
            self.date_of_leave = False
        return {'warning': warning}

    @api.depends('date_of_join')
    def _get_service_year(self):
        """
            Calculate the total no of years, total no of months.
        """
        for rec in self:
            if rec.date_of_join and datetime.strptime(str(rec.date_of_join),
                                                      DEFAULT_SERVER_DATE_FORMAT) < datetime.strptime(
                    str(datetime.today().date().strftime(DEFAULT_SERVER_DATE_FORMAT)), DEFAULT_SERVER_DATE_FORMAT):
                if rec.date_of_leave:
                    diff = relativedelta(datetime.strptime(str(rec.date_of_leave), DEFAULT_SERVER_DATE_FORMAT),
                                         datetime.strptime(str(rec.date_of_join), DEFAULT_SERVER_DATE_FORMAT))
                else:
                    diff = relativedelta(datetime.today(),
                                         datetime.strptime(str(rec.date_of_join), DEFAULT_SERVER_DATE_FORMAT))
                rec.total_service_year = " ".join([str(diff.years), 'Years', str(diff.months), "Months"])
                rec.service_year = diff.years

            else:
                rec.total_service_year = "0 Years 0 Months"
                rec.service_year = 0



    @api.depends('name', 'middle_name', 'last_name')
    def name_get(self):
        """
            Generate the single string for Name
            for eg. name: John, MiddleName: Pittu, LastName: Rank
            Calculated Name: John Pittu Rank
        """
        res = []
        for employee in self:
            name = employee.name
            name = ' '.join([name or '', employee.middle_name or '', employee.last_name or ''])
            res.append((employee.id, name))
        return res

    @api.model
    def age_notification(self):
        template_id = self.env.ref('saudi_hr.notification_employee_retirement', False)
        employees = []
        if template_id:
            for manager in self.env['hr.groups.configuration'].search([('hr_ids', '!=', False)]):
                for employee in self.env['hr.employee'].search([('branch_id', '=', manager.branch_id.id)]):
                    diff = relativedelta(datetime.today(), datetime.strptime(str(employee.birthday), DEFAULT_SERVER_DATE_FORMAT))
                    if diff and diff.years == 59 and diff.months == 6:
                        employees.append(employee.name)
                        if employee.code:
                            employees.append(employee.code)
                emp = ',\n'.join(employees)
                for hr in manager.hr_ids:
                    template_id.with_context(employees=emp).send_mail(hr.id, force_send=True, raise_exception=True)

    @api.model
    def create(self, values):
        """
            Create a new record.
        """
        # values['code'] = self.env['ir.sequence'].next_by_code('hr.employee')
        if values.get('country_id', False):
            country = self.env['res.country'].browse(values['country_id'])
            if country.code == 'SA':
                values.update({'is_saudi': True})
            else:
                values.update({'is_saudi': False})
        return super(HrEmployee, self).create(values)

    # def write(self, values):
    #     """
    #         update a record
    #     """
    #     if values.get('user_id', False):
    #         rec = self.user_id.write({'employee_id': self.ids and self.ids[0] or False})
    #     return super(HrEmployee, self).write(values)

    @api.onchange('company_id')
    def onchange_company(self):
        """
            set branch false
        """
        self.branch_id = False

    @api.onchange('country_id')
    def onchange_country(self):
        """
            Check Nationality is Saudi, If True, update value of is_saudi
        """
        if self.country_id and self.country_id.code == 'SA':
            self.is_saudi = True
        else:
            self.is_saudi = False
