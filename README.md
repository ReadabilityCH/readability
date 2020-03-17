# readability
compute readability of text

How to install:
---------------
* python3 -m venv readability
* cd readability
* source bin/activate
* git clone https://github.com/ReadabilityCH/readability.git
* cd readability
* pip install -r requirements.txt

How to use:
-----------
* go to python console: python
* import nltk
* nltk.download('punkt')
* nltk.download('stopwords')
* nltk.download('cmudict')
* nltk.download('averaged_perceptron_tagger')
* from .readability_nltk import get_redability_assessments
* get_redability_assessments("text to check")
