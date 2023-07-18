import json
import base64
import os

from tnzapi.helpers.custom_json_encoder import CustomJSONEncoder

class Functions(object):

    """ Format JSON into pretty format """
    def __pretty__(self, obj):

        return json.dumps(obj,indent=4)
    
    """ New """
    def __pretty_class__(self, obj):
        return json.dumps(obj, default=lambda o: o.__dict__, indent=4)
    
    def __remove_nulls__(d):
        return {k: v for k, v in d.items() if v is not None}

    def __json_dump_dto__(self, obj):
        json_string = json.dumps(obj, default=lambda o: o.__dict__, cls=CustomJSONEncoder)
        res = json.loads(json_string)
        res = {k: v for k, v in res.items() if v is not None}
        return json.dumps(res)

    """ Parse JSON """
    def __parsejson__(self, json_string):
        
        try:
            json_object = json.loads(json_string)
        except ValueError:
            return None

        return json_object

    """ Get Attachment File Name """
    def __getfilename__(self, file_loc):

        file = open(file_loc)

        return os.path.basename(file.name)

    """ Parse Attachment """
    def __getfilecontents__(self, file_loc):

        return base64.b64encode(open(file_loc,"rb").read()).decode("utf-8")
