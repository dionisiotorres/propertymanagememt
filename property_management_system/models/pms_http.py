from odoo.http import request
import odoo
import json
from odoo import models
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug import urls
from werkzeug.wsgi import wrap_file

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        res = super(Http, self).session_info()
        display_switch_property_menu =  user.has_group('property_management_system.group_multi_property') and len(user.property_id) > 1
        res['property_id'] =  user.current_property_id.id if request.session.uid else None
        res['user_properties'] = {'current_property': (user.current_property_id.id, user.current_property_id.name), 'allowed_properties': [(pro.id, pro.name) for pro in user.property_id]} if display_switch_property_menu else False
        return res


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'
    _description = "HTTP Routing"

    @classmethod
    def _dispatch(cls):
        # locate the controller method
        try:
            rule, arguments = cls._find_handler(return_rule=True)
            func = rule.endpoint
        except werkzeug.exceptions.NotFound as e:
            return cls._handle_exception(e)

        # check authentication level
        try:
            auth_method = cls._authenticate(func.routing["auth"])
        except Exception as e:
            return cls._handle_exception(e)

        processing = cls._postprocess_args(arguments, rule)
        if processing:
            return processing

        # set and execute handler
        try:
            request.set_handler(func, arguments, auth_method)
            result = request.dispatch()
            if isinstance(result, Exception):
                raise result
        except Exception as e:
            return cls._handle_exception(e)        
        # cls._ensure_sequence()
        # if result.data:
        #     isValid = validateJSON(result.data)
        #     if isValid:
        #         error_data = json.loads(result.data)
        #         if 'error' in error_data:
        #             error_data['error']['message'] = 'ZPMS'
        #             result.data = json.dumps(error_data, sort_keys=True)
        return result
