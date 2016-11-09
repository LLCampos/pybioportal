import requests
from requests import HTTPError
from keys import BIOPORTAL_API_KEY


class Bioportal(object):

    '''A Python binding of the BioPortal REST API
    (http://data.bioontology.org/documentation)'''

    BASE_URL = 'http://data.bioontology.org'

    def __init__(self):
        # You can get the API Key by signing up at BioPortal website. You
        # should had your key to the keys.py file.
        if not BIOPORTAL_API_KEY:
            raise Exception('You probably forgot to add your API Key to the '
                            'code.')
        self.apikey = BIOPORTAL_API_KEY

    def classes(self, search_query, **kwargs):

        # http://data.bioontology.org/documentation#nav_search

        endpoint = '/search'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['q'] = search_query
        payload['apikey'] = self.apikey

        return self._bioportal_api_request(full_url, payload)

    def annotator(self, text, only_terms_names=False, **kwargs):

        '''If the 'only_terms_names' argument is true, return only a set of
        the terms annotated. If the term found is a synonym, it will return  '''

        # http://data.bioontology.org/documentation#nav_annotator

        endpoint = '/annotator'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['text'] = text
        payload['apikey'] = self.apikey

        complete_annotations = self._bioportal_api_request(full_url, payload)

        if only_terms_names:
            return self._extract_terms_names_from_annotations(complete_annotations)
        else:
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

    def _extract_terms_names_from_annotations(self, complete_annotations):
        all_terms = []

        for annotated_class in complete_annotations:
            for annotation in annotated_class['annotations']:
                all_terms.append(annotation['text'])

        return set(all_terms)
