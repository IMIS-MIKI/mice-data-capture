from fhir.resources.R4B.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.binary import Binary
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.quantity import Quantity
import helper

metrics = {'ECGI.Realtimecurve.68.793F': 'DeviceMetric/0a017abd-db0e-5865-ab2c-1de1c9d6406e',
           'ECGII.Realtimecurve.69.77E9': 'DeviceMetric/714ecc05-bab8-548e-8c28-54ea8e6c888f',
           'ECGIII.Realtimecurve.6A.3BBF': 'DeviceMetric/31a2c6e4-e3f6-5de8-8ac1-c285e81db318',
           'aVR.Realtimecurve.76.28D': 'DeviceMetric/c2512950-fb66-5025-a9ee-79ab7ab630d2',
           'aVL.Realtimecurve.75.48B7': 'DeviceMetric/c6d1881e-ebdc-54c7-bb22-08c8a2f9a027',
           'aVF.Realtimecurve.74.FF': 'DeviceMetric/a57aaad3-c299-5f59-9250-5a2f4d695356',
           'ECGV.Realtimecurve.6B.573E': 'DeviceMetric/890a7d4f-fb6b-5e63-be5a-aabd090a087d',
           'ECGV.Realtimecurve.6C.64E8': 'DeviceMetric/890a7d4f-fb6b-5e63-be5a-aabd090a087d',
           'SpO2.Realtimecurve.31.DB6': 'DeviceMetric/5ec1cc7c-85f2-52ea-89e3-7dc39701dadb'}


def get_mdc_mapping(key):
    prefix = key.split('.')[0]
    match prefix:
        case 'ECGI':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131329", "display": "MDC_ECG_ELEC_POTL_I"}
        case 'ECGII':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131330", "display": "MDC_ECG_ELEC_POTL_II"}
        case 'ECGIII':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131389", "display": "MDC_ECG_ELEC_POTL_III"}
        case 'ECGV':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131395", "display": "MDC_ECG_ELEC_POTL_V"}
        case 'aVF':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131392", "display": "MDC_ECG_ELEC_POTL_AVR"}
        case 'aVL':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131391", "display": "MDC_ECG_ELEC_POTL_AVL"}
        case 'aVR':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131390", "display": "MDC_ECG_ELEC_POTL_AVR"}
        case 'SpO2':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "150456", "display": "MDC_PULS_OXIM_SAT_O2"}
        case _:
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131328", "display": "MDC_ECG_ELEC_POTL"}


def fhirize(incoming_data):
    bundle = Bundle.construct()
    bundle.type = 'transaction'

    binary_entry = BundleEntry.construct()

    keys = list(incoming_data.keys())
    image = helper.create_image(incoming_data[keys[0]][0], incoming_data[keys[0]][1], keys[0])
    binary = create_binary(image)

    binary_entry.resource = binary
    binary_entry.request = BundleEntryRequest(url='Binary', method='POST')
    bundle.entry = [binary_entry]

    for k in keys:
        obs_entry = BundleEntry.construct()
        obs_entry.request = BundleEntryRequest(url='Observation', method='POST')
        obs = create_observation(k, incoming_data[k][1])
        obs.device = Reference.construct(reference=metrics[k])
        obs_entry.resource = obs
        bundle.entry.append(obs_entry)
    return bundle


def create_binary(base):
    binary = Binary.construct(contentType='image/jpeg')
    binary.id = 'ecg'
    binary.data = base
    return binary


def create_observation(key, incoming_data):
    obs = Observation.construct()
    obs.status = 'final'
    obs_code = CodeableConcept.construct()
    obs_code.coding = list()
    obs_code.coding.append(get_mdc_mapping(key))
    value_sample_data_dict = dict()
    value_sample_data_origin = Quantity.construct()
    value_sample_data_origin.value = '-0.5'
    value_sample_data_origin.unit = 'mV'
    value_sample_data_origin.system = 'http://unitsofmeasure.org'
    value_sample_data_origin.code = 'mV'
    value_sample_data_dict['origin'] = value_sample_data_origin
    value_sample_data_dict['period'] = 0.001
    value_sample_data_dict['dimensions'] = 1
    value_sample_data_dict['data'] = str(' ').join(incoming_data[0])
    obs.valueSampledData = value_sample_data_dict
    return obs
