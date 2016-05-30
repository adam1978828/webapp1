from semantics3 import Products


# Set up a client to talk to the Semantics3 API using your Semantics3 API Credentials
# Go to https://www.semantics3.com/, register, choose the appropriate price plan
# Than in dashboard get your API key and API secret number and enter them here to replace these
sem3 = Products(
    api_key="SEM3A9A3C5F380F9F62A6974C882CB5AD1DC",
    api_secret="OGZhYjA0OWM1NGU1OTZkODhmOGE2NTViNDkxMGRiMjQ"
)


def get_upc(upc):
    sem3.products_field("upc", upc)
    results = sem3.get_products()
    return results if results[u'code'] == u'OK' else None


if __name__ == '__main__':
    print get_upc('025192223280')
