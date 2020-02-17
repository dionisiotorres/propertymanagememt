import requests
import json
import datetime
from odoo.addons.property_management_system.rauth import OAuth2Service
from odoo import tools, _
from odoo import models, api
# from rauth import OAuth2Service


class APIData:
    def __init__(self, model_id, values, property_id, integ_obj, api_line_ids):
        self.values = values
        self.model_id = model_id
        self.property_id = property_id
        self.integ_obj = integ_obj
        self.api_line_ids = api_line_ids
        return self.get_data()

    def get_data(self):
        property_ids = self.property_id
        integ_obj = self.integ_obj
        api_line_ids = self.api_line_ids
        api_integ = data = []
        headers = {}
        payload_code = payload_name = modify_date = payload = None
        if api_line_ids:
            for line in api_line_ids:
                url_save = line.api_integration_id.base_url + '/' + line.api_url
                if line.http_method_type == 'post':
                    api_integ = line.generate_api_data({
                        'id': line.id,
                        'data': self.values
                    })
                    headers = api_integ['header']
                    if line.name == 'Floor':
                        payload_code = str(self.values['code'])
                        payload_name = str(self.values['name'])
                        modify_date = datetime.datetime.now().strftime(
                            '%Y-%m-%d %H:%M:%S.%f')
                        if self.values['active'] == True:
                            payload_active = 'true'
                        else:
                            payload_active = 'false'
                        data_batch = BatchInfo()
                        data_batch.AppCode = "FI"
                        data_batch.BatchCode = "2019121798381"
                        data_batch.PropertyCode = 'JNC' if property_ids.code else JNC
                        data_batch.InterfaceCode = ""
                        floor = Floor()
                        floor.BatchInfo = data_batch.__dict__
                        floor.FloorID = "1"
                        floor.FloorCode = payload_code
                        floor.FloorDesc = payload_name
                        floor.ModifiedDate = modify_date
                        floor.ExtDataSourceID = "ZPMS"
                        floor.Remark = ''
                        floor.ExtFloorID = self.model_id.id
                        payload = floor.__dict__
                    if line.name == 'CRMAccount':
                        # payload_code = str(self.values['code'])
                        # payload_name = str(self.values['name'])
                        modify_date = datetime.datetime.now().strftime(
                            '%Y-%m-%d %H:%M:%S.%f')
                        if self.values['active'] == True:
                            payload_active = 'true'
                        else:
                            payload_active = 'false'
                        data_batch = BatchInfo("PEMS", property_ids.code,
                                               "2019121798380", "")
                        CRM = CRMAccount("", payload_code, payload_name, "",
                                         '', "", self.model_id.id, modify_date,
                                         data_batch)
                        payload = [{CRM}]
                    if line.name == 'SpaceUnit':
                        payload_name = str(self.model_id.name)
                        payload_area = str(self.values['area'])
                        start_date = str(self.values['start_date'])
                        end_date = str(
                            self.values['end_date']
                        ) if self.values['end_date'] != False else None
                        floor_code = str(self.model_id.floor_code)
                        payload_uom = str(self.model_id.uom.name)
                        payload_remark = str(
                            self.values['remark']
                        ) if self.values['remark'] != False else None
                        floor_id = str(self.model_id.floor_id.id)
                        modify_date = datetime.datetime.now().strftime(
                            '%Y-%m-%d')
                        if self.values['active'] == True:
                            payload_active = '1'
                        else:
                            payload_active = '0'
                        data_batch = BatchInfo()
                        data_batch.AppCode = "SPI"
                        data_batch.BatchCode = "47389245" + str(
                            self.model_id.id)
                        data_batch.PropertyCode = property_ids.code
                        data_batch.InterfaceCode = ""
                        spaceunit = SpaceUnit()
                        spaceunit.PropertyCode = property_ids.code
                        spaceunit.FloorID = floor_id
                        spaceunit.SpaceUnitNo = payload_name
                        spaceunit.FloorCode = floor_code
                        spaceunit.DisplayOrdinal = None
                        spaceunit.StartDate = start_date
                        spaceunit.EndDate = end_date
                        spaceunit.Area = payload_area
                        spaceunit.SpaceUnitID = ''
                        spaceunit.UM = payload_uom
                        spaceunit.Remark = payload_remark
                        spaceunit.ExtDataSourceID = 'ZPMS'
                        spaceunit.ExtSpaceUnitID = str(self.model_id.id)
                        spaceunit.ModifiedDate = modify_date
                        spaceunit.Status = payload_active
                        spaceunit.BatchInfo = data_batch.__dict__
                        payload = spaceunit.__dict__
                    if line.name == 'SpaceUnitFacilities':
                        if self.model_id.facility_line.facilities_line:
                            for facline in self.model_id.facility_line.facilities_line:
                                modify_date = datetime.datetime.now().strftime(
                                    '%Y-%m-%d')
                                data_batch = BatchInfo()
                                data_batch.AppCode = "ZPMS"
                                data_batch.BatchCode = "47389245" + str(
                                    self.model_id.id)
                                data_batch.PropertyCode = self.model_id.property_id.code
                                data_batch.InterfaceCode = "SPUFI"
                                facility = SpaceUnitFacility()
                                facility.SpaceUnitID = str(self.model_id.id)
                                facility.SpaceUnitFacilityID = ''
                                facility.StartDate = str(
                                    self.model_id.start_date)
                                facility.EndDate = str(
                                    self.model_id.end_date
                                ) if self.model_id.end_date else None
                                facility.UtilityMeterNo = self.model_id.facility_line.utilities_no.name
                                facility.UtilityType = self.model_id.facility_line.utilities_type_id.code
                                facility.LastReadingOn = str(facline.lmr_date)
                                facility.LastReadingValue = facline.lmr_value
                                facility.LastReadingNOC = 0
                                facility.LastReadingNOH = 0
                                facility.EMeterType = facline.source_type_id.code
                                facility.Remark = str(
                                    self.model_id.remark
                                ) if self.model_id.remark != False else None
                                facility.IsNew = True
                                facility.UpdateMethod = None
                                facility.Digit = self.model_id.facility_line.utilities_no.digit
                                facility.Indicator = None
                                facility.CanChangeMeterNo = False
                                facility.ExtDataSourceID = 'ZPMS'
                                facility.ExtSpaceUnitFacilityID = str(
                                    facline.id)
                                facility.ModifiedDate = modify_date
                                facility.BatchInfo = data_batch.__dict__
                                data.append(facility.__dict__)
                    if line.name == 'LeaseAgreement':
                        # payload_code = str(self.values['code'])
                        # payload_name = str(self.values['name'])
                        modify_date = datetime.datetime.now().strftime(
                            '%Y-%m-%d %H:%M:%S.%f')
                        if self.values['active'] == True:
                            payload_active = 'true'
                        else:
                            payload_active = 'false'
                        data_batch = BatchInfo()
                        data_batch.AppCode = "LGI"
                        data_batch.BatchCode = "20191217983089"
                        data_batch.PropertyCode = property_ids.code
                        data_batch.InterfaceCode = ""
                        lease = LeaseAgreement()
                        lease.LeaseAgreementID = self.model_id.id
                        lease.CrmAccountID = ''
                        lease.PosVendorID = ''
                        lease.PropertyID = property_ids.id
                        lease.PosIDs = ''
                        lease.LeaseStartDate = self.model_id.start_date
                        lease.LeaseEndDate = self.model_id.end_date
                        lease.ExtendedTo = self.model_id.extend_date
                        # lease.OldEndDate = ''
                        # lease.RevisedEndDate = ''
                        lease.Remark = ''
                        lease.EnforceGPFlag = ''
                        lease.ResetGPFlag = ''
                        lease.SetResetOn = ''
                        lease.LeaseStatus = ''
                        lease.ResetDate = ''
                        lease.ExternalLeaseNo = ''
                        lease.LeaseAggrementCode = ''
                        lease.PosInterfaceCode = ''
                        lease.AppAccessKey = ''
                        lease.AppSecretAccessKey = ''
                        lease.DefaultLocalCurrency = ''
                        lease.PropertyName = property_ids.name
                        lease.PropertyCode = property_ids.code
                        lease.ShopName = self.model_id.company_tanent_id.name
                        lease.VendorName = self.model_id.company_vendor_id.name
                        lease.PosSubmissionFrequency = ''
                        lease.LeaseStatusDesc = ''
                        lease.SpaceUnitNo = self.model_id.unit_no
                        lease.AppAccessKeyStatus = ''
                        lease.DebugMode = ''
                        lease.ExtDataSourceID = 'ZPMS'
                        lease.ModifiedDate = modify_date
                        lease.ExtLeaseAgreementID = str(self.model_id.id)
                        lease.PosSubmissionType = ''
                        lease.SalesDataType = ''
                        lease.PosSubmissionTypeDesc = ''
                        lease.SalesDataTypeDesc = ''
                        lease.SubmissionLink = ''
                        lease.BatchInfo = data_batch.__dict__
                        payload = lease.__dict__
                    r = requests.request(
                        "POST",
                        url_save,
                        data=json.dumps([payload] if payload else data),
                        headers=headers)


