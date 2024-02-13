from fhir.resources.R4B.binary import Binary
from fhir.resources.R4B.observation import Observation, ObservationComponent
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.quantity import Quantity
from fhir.resources.R4B.narrative import Narrative


def fhir(incoming_data, image):
    binary = create_binary(image)
    obs = create_observation(incoming_data)
    obs.contained = [binary]
    print(obs.json(indent=2))
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

    obs_com = ObservationComponent.construct()

    obs_com_code = CodeableConcept.construct()
    obs_com_code.coding = list()
    obs_com_code.coding.append(
        {"system": "urn:iso:std:iso:11073:10101", "code": "131329", "display": "MDC_ECG_ELEC_POTL_I"})

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
    value_sample_data_dict['data'] = str(' ').join(incoming_data)

    obs_com.valueSampledData = value_sample_data_dict
    obs.component = [obs_com]

    return obs
