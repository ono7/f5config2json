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

# ltm_list_keys = [
#     "rules",
#     "variables",
#     "rows",
#     "\d+ {",
#     "attributes",
#     "assertion-consumer-services",
# ]
# default_list_key_pre = sorted(ltm_list_keys, key=len, reverse=True)
# default_list_key_pre = "|".join(default_list_key_pre)
# default_list_key_re = re.compile(f"({default_list_key_pre})")

re_keys = re.compile(r'("[^{}]+"|[^{} ]+)')

### context aware functions to parse k, v pairs inside stanza block

# TODO: 07/30/2021 | fix some repetitive code at some point to steamline creating a new context function


def context_ltm_pool(line: str):
    monitor = re.compile(r"(monitor) (.*)")
    if line.strip().startswith("monitor"):
        try:
            k, v = monitor.search(line).groups()
            if v:
                return {k: v.split(" and ")}
        except:
            return {"monitor": []}

    if line.endswith('"'):
        k, v = default_quotes.search(line).groups()
        return {k: v}
    if re.findall(r"{.*}", line):
        k, v = default_list_kv.search(line).groups()
        if v != " ":
            v = v.split()
        else:
            v = []
        return {k: v}
    try:
        k, v = default_kv.findall(line)
        return {k: v}
    except ValueError:
        # deals with single items in a line that are not k, v pairs
        k = default_kv.findall(line)
        return {k[0]: None}


def context_default(line: str):
    if line.endswith('"'):
        k, v = default_quotes.search(line).groups()
        return {k: v}
    if re.findall(r"{.*}", line):
        k, v = default_list_kv.search(line).groups()
        if v != " ":
            v = v.split()
        else:
            v = []
        return {k: v}
    try:
        k, v = default_kv.findall(line)
        return {k: v}
    except ValueError:
        # deals with single items in a line that are not k, v pairs
        k = default_kv.findall(line)
        return {k[0]: None}


### context mappings ###

# returns a context aware funtion that deals with parsing a "key value" line item
# if none is found, the implementation should return a default in this case  context_default()
line_context_pool = {"ltm:pool": context_ltm_pool}

# this lookup provides context aware data containers, default is type -> dict
# so this mapping is really only good for places where we need a list instead of a {}
storage_context = {
    "ltm:policy": {"rules": []},
    "apm:sso:saml-sp-connector": {"assertion-consumer-services": []},
    "apm:policy:agent:variable-assign": {"variables": []},
    "apm:policy:customization-group": {"images": []},
    "apm:profile:access": {"log-settings": []},
    "apm:sso:form-based": {"form-field": []},
    "sys:application:service": {"rows": []},
}


def kv_context(line: str, context: str) -> dict:
    """gets a context aware function from line_context_pool mapping
    parses the line and returns the values as {k: v}
    """
    parser = line_context_pool.get(context, context_default)
    return parser(line)