class Auth2Client:
    def __init__(self, url, client_id, client_secret, access_token):
        self.access_token = self.service = self.url = None
        self.url = url
        self.service = OAuth2Service(
            name="foo",
            client_id=client_id,
            client_secret=client_secret,
            access_token_url=access_token,
            authorize_url=access_token,
            base_url=url,
        )
        return self.get_access_token()

    def get_access_token(self):
        data = {
            'code': 'bar',
            'grant_type': 'client_credentials',
            'redirect_uri': self.url
        }
        session = self.service.get_auth_session(data=data, decoder=json.loads)
        self.access_token = session.access_token


class BatchInfo:
    AppCode = None
    PropertyCode = None
    BatchCode = None
    InterfaceCode = None


class Floor:
    FloorID = None
    FloorCode = None
    FloorDesc = None
    DisplayOrdinal = None
    Remark = None
    ExtDataSourceID = None
    ExtFloorID = None
    ModifiedDate = None
    BatchInfo = None


class CRMAccount:
    CRMAccountName = None
    CRMAccountID = None
    CRMAccountTypeID = None
    Remark = None
    RegNo = None
    WebSiteUrl = None
    CountryOfOrigin = None
    ContactPerson = None
    Phone = None
    Address = None
    TenantCode = None
    Trade = None
    TradeCategory = None
    CRMAccountTypeDescription = None
    ExtDataSourceID = None
    ExtCRMAccountID = None
    ModifiedDate = None
    BatchInfo = None


