# pybioportal
A Python binding of the BioPortal REST API.

There are a lot of endpoints missing. Feel free to fork this and make pull requests.

**Usage example:** 

```python
from pybioportal.Bioportal import Bioportal

biop = Bioportal()
annotations = biop.annotator('my upper limb', ontologies='RADLEX', exclude_synonyms='false')
```

Don't forget to add your API key to the keys.py file! :) 
