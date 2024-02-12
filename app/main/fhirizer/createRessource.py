#from fhir.resources.binary import binary


def createBinaryRessource(base):

    json_obj = {"ressourceType": "Binary",
                "contentType": "text/csv",
                "data": str(base)
                }
    #bin = binary.parse_obj(json_obj)
    print(json_obj)