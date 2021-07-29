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


### this searches looks for values that would construct a {k : []} container ###
ltm_list_keys = [
    # "rules",
    "images",
    "variables",
    "rows",
    "log-settings",
    "\d+ {",
    "attributes",
    "assertion-consumer-services",
]
default_list_key_pre = sorted(ltm_list_keys, key=len, reverse=True)
default_list_key_pre = "|".join(default_list_key_pre)
default_list_key_re = re.compile(f"({default_list_key_pre})")

re_keys = re.compile(r'("[^{}]+"|[^{} ]+)')

### context aware definitions based on root key name ###


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
        k, v = default_list.search(line).groups()
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


line_context_pool = {"ltm:pool": context_ltm_pool}


def kv_context(line: str, context: str):
    parser = line_context_pool.get(context, context_default)
    return parser(line)
