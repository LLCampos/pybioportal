# pybioportal
A Python binding of the BioPortal REST API.

There are a lot of endpoints missing. Feel free to fork this and make pull requests.

**Usage example:** 

```python
from pybioportal.Bioportal import Bioportal

biop = Bioportal('{{your api key}}')
annotations = biop.annotator('my upper limb', ontologies='RADLEX', exclude_synonyms=False)
```