class SpaceUnit:
    FloorID = None
    SpaceUnitID = None
    PropertyID = None
    SpaceUnitNo = None
    PropertyCode = None
    FloorCode = None
    DisplayOrdinal = None
    Area = None
    Remark = None
    StartDate = None
    EndDate = None
    UM = None
    Status = None
    ExtDataSourceID = None
    ExtSpaceUnitID = None
    ModifiedDate = None
    BatchInfo = None


class SpaceUnitFacility:
    SpaceUnitID = None
    SpaceUnitFacilityID = None
    StartDate = None
    EndDate = None
    UtilityMeterNo = None
    UtilityType = None
    LastReadingOn = None
    LastReadingValue = None
    LastReadingNOC = None
    LastReadingNOH = None
    EMeterType = None
    Remark = None
    IsNew = None
    UpdateMethod = None
    Digit = None
    Indicator = None
    CanChangeMeterNo = None
    ExtDataSourceID = None
    ExtSpaceUnitFacilityID = None
    ModifiedDate = None
    BatchInfo = None


class LeaseAgreement:
    LeaseAgreementID = None
    CrmAccountID = None
    PosVendorID = None
    PropertyID = None
    PosIDs = None
    LeaseStartDate = None
    LeaseEndDate = None
    ExtendedTo = None
    OldEndDate = None
    RevisedEndDate = None
    Remark = None
    EnforceGPFlag = None
    ResetGPFlag = None
    SetResetOn = None
    LeaseStatus = None
    ResetDate = None
    ExternalLeaseNo = None
    LeaseAggrementCode = None
    PosInterfaceCode = None
    AppAccessKey = None
    AppSecretAccessKey = None
    DefaultLocalCurrency = None
    PropertyName = None
    PropertyCode = None
    ShopName = None
    VendorName = None
    PosSubmissionFrequency = None
    LeaseStatusDesc = None
    SpaceUnitNo = None
    AppAccessKeyStatus = None
    DebugMode = None
    ExtDataSourceID = None
    ModifiedDate = None
    ExtLeaseAgreementID = None
    PosSubmissionType = None
    SalesDataType = None
    PosSubmissionTypeDesc = None
    SalesDataTypeDesc = None
    SubmissionLink = None
    BatchInfo = None
