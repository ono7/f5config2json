#!/usr/bin/env python
""" context aware functions for dealing with F5 stanza blocks

    Thu Jul 29 14:35:30 2021

    __author__ = 'Jose Lima'

"""
import re

### one line parsers ###

default_quotes = re.compile(r"\b(\S+) (.*)")
default_kv = re.compile(r"\S+")
default_list_kv = re.compile(r"(\S+) {(?:([^{}]*))}")

re_keys = re.compile(r'("[^{}]+"|[^{} ]+)')

### default line parsers ###


def default_line_parse(line):
    """ default line parser, returns null for value if no match """
    try:
        k, v = default_kv.findall(line)
    except ValueError:
        # deals with single items in a line that are not k, v pairs
        k = default_kv.findall(line)[0]
        v = None
    return k, v


def default_line_list(line):
    """ deals with list type lines e.g. 'item { a b c }' """
    k, v = default_list_kv.search(line).groups()
    if v != " ":
        v = v.split()
    else:
        v = []
    return k, v


### context aware functions to parse k, v pairs ###


def context_ltm_pool(line: str):
    monitor = re.compile(r"(monitor) (.*)")
    if line.startswith("monitor"):
        try:
            k, v = monitor.search(line).groups()
            if v:
                v = v.split(" and ")
        except:
            return {"monitor": []}
    elif line.endswith('"'):
        k, v = default_quotes.search(line).groups()
    elif re.findall(r"{.*}", line):
        k, v = default_line_list(line)
    else:
        k, v = default_line_parse(line)
    return {k: v}


def context_default(line: str):
    if line.endswith('"'):
        k, v = default_quotes.search(line).groups()
    elif re.findall(r"{.*}", line):
        k, v = default_line_list(line)
    else:
        k, v = default_line_parse(line)
    return {k: v}


### context mappings ###

# returns a context aware funtion that deals with parsing a "key value" line item
# if none is found, the implementation should return a default in this case  context_default()
line_context_pool = {"ltm:pool": context_ltm_pool}

# this lookup provides context aware data containers, default is type -> dict
# this mapping is really only good for places where we need a list instead of a {}
storage_context = {
    "apm:sso:saml-sp-connector": {"assertion-consumer-services": []},
    "apm:policy:agent:variable-assign": {"variables": []},
    "apm:policy:customization-group": {"images": []},
    "apm:policy:policy-item": {"rules": []},
    "apm:profile:access": {"log-settings": []},
    "apm:sso:form-based": {"form-field": []},
    "apm:sso:saml": {"attributes": []},
    "sys:application:service": {"rows": []},
}


def kv_context(line: str, context: str) -> dict:
    """gets a context aware function from line_context_pool mapping
    parses the line and returns the values as {k: v}
    """
    parser = line_context_pool.get(context, context_default)
    return parser(line)
