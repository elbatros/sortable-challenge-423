from multiprocessing import Pool, freeze_support
from functools import partial, reduce
from collections import OrderedDict
import os
import json

from match import match_listings


class ProductTreeBuilder(object):
    def __init__(self):
        self.listings = []
        self.products = []
        self.st = {}

    # load json data
    def load_data(self, list_path, prod_path):
        with open(list_path) as f:
            for line in f:
                self.listings.append( json.loads(line) )

        with open(prod_path) as f:
            for line in f:
                self.products.append( json.loads(line) )

     # rearrange products into a shallow search hierarchy
    def make_st( self ):
        for prod in self.products:
            manu = prod.get('manufacturer').lower().strip()
            family = prod.get('family', 'no-family').lower().strip()
            model = prod.get('model').lower().strip()

            # keep the product name in original case
            name = prod.get('product_name').strip()

            if not manu in self.st:
                self.st[manu] = {}
            
            if family and not family in self.st[manu]:
                self.st[manu][family] = {}

            if model and not model in self.st[manu][family]:
                self.st[manu][family][model] = name

        # sort models reverse lexicographically as some are
        # prefixes of others
        for manu in self.st:
            for family in self.st[manu]:
                self.st[manu][family] = OrderedDict(sorted(self.st[manu][family].items(), reverse=True))

    # matches listings in parallel with Pool.map and
    # reduces to get final result
    def match( self ):
        return match_listings( self.listings, self.st)

        def reducer(a, b):
            for k, v in b[1].items():
                if k in a[1]:
                    a[1][k]['listings'].extend(b[1][k]['listings'])

            return (a[0] + b[0], a[1])

        cpus = os.cpu_count()
        if not cpus or cpus == 1:
            return match_listings( self.listings, self.st)

        num_listings = len( self.listings )
        chunk_size = num_listings // cpus
        self.listings = [
                self.listings[i:i + chunk_size] for i in range(0, num_listings, chunk_size)
        ]

        with Pool() as pool:
            results = pool.map(
                partial(match_listings, st=self.st),
                self.listings
            )
            results = reduce(reducer, results)
            return results


if __name__ == '__main__':
    # apparently needed for processing on Windows
    freeze_support()

    pb = ProductTreeBuilder()
    pb.load_data('listings.txt', 'products.txt')
    pb.make_st()

    count, matched = pb.match()

    for match in matched.values():
        # ensure ascii prevents default behaviour of converting
        # unicode strings in dict to ascii
        print(json.dumps(match, ensure_ascii=False))

