import requests
from requests import HTTPError


class Bioportal(object):

    '''A Python binding of the BioPortal REST API
    (http://data.bioontology.org/documentation)'''

    BASE_URL = 'http://data.bioontology.org'

    def __init__(self, api_key):
        self.apikey = api_key

    def classes(self, search_query, **kwargs):

        # http://data.bioontology.org/documentation#nav_search

        endpoint = '/search'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['q'] = search_query
        payload['apikey'] = self.apikey

        return self._bioportal_api_request(full_url, payload)

    def annotator(self, text, **kwargs):

        # http://data.bioontology.org/documentation#nav_annotator

        endpoint = '/annotator'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['text'] = text
        payload['apikey'] = self.apikey

        complete_annotations = self._bioportal_api_request(full_url, payload)

        return complete_annotations

    def recommender(self, text_or_keywords, **kwargs):

        # http://data.bioontology.org/documentation#nav_recommender

        endpoint = '/recommender'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['input'] = text_or_keywords
        payload['apikey'] = self.apikey

        return self._bioportal_api_request(full_url, payload)

    def _bioportal_api_request(self, url, payload):

        r = requests.get(url, params=payload)
        json_response = r.json()

        try:
            # This will raise an HTTPError if the HTTP request returned an
            # unsuccessful status code.
            r.raise_for_status()
        except HTTPError:
            error_messages = json_response['errors']
            joint_error_messages = '\n'.join(error_messages)
            raise HTTPError(joint_error_messages)

        return json_response