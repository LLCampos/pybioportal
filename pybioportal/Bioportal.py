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

    def annotator(self, text, only_terms_names=False,
                  show_synonyms_names=False, **kwargs):

        '''If the 'only_terms_names' argument is true, return only a set of
        the terms annotated. If show_synonyms_names is false, if the term is a
        synonym, the preferred name will be added to the set, not the synonym.
        '''

        # http://data.bioontology.org/documentation#nav_annotator

        endpoint = '/annotator'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['text'] = text

        complete_annotations = self._bioportal_api_request(full_url, payload)

        if only_terms_names:
            return self._extract_terms_names_from_annotations(complete_annotations,
                                                              show_synonyms_names)
        else:
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

    def _extract_terms_names_from_annotations(self, complete_annotations,
                                              show_synonyms_names):
        all_terms = []

        for annotated_class in complete_annotations:
            for annotation in annotated_class['annotations']:
                match_type = annotation['matchType']

                if match_type == u'PREF':
                    preferred_term_name = annotation['text']
                # Go get the preferred name for this term.
                elif match_type == u'SYN':
                    if show_synonyms_names:
                        preferred_term_name = annotation['text']
                    else:
                        class_url = annotated_class['annotatedClass']['links']['self']
                        payload = {'apikey': self.apikey}
                        class_info_dict = requests.get(class_url, payload).json()
                        preferred_term_name = class_info_dict['prefLabel']

                all_terms.append(preferred_term_name.lower())

        return set(all_terms)

    def _process_payload(self, payload):
        '''Turn boolean True to str 'true' and False to str 'false'. Otherwise,
        server will ignore argument with boolean value.'''

        def process_value(value):
            if type(value) is bool:
                return str(value).lower()
            else:
                return value

        return {key: process_value(value) for key, value in payload.iteritems()}
