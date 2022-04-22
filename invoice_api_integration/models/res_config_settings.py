from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_token = fields.Char(string='API Invoice Token',
                                help='Necessary for some functionalities in the API view',
                                default="41AX4XfWgj8kpQnGGONtjfYcOVV4u5sMWuVjksWb_I5GS89JVL4loH7XAnC2o")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(invoice_token=str(get_param('invoice_api_integration.invoice_token')) if get_param(
            'invoice_api_integration.invoice_token') else '')
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("invoice_api_integration.invoice_token", self.invoice_token)


ResConfigSettings()
