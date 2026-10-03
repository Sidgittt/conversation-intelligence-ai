import json


class JSONService:

    def parse(self, response_text):

        return json.loads(response_text)