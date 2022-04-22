# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools, modules,  _
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self.env.uid', 'self.env.su', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        res = super(IrModelAccess, self).check(model, mode=mode, raise_exception=raise_exception)
        context = dict(self.env.context)
        if 'install_mode' not in context and self.env.user.installed_modules and 'saudi' in self.env.user.installed_modules:
            r = True
            if mode != 'read' and model not in ['res.users', 'res.users.log', 'ir.module.module', 'ir.ui.view',
                                                'ir.model.data', 'ir.model', 'ir.model.access', 'res.lang', 'ir.ui.menu',
                                                'bus.presence', 'mail.message', 'res.partner', 'ir.actions.act_window',
                                                'ir.module.category', 'board.board', 'bus', 'bus.bus']:
                r = False
            if not r:
                groups = '\n'.join('\t- %s' % g for g in self.group_names_with_access(model, mode))
                msg_heads = {
                    # Messages are declared in extenso so they are properly exported in translation terms
                    'read': _("Sorry, you are not allowed to access documents of type '%(document_kind)s' (%(document_model)s)."),
                    'write':  _("Sorry, you are not allowed to modify documents of type '%(document_kind)s' (%(document_model)s)."),
                    'create': _("Sorry, you are not allowed to create documents of type '%(document_kind)s' (%(document_model)s)."),
                    'unlink': _("Sorry, you are not allowed to delete documents of type '%(document_kind)s' (%(document_model)s)."),
                }
                msg_params = {
                    'document_kind': self.env['ir.model']._get(model).name or model,
                    'document_model': model,
                }
                if groups:
                    msg_tail = _("This operation is allowed for the groups:\n%(groups_list)s")
                    msg_params['groups_list'] = groups
                else:
                    msg_tail = _("No group currently allows this operation.")
                msg_tail += u' - ({} {}, {} {})'.format(_('Operation:'), mode, _('User:'), self._uid)
                _logger.info('Access Denied by ACLs for operation: %s, uid: %s, model: %s', mode, self._uid, model)
                msg = '%s %s' % (msg_heads[mode], msg_tail)
                raise AccessError(msg % msg_params)
            return bool(r)
        return res
