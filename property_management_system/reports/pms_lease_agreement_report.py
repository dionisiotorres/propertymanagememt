
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportPMSLeaseReport(models.AbstractModel):
    _name = 'report.property_management_system.lease_report'
    _description = 'Lease Agreement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print(data.get('form'))
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        report_data = data.get('form')
        property_id = report_data['property_id']
        start_date = report_data['from_date']
        end_date = report_data['to_date']
        state = report_data['state']
        if state:
            lease_ids = self.env["pms.lease_agreement"].search([('property_id', '=', property_id), ('start_date', '>=', start_date), ('start_date', '<=', end_date), ('state', '=', state)], order='start_date')
        else:
            lease_ids = self.env["pms.lease_agreement"].search([('property_id', '=', property_id), ('start_date', '>=', start_date), ('start_date', '<=', end_date)], order='start_date')
        docs = []
        logo = self.env.user.company_id.logo
        lang = self.env.user.company_id.partner_id.lang
        if lease_ids:
            for lid in lease_ids:
                datas = {}
                datas['company_tanent_id'] = lid.company_tanent_id
                datas['property'] = lid.property_id.code
                datas['shop'] = lid.name
                datas['lease_no'] = lid.lease_no
                datas['unit_no'] = lid.unit_no
                datas['start_date'] = lid.start_date
                datas['end_date'] = lid.end_date
                datas['state'] = lid.state
                docs.append(datas)
        return {
            'doc_ids': self.ids,
            'doc_model': "pms.lease_agreement",
            'docs': docs,
            'logo': logo,
            'lang': lang,
        }
