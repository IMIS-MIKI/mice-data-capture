from fhir.resources.R4B.binary import Binary
from fhir.resources.R4B.observation import Observation, ObservationComponent
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.quantity import Quantity
from fhir.resources.R4B.narrative import Narrative
import logic.create_image

def get_mdc_mapping(key):
    prefix = key.split('.')[0]
    match prefix:
        case 'ECGI':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131331", "display": "MDC_ECG_ELEC_POTL_V1"}
        case 'ECGII':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131332", "display": "MDC_ECG_ELEC_POTL_V2"}
        case 'ECGIII':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131333", "display": "MDC_ECG_ELEC_POTL_V3"}
        case 'ECGIV':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131334", "display": "MDC_ECG_ELEC_POTL_V4"}
        case 'ECGV':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131335", "display": "MDC_ECG_ELEC_POTL_V5"}
        case 'ECGVI':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131336", "display": "MDC_ECG_ELEC_POTL_V6"}
        case 'aVF':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131392", "display": "MDC_ECG_ELEC_POTL_AVR"}
        case 'aVL':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131391", "display": "MDC_ECG_ELEC_POTL_AVL"}
        case 'aVR':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131390", "display": "MDC_ECG_ELEC_POTL_AVR"}
        case 'SpO2':
            return {"system": "urn:iso:std:iso:11073:10101", "code": "150316", "display": "MDC_SAT_O2"}
        case _:
            return {"system": "urn:iso:std:iso:11073:10101", "code": "131328", "display": "MDC_ECG_ELEC_POTL"}


def fhir(incoming_data):
    key = list(incoming_data.keys())[0]
    image = logic.create_image.createImage(incoming_data[key][0], incoming_data[key][1], key)
    binary = create_binary(image)
    obs = create_observation(incoming_data)
    obs.contained = [binary]
    return obs


def create_binary(base):
    binary = Binary.construct(contentType='image/jpeg')
    binary.id = 'ecg'
    binary.data = base
    return binary


def create_observation(incoming_data):
    obs = Observation.construct()
    obs.status = 'final'
    obs_code = CodeableConcept.construct()
    obs_code.coding = list()
    obs_code.coding.append(
        {"system": "urn:iso:std:iso:11073:10101", "code": "131328", "display": "MDC_ECG_ELEC_POTL"})

    obs.code = obs_code

    div_x = '<div xmlns="http://www.w3.org/1999/xhtml"><p><img src="#ecg"/></p></div>'
    obs.text = Narrative.construct(status='generated', div=div_x)

    obs.component = []
    for entry in incoming_data:
        obs_com = ObservationComponent.construct()
        obs_com_code = CodeableConcept.construct()
        obs_com_code.coding = list()
        obs_com_code.coding.append(get_mdc_mapping(entry))
        obs_com.code = obs_com_code
        value_sample_data_dict = dict()

        value_sample_data_origin = Quantity.construct()
        value_sample_data_origin.value = '-0.5'
        value_sample_data_origin.unit = 'mV'
        value_sample_data_origin.system = 'http://unitsofmeasure.org'
        value_sample_data_origin.code = 'mV'

        value_sample_data_dict['origin'] = value_sample_data_origin
        value_sample_data_dict['period'] = 0.001
        value_sample_data_dict['dimensions'] = 1
        value_sample_data_dict['data'] = str(' ').join(incoming_data[entry][1][0])
        obs_com.valueSampledData = value_sample_data_dict
        obs.component.append(obs_com)

    return obs
