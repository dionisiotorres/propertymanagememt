import requests
import json
import datetime
from odoo.addons.property_management_system.rauth import OAuth2Service
from odoo import tools, _
from odoo import models, api

# from rauth import OAuth2Service


class APIData:
    def __init__(self, model_id, values, property_obj, integ_obj,
                 api_type_obj):
        self.values = values
        self.model_id = model_id
        self.property_obj = property_obj
        self.integ_obj = integ_obj
        self.api_type_obj = api_type_obj
        return self.get_data()

    def get_data(self):
        property_id = self.values['property_id']
        property_ids = self.property_obj
        integ_obj = self.integ_obj
        api_type_obj = self.api_type_obj
        api_integ_id = integ_obj.search([
            ('property_id', '=', self.values['property_id']),
            ('api_type', '=', api_type_obj['name'])
        ])
        api_integ = []
        headers = {}
        payload_code = payload_name = modify_date = None
        payload = None
        if api_integ_id and property_ids.api_integration == True:
            api_integ = api_integ_id.generate_api_data({
                'id': api_integ_id.id,
                'data': self.values
            })
            headers = api_integ['header']
            url_save = api_integ_id.url + api_integ_id.post_api
            if api_type_obj['name'] == 'Floor':
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
                data_batch.PropertyCode = property_ids.code
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
            if api_type_obj['name'] == 'CRMAccount':
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
                CRM = CRMAccount("", payload_code, payload_name, "", '', "",
                                 self.model_id.id, modify_date, data_batch)
                payload = [{CRM}]
            if api_type_obj['name'] == 'SpaceUnit':
                payload_name = str(self.model_id.name)
                payload_area = str(self.values['area'])
                start_date = str(self.values['start_date'])
                end_date = str(self.values['end_date'])
                floor_code = str(self.model_id.floor_code)
                payload_uom = str(self.model_id.uom)
                payload_remark = str(self.values['remark'])
                floor_id = str(self.model_id.floor_id.id)
                modify_date = datetime.datetime.now().strftime('%Y-%m-%d')
                # if self.values['active'] == True:
                #     payload_active = 'true'
                # else:
                #     payload_active = 'false'
                data_batch = BatchInfo()
                data_batch.AppCode = "SPI"
                data_batch.BatchCode = "201912179810983"
                data_batch.PropertyCode = property_ids.code
                data_batch.InterfaceCode = ""
                spaceunit = SpaceUnit()
                spaceunit.PropertyCode = property_ids.code
                spaceunit.FloorID = floor_id
                # spaceunit.PropertyCode = property_ids.code
                spaceunit.SpaceUnitNo = payload_name
                spaceunit.FloorCode = floor_code
                spaceunit.DisplayOrdinal = ''
                spaceunit.StartDate = start_date
                # spaceunit.EndDate = end_date
                spaceunit.EndDate = ''
                spaceunit.Area = payload_area
                spaceunit.SpaceUnitID = ''
                # spaceunit.UM = payload_uom
                spaceunit.UM = ''
                # spaceunit.Remark = payload_remark
                spaceunit.Remark = ''
                spaceunit.ExtDataSourceID = 'ZPMS'
                spaceunit.ExtSpaceUnitID = str(self.model_id.id)
                # spaceunit.ModifiedDate = modify_date
                spaceunit.ModifiedDate = modify_date
                spaceunit.Status = '1'
                spaceunit.BatchInfo = data_batch.__dict__
                payload = spaceunit.__dict__
            if api_type_obj['name'] == 'SpaceUnitFacility':
                # payload_code = str(self.values['code'])
                # payload_name = str(self.values['name'])
                modify_date = datetime.datetime.now().strftime('%Y-%m-%d')
                # if self.values['active'] == True:
                #     payload_active = 'true'
                # else:
                #     payload_active = 'false'
                data_batch = BatchInfo()
                data_batch.AppCode = "SPUFI"
                data_batch.BatchCode = "2019121709888"
                data_batch.PropertyCode = property_ids.code
                data_batch.InterfaceCode = ""
                facility = SpaceUnitFacility()
                # facility.SpaceUnitID = self
                facility.SpaceUnitID = '41'
                facility.SpaceUnitFacilityID = None
                facility.StartDate = str(
                    self.model_id.facilities_line.start_date)
                facility.EndDate = str(self.model_id.facilities_line.end_date)
                facility.UtilityMeterNo = self.model_id.meter_no.name
                facility.UtilityType = self.model_id.utility_type_id.code
                facility.LastReadingOn = str(
                    self.model_id.facilities_line.start_date)
                facility.LastReadingValue = self.model_id.facilities_line.start_reading_value
                facility.LastReadingNOC = 0
                facility.LastReadingNOH = 0
                facility.EMeterType = ''
                facility.Remark = None
                facility.IsNew = True
                facility.UpdateMethod = None
                facility.Digit = self.model_id.facilities_line.digit
                facility.Indicator = None
                facility.CanChangeMeterNo = False
                facility.ExtDataSourceID = 'ZPMS'
                facility.ExtSpaceUnitFacilityID = str(self.model_id.id)
                facility.ModifiedDate = modify_date
                facility.BatchInfo = data_batch.__dict__
                payload = facility.__dict__
            if api_type_obj['name'] == 'LeaseAgreement':
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
            datapayload = json.dumps([payload])
            print(datapayload)
            requests.request("POST",
                             url_save,
                             data=json.dumps([payload]),
                             headers=headers)


class Auth2Client:
    def __init__(self, url, client_id, client_secret, access_token):
        self.access_token = self.service = self.url = None
        self.url = url
        self.service = OAuth2Service(
            name="foo",
            client_id=client_id,
            client_secret=client_secret,
            access_token_url=url + access_token,
            authorize_url=url + access_token,
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
