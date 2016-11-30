import requests
import urllib
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

        return self._bioportal_api_request(full_url, payload)

    def annotator(self, text, **kwargs):

        # http://data.bioontology.org/documentation#nav_annotator

        endpoint = '/annotator'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['text'] = text

        complete_annotations = self._bioportal_api_request(full_url, payload)

        return complete_annotations

    def recommender(self, text_or_keywords, **kwargs):

        # http://data.bioontology.org/documentation#nav_recommender

        endpoint = '/recommender'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['input'] = text_or_keywords

        return self._bioportal_api_request(full_url, payload)

    def ontology_class(self, ontology, cls_id):
        '''
        Just supports the /ontologies/:ontology/classes/:cls endpoint, which
        returns information about one class

        ontology: name of the ontology
        cls_id: @id of the class. Ex: http://www.radlex.org/RID/#RID43314
        '''

        # http://data.bioontology.org/documentation#Class

        escaped_cls_id = urllib.quote(cls_id, safe='')
        endpoint = '/ontologies/{}/classes/{}'.format(ontology, escaped_cls_id)
        full_url = Bioportal.BASE_URL + endpoint

        return self._bioportal_api_request(full_url)

    def _bioportal_api_request(self, url, payload={}):

        payload['apikey'] = self.apikey
        processed_payload = self._process_payload(payload)

        r = requests.get(url, params=processed_payload)

        if r.status_code is 414:
            raise HTTPError('Text is too long.')

        json_response = r.json()

        try:
            # This will raise an HTTPError if the HTTP request returned an
            # unsuccessful status code.
            r.raise_for_status()
        except HTTPError:
            if 'errors' in json_response.keys():
                error_messages = json_response['errors']
                error_message = '\n'.join(error_messages)
            elif 'error' in json_response.keys():
                error_message = json_response['error']

            raise HTTPError(error_message)

        return json_response

    def _process_payload(self, payload):
        '''Turn boolean True to str 'true' and False to str 'false'. Otherwise,
        server will ignore argument with boolean value.'''

        def process_value(value):
            if type(value) is bool:
                return str(value).lower()
            else:
                return value

        return {key: process_value(value) for key, value in payload.iteritems()}
