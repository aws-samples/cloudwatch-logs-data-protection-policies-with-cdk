import json

class StackUtils:

    @staticmethod
    def read_cdk_context_json():

        filename = "cdk.json"

        with open(filename, 'r') as my_file:

            data = my_file.read()

        obj = json.loads(data)

        return obj.get('context')
