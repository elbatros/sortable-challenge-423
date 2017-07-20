# Sortable Coding Challenge

reconcile.py holds the setup and output logic, match.py holds the
matching logic.

## Methodology

Attempt strictest search to first minimize false positives, then use
the false negatives to find edge cases to make informed flexibility
changes to search criteria.

## Ideas

1. Basic matching by search hierarchy from manufacturer to family to model. Also clean the data by normalizing case and stripping extra whitespace.

2. Tokenize the listing's manufacturer and try to find a match with each token to deal with cases of international branches, ex. Canon Canada. We can assume that if one token of the sentence is an existing manufacturer name, then it should be reasonable to equate them.

3. Add flexibility to search by continuing the search with the model name if the family name is not found. Helps resolve cases where family name is left out of the listing title, or the product is legitimately not part of a family line.

4. "Fuzzy match" the model name by using variants with spaces removed or replacing them with - and _. A common issue with record linkage is inconsistent formats.

5. If family name was found but model name was not, apply same logic in step 3, and check all IDs for the manufacturer. Solves the issue of duplicate family names Cyber-shot and Cybershot.

6. For model names that start with characters and end with digits, introduce a delimiter between the characters and digits. Solves the issue when some model names are delimited in listings, but not in products.

7. Use parallel map-reduce to scale the solution.

