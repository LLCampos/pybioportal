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

    def annotator(self, text, output_type='bioportal',
                  show_synonyms_names=False, **kwargs):

        """

        output_type argument define how the output is formatted. possible
        values:

        bioportal (default) -- return a list of annotations returned by
                               BioPortal API.
        only_terms_names    -- return only a set of the terms annotated
        brat                -- returns the result in the brat standoff format
                               (http://brat.nlplab.org/standoff.html) as list
                               where each member corresponds to a line in the
                               annotation file.


        If show_synonyms_names is false, if the term is a
        synonym, the preferred name will be added to the set, not the synonym.
        """

        # http://data.bioontology.org/documentation#nav_annotator

        output_types = ['bioportal', 'only_terms_names', 'brat']
        if output_type not in output_types:
            raise Exception('The output_type you sent as argument is not one of'
                            'the allowed output_types values')

        endpoint = '/annotator'
        full_url = Bioportal.BASE_URL + endpoint

        payload = kwargs
        payload['text'] = text

        complete_annotations = self._bioportal_api_request(full_url, payload)

        if output_type == 'bioportal':
            return complete_annotations
        elif output_type == 'only_terms_names':
            return self._extract_terms_names_from_annotations(complete_annotations,
                                                              show_synonyms_names)
        elif output_type == 'brat':
            return Bioportal._convert_to_brat_format(complete_annotations, text)

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

            # Hack while bug on BioPortal is not fixed
            if 'owl-ontologies' in annotated_class['annotatedClass']['@id']:
                continue

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
                        try:
                            preferred_term_name = class_info_dict['prefLabel']
                        except KeyError:
                            raise KeyError("Key error for term \"{}\"".format(annotation['text']))

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

    @staticmethod
    def _convert_to_brat_format(bioportal_annotations, text):
        """Receive a list of BioPortal annotations as the ones returning from
        their API and returns a list the annotations in the brat standoff format
        (http://brat.nlplab.org/standoff.html), where each member of the list
        corresponds to one line of the annotation file.
        """

        brat_annotations = []

        next_entity_id = 1
        for annotated_class in bioportal_annotations:

            # Hack while bug on BioPortal is not fixed
            if 'owl-ontologies' in annotated_class['annotatedClass']['@id']:
                continue

            annot_type = annotated_class['annotatedClass']['links']['ontology'].split('/')[-1]

            for annotation in annotated_class['annotations']:
                annot_id = 'T{}'.format(next_entity_id)
                next_entity_id += 1

                start_offset = annotation['from'] - 1
                end_offset = annotation['to']
                text_annotated = text[start_offset:end_offset]

                annot_data = {
                    'annot_id': annot_id,
                    'annot_type': annot_type,
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                    'text_annotated': text_annotated
                }

                brat_annotations.append(
                    '{annot_id}\t{annot_type} {start_offset} {end_offset}\t{text_annotated}'.format(**annot_data)
                )

        return brat_annotations
