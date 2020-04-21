import datetime
from odoo import api, fields, models, tools, _


class PMSLeaseReportlWizard(models.TransientModel):
    _name = "pms.lease.report.wizard"
    _description = "Lease Report Wizard"

    property_id = fields.Many2one("pms.properties", "Property")
    # lease_no = fields.Char("Lease No")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    state = fields.Selection([('NEW', "New"), ('EXTENDED', "Extended"),
                              ('RENEWED', 'Renewed'),
                              ('CANCELLED', "Cancelled"),
                              ('TERMINATED', 'Terminated'),
                              ('EXPIRED', "Expired")],
                             string="Status",
                             default="NEW",
                             track_visibility=True)

    @api.multi
    def print_report(self):
        """
            Print report either by warehouse or product-category
        """
        assert len(
            self
        ) == 1, 'This option should only be used for a single id at a time.'
        datas = {
            'form': {
                'property_id': self.property_id.id,
                # 'lease_no': self.lease_no,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'state': self.state,
            }
        }
        return self.env.ref(
            'property_management_system.action_pms_lease_report').with_context(
                landscape=True).report_action(self, data=datas)
