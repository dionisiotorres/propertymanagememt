import datetime
from odoo import api, fields, models, tools, _


class PMSMessageBox(models.TransientModel):
    _name = "pms.alert.message.wizard"
    _description = "Message"

    message = fields.Text("Message", readonly=True)

