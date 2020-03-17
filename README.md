# readability
compute readability of text

How to install:
---------------
.. code-block:: text
python3 -m venv readability
cd readability
source bin/activate
git clone https://github.com/ReadabilityCH/readability.git
cd readability
pip install -r requirements.txt

How to use:
-----------
.. code-block:: text
go to python console: python
>>> from .readability_nltk import get_redability_assessments
>>> get_redability_assessments("text to check")
