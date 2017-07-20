import re

'''
Matches strictly using search hierarchy with tokenized manufacturer.
Cache the mapping between listing and product manufacturer names to
speed up on the search. Search for family names within the title, and
prioritize ID matching from those. If not found, then look through the
rest of the manufacturer IDs. Fuzzy match the model with variations on the
delimiter.
'''
def add_match(matched, prod, lst):
    if not prod in matched:
        matched[prod] = {
            'product_name': prod,
            'listings': [lst]
        }
    else:
        matched[prod]['listings'].append(lst)

# search using tokenized manufacturer with cached lookup
def match_manufacturer(lst, manu, st, cache):
    if manu in cache:
        return cache[manu]

    if manu in st:
        cache[manu] = manu
        return manu

    # check if part of manufacturer's name in search tree
    for word in manu.split():
        if word in st:
            cache[manu] = word
            return word

    cache[manu] = None
    return None


# fuzzy match on the model name
def match_model(model, title):
    rgx = model

    # assume model is characters followed by digits
    # insert a space to check for cases where
    # model is tokenized in listing
    m = re.fullmatch('([a-z]+)(\d+[a-z]*)', model)
    if m:
        rgx = m.group(1) + ' ' + m.group(2)


    # check variations of delimiter or lack thereof
    rgx = rgx.replace('-', ' ').replace('_', ' ')
    rgx = rgx.replace(' ', '( |-|_)?')

    # check for word boundary so we don't accidentally match model
    # which is prefix or suffix of another
    rgx = "\\b" + rgx + "\\b"

    result = re.search( rgx, title )

    return result is not None


def match_listings(listings, st):
    count = 0
    matched = {}
    cache = {}

    for lst in listings:
        manu = lst['manufacturer'].lower().strip()
        title = lst['title'].lower().strip()

        # manufacturer is incorrect
        manu = match_manufacturer(lst, manu, st, cache)

        if not manu:
            continue

        families = set()

        # search for family name in listing description
        for family in st[manu].keys():
            if family in title:
                families.add( family )

        hasModel = False

        # give priority to looking through IDs in found families
        for family in families:
            for model in st[manu][family].keys():
                if match_model(model, title):
                    count += 1
                    hasModel = True
                    add_match(
                        matched,
                        st[manu][family][model],
                        lst
                    )
                    break

            if hasModel:
                break

        if hasModel:
            continue

        # if not found, brute search the other IDs
        for family in st[manu].keys():
            if family in families:
                continue

            for model in st[manu][family].keys():
                if match_model(model, title):
                    count += 1
                    hasModel = True
                    add_match(
                        matched,
                        st[manu][family][model],
                        lst
                    )
                    break

            if hasModel:
                break

    return count, matched

