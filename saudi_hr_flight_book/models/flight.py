# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

booking_states = [('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('validate', 'Approved'), ('validate1', 'Approved by HOF'),
                  ('in_progress', 'In Progress'), ('received', 'Received'), ('refuse', 'Refused')]


class FlightBooking(models.Model):
    _name = 'flight.booking'
    _order = 'id desc'
    _inherit = ['mail.thread', 'hr.expense.payment']
    _description = "Flight Booking"

    def _track_subtype(self, init_values):
        """
            Give the subtypes triggered by the changes on the record according
            to values that have been updated.
        """
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('hr_flight_book.mt_flight_booking_new')
        elif 'state' in init_values and self.state == 'confirm':
            return self.env.ref('hr_flight_book.mt_flight_booking_confirm')
        elif 'state' in init_values and self.state == 'validate':
            return self.env.ref('hr_flight_book.mt_flight_booking_validate')
        elif 'state' in init_values and self.state == 'received':
            return self.env.ref('hr_flight_book.mt_flight_booking_receive')
        elif 'state' in init_values and self.state == 'refuse':
            return self.env.ref('hr_flight_book.mt_flight_booking_cancel')
        return super(FlightBooking, self)._track_subtype(init_values)

    state = fields.Selection(booking_states, string='Status', default='draft')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    job_id = fields.Many2one('hr.job', string='Job Position', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    branch_id = fields.Many2one('res.branch', 'Office', readonly=True)
    type = fields.Selection([('single', 'One Way'),
                            ('return', 'Round Trip')], required=True, string='Type', default='single')
    departure_date = fields.Date(string='Preferred Start Date', required=True, default=datetime.strftime(datetime.now(), '%Y-%m-%d'),
                                 )
    arrival_date = fields.Date(string='Preferred End Date')
    expense_total = fields.Float(string='Total Expense', digits='Account')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    source = fields.Char(string='Leaving From', required=True)
    destination = fields.Char(string='Going To', required=True)
    seats = fields.Integer(string='No. of Seats', required=True, default=1)
    booking_lines = fields.One2many('flight.booking.line', 'booking_id', string='Booking Lines')
    group_member_ids = fields.One2many('group.member', 'booking_id', string='Group Member')
    reason = fields.Selection([('internal', 'Internal Meeting'), ('client_related', 'Client Related'),
                               ('for_business', 'Business Development'), ('visa_related', 'Visa Related'),
                               ('training', 'Training'), ('personal', 'Personal'), ('annual_ticket', 'Annual Ticket'),
                               ('others', 'Others')], required=True, string='Purpose of Travel', default='internal')
    ticket_type = fields.Selection([('single', 'Single'),
                                   ('group', 'Group'),
                                   ('family', 'Family')], required=True, string='Ticket type', default='single')
    approved_date = fields.Datetime(string='Approved Date', readonly=True, track_visibility='onchange', copy=False)
    approved_by = fields.Many2one('res.users', string='Approved by', readonly=True, track_visibility='onchange', copy=False)
    description = fields.Text(string='Description', required=True)
    po_number = fields.Char(string='PO Number')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    expense_ids = fields.Many2many('hr.expense', string="Expenses", copy=False)

    @api.model
    def create(self, values):
        """
            Create a new record
            :return: Newly created record ID
        """
        partner = []
        if values.get('employee_id'):
            employee_obj = self.env['hr.employee'].browse(values['employee_id'])
            values.update({'job_id': employee_obj.job_id.id,
                           'department_id': employee_obj.department_id.id,
                           'company_id': employee_obj.company_id.id,
                           'branch_id': employee_obj.branch_id.id,
                           })
        return super(FlightBooking, self).create(values)

    def write(self, values):
        """
            Update an existing record.
            :param values:
            :return: Current update record ID
        """
        partner = []
        if values.get('employee_id'):
            employee_obj = self.env['hr.employee'].browse(values['employee_id'])
            values.update({'job_id': employee_obj.job_id.id,
                           'department_id': employee_obj.department_id.id,
                           'company_id': employee_obj.company_id.id,
                           'branch_id': employee_obj.branch_id.id,
                           })
            if employee_obj.user_id:
                partner.append(employee_obj.user_id.partner_id.id)
            if employee_obj.parent_id.user_id:
                partner.append(employee_obj.parent_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner)
        return super(FlightBooking, self).write(values)

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for booking in self:
            if booking.state not in ['draft']:
                raise UserError(_('You cannot remove the record which is not in draft state!'))
        return super(FlightBooking, self).unlink()

    @api.depends('employee_id', 'departure_date', 'arrival_date')
    def name_get(self):
        """
            return name of employee with departure_date and arrival_date
        """
        res = []
        for booking in self:
            name = booking.employee_id.name or ''
            if booking.arrival_date:
                name = ''.join([name, ' ( ', str(booking.departure_date), str(booking.arrival_date) and ' to ' or '', str(booking.arrival_date) or '', ' )'])
            else:
                name = ''.join([name, ' ( ', str(booking.departure_date), ' )'])
            res.append((booking.id, name))
        return res

    @api.onchange('type')
    def onchange_type(self):
        """
            onchange the value based on selected type
            Set arrival_date False
        """
        self.arrival_date = False

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee
            Set employee code, job, department, branch, ticket type and family members according to employee.
        """
        # self.employee_code = ''
        self.job_id = False
        self.department_id = False
        self.branch_id = False
        # self.family_member_ids = False
        self.branch_id = False
        if self.employee_id:
            self.job_id = self.employee_id.job_id and self.employee_id.job_id.id
            self.department_id = self.employee_id.department_id and self.employee_id.department_id.id
            self.company_id = self.employee_id.company_id and self.employee_id.company_id.id
            self.branch_id = self.employee_id.branch_id and self.employee_id.branch_id.id
            # self.family_member_ids = False

    def _add_followers(self):
        """
            Add employee and manager in followers
        """
        admin_groups_config_ids = self.env['hr.groups.configuration'].sudo().search([('branch_id', '=', self.employee_id.branch_id.id), ('admin_ids', '!=', False)])
        partner_ids = admin_groups_config_ids and [employee.user_id.partner_id.id for employee in admin_groups_config_ids.admin_ids if employee.user_id] or []
        partner_ids.append(self.employee_id.user_id.partner_id.id)
        if self.employee_id.sudo().parent_id.user_id:
            partner_ids.append(self.employee_id.sudo().parent_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def flight_booking_confirm(self):
        """
            Change state to confirm and send message to employee for flight confirmation.
            :return: True
        """
        self.ensure_one()
        if self.ticket_type == 'group' or self.ticket_type == 'family':
            if not self.group_member_ids:
                raise UserError(_("Please add Group Member Details first !"))
        self._add_followers()
        self.state = 'confirm'
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Booking Confirmed.'))

    def flight_booking_validate(self):
        """
            Change state to validate and send message to employee.
            :return: True
        """
        self.ensure_one()
        for record in self:
            if record.supplier_id:
                self.message_subscribe(partner_ids=[record.supplier_id.id])
        self.write({'state': 'validate',
                    'approved_by': self.env.user.id,
                    'approved_date': datetime.today()})
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Booking Approved.'))

    def flight_booking_inprogress(self):
        """
            Change state to in progress and send message to employee.
            :return: True
        """
        self.ensure_one()
        for record in self:
            if record.supplier_id:
                self.message_subscribe(partner_ids=[record.supplier_id.id])
        self.state = 'in_progress'
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Booking In Progress.'))

    def ticket_received(self):
        """
            Change state to received and set total expense and company contribution.
            :return: True
        """
        self.ensure_one()
        booking = self
        if not booking.booking_lines:
            raise UserError(_('Please add Ticket Details first !'))
        expense = 0.0
        company_expense = self.company_contribution
        emp_expense = self.emp_contribution
        used_amount = 0.0

        for book in booking.booking_lines:
            if book.invoice_amount <= 0:
                raise UserError(_('Invoice Amount should be greater then 0'))
            expense = book.invoice_amount + expense

            if booking.reason == 'annual_ticket':
                annual_ticket_id = self.env['annual.ticket.detail'].search(
                    [('employee_id', '=', booking.employee_id.id), ('year_id.code', '=', book.travel_date.year)])
                if annual_ticket_id and book.member_type == 'adult':
                    ticket_status_ids = self.env['annual.ticket.status'].search_count(
                        [('ticket_detail_id', '=', annual_ticket_id.id),
                         ('member_type', '=', 'adult'),
                         ('ticket_status', '=', 'used')])
                    if ticket_status_ids < annual_ticket_id.adults:
                        if annual_ticket_id.adult_fare > 0 and book.invoice_amount < (
                                annual_ticket_id.adult_fare / annual_ticket_id.adults):
                            company_expense += book.invoice_amount
                            used_amount = book.invoice_amount
                        else:
                            company_expense += (annual_ticket_id.adult_fare / annual_ticket_id.adults)
                            emp_expense += (book.invoice_amount - annual_ticket_id.adult_fare / annual_ticket_id.adults)
                            used_amount = annual_ticket_id.adult_fare / annual_ticket_id.adults
                        self.env['annual.ticket.status'].create({'ticket_detail_id': annual_ticket_id.id,
                                                                 'member_type': book.member_type,
                                                                 'ticket_status': 'used',
                                                                 'used_amount': used_amount
                                                                 })
                elif annual_ticket_id and book.member_type == 'child':
                    ticket_status_ids = self.env['annual.ticket.status'].search_count(
                        [('ticket_detail_id', '=', annual_ticket_id.id), ('member_type', '=', 'child'),
                         ('ticket_status', '=', 'used')])
                    if ticket_status_ids < annual_ticket_id.children:
                        if annual_ticket_id.child_fare > 0 and book.invoice_amount < (
                                annual_ticket_id.child_fare / annual_ticket_id.children):
                            company_expense += book.invoice_amount
                            used_amount = book.invoice_amount
                        else:
                            company_expense += annual_ticket_id.child_fare / annual_ticket_id.children
                            emp_expense += (
                                        book.invoice_amount - annual_ticket_id.child_fare / annual_ticket_id.children)
                            used_amount = annual_ticket_id.child_fare / annual_ticket_id.children
                        self.env['annual.ticket.status'].create({'ticket_detail_id': annual_ticket_id.id,
                                                                 'member_type': book.member_type,
                                                                 'ticket_status': 'used',
                                                                 'used_amount': used_amount
                                                                 })
                elif annual_ticket_id and book.member_type == 'infant':
                    ticket_status_ids = self.env['annual.ticket.status'].search_count(
                        [('ticket_detail_id', '=', annual_ticket_id.id), ('member_type', '=', 'infant'),
                         ('ticket_status', '=', 'used')])
                    if ticket_status_ids < annual_ticket_id.infant:
                        if annual_ticket_id.infant_fare > 0 and book.invoice_amount < (
                                annual_ticket_id.infant_fare / annual_ticket_id.infant):
                            company_expense += book.invoice_amount
                            used_amount = book.invoice_amount
                        else:
                            company_expense += (annual_ticket_id.infant_fare / annual_ticket_id.infant)
                            emp_expense += (
                                        book.invoice_amount - annual_ticket_id.infant_fare / annual_ticket_id.infant)
                            used_amount = annual_ticket_id.infant_fare / annual_ticket_id.infant
                        self.env['annual.ticket.status'].create({'ticket_detail_id': annual_ticket_id.id,
                                                                 'member_type': book.member_type,
                                                                 'ticket_status': 'used',
                                                                 'used_amount': used_amount
                                                                 })
            booking.emp_contribution = emp_expense
            if booking.emp_contribution > 0:
                booking.payment_mode = 'both'
            booking.company_contribution = company_expense
            booking.expense_total = emp_expense + company_expense

        self.state = 'received'
        self.expense_total = expense

    def flight_booking_refuse(self):
        """
            Change state to refuse and send message.
            :return: True
        """
        self.ensure_one()
        self.state = 'refuse'
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Booking Refused.'))

    def set_draft(self):
        """
            Change state to draft and send message.
            :return: True
        """
        self.ensure_one()
        self.state = 'draft'
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Booking Created.'))
        self.po_number = False
        self.approved_by = False

    def generate_expense(self):
        self.ensure_one()
        product_id = self.env.ref('saudi_hr_flight_book.air_flight_ticket')
        name = 'Flight Booking - ' + self.name_get()[0][1]
        return self.generate_expense_payment(self, self.expense_note, self.emp_contribution, self.company_contribution, self.payment_mode,
                    name, product_id, self.expense_total, company_contribution_amount=self.company_contribution_amount,
                    emp_contribution_amount=self.emp_contribution_amount, calculate_company_expense=self.calculate_company_expense)

    def view_expense(self):
        """
            Redirect to show expense method.
            return: Current record expense ID
        """
        for line in self:
            return self.redirect_to_expense(line.expense_ids)


class FlightBookingLine(models.Model):
    _name = 'flight.booking.line'
    _order = 'id desc'
    _inherit = 'mail.thread'
    _description = "Flight Booking Lines"

    def _set_currency(self):
        """
            set currency based on company currency
        """
        self.currency_id = self.company_id.currency_id.id if self.company_id else False

    ticket_no = fields.Char(string='Ticket Number', required=True)
    booking_id = fields.Many2one('flight.booking', string='Booking Request')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    travel_date = fields.Date(string='Date of Journey', required=True)
    source = fields.Char(string='Leaving From', required=True)
    destination = fields.Char(string='Going To', required=True)
    airline = fields.Many2one('airlines', string='Airline', required=True)
    invoice_amount = fields.Float(string='Invoice Amount', required=True)
    currency_id = fields.Many2one('res.currency', compute=_set_currency)
    remarks = fields.Text(string='Remarks')
    seats = fields.Integer(string='No. of Seats', default=1, readonly=True)
    member_type = fields.Selection([('adult', 'Adult'), ('child', 'Child'), ('infant', 'Infant')], string="Member Type")
    flight_class = fields.Selection([('first', 'First'),
                                     ('business', 'Business'), ('guest', 'Guest')], string='Class', default='first')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, values):
        """
            Create a new record
            :return: Newly created record ID
        """
        if values.get('booking_id'):
            self._check_state(values['booking_id'])
        return super(FlightBookingLine, self).create(values)

    def _check_state(self, booking_id):
        """
            Check flight booking states.
            :param booking_id: A recordset of bookings
            :return: True
        """
        booking = self.env['flight.booking'].browse(booking_id)
        if booking.state not in ['in_progress', 'received']:
            raise UserError(_("You can't set details for the Booking which is not in 'In Progress' state!"))
        return True

    def write(self, values):
        """
            Update an existing record.
            :param values:
            :return: Current update record ID
        """
        if values.get('booking_id'):
            self._check_state(values['booking_id'])
        else:
            self._check_state(self.booking_id.id,)
        return super(FlightBookingLine, self).write(values)

    @api.depends('ticket_no', 'travel_date')
    def name_get(self):
        """
            Return names with TravelDate as well as Tickets Number
            :return: List of TravelDate and Tickets Number
        """
        res = []
        for ticket in self:
            name = ''.join([ticket.ticket_no, ' - ', str(ticket.travel_date)])
            res.append((ticket.id, name))
        return res


class Airlines(models.Model):
    _name = 'airlines'
    _order = 'id desc'
    _description = 'Airlines'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique!'),
    ]


class GroupMember(models.Model):
    _name = 'group.member'
    _order = 'id desc'
    _description = 'Group Member'

    booking_id = fields.Many2one('flight.booking', 'Booking Request', required=True)
    name = fields.Char('Name', required=True)
    type = fields.Selection([('employee', 'Employee'),
                             ('family', 'Family'),
                             ('visitor', 'Visitor'),
                             ('other', 'Other')], required=True, string='Type')
