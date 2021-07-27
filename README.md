"""
converts f5 stanza config blocks to JSON

    Thu Jul 22 00:09:24 2021

    this is for cases where iControl REST is not possible...
    I wrote this with the intention to store the json output to mongodb
    keys containing '.' should be normilized etc...

    test:
        `python3 f5conf2json.py`

"""
