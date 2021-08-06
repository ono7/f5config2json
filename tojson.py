#!/usr/bin/env python
""" Utilities for implementing stacks to track stanza config objects
    and generate JSON output

    e.g.

    virtual-server /Common/best_vs {
        attributes {
            key1 value1
            key2 value2
        }
        empty-definition { }
    }


    Fri Jul 23 13:11:27 2021

    __author__ = 'Jose Lima'

"""

import re
from base64 import b64encode
from typing import Tuple, List, Any
from context import kv_context, storage_context

### rock stars ###


class Storage:
    """Storage container
    relies on results from is_parent function to create
    an appropiate data structure for the type of node
    currently in the stack
    """

    def __init__(self, k1: str = None, k2: Any = None):
        self.k1 = k1
        self.k2 = k2
        self.parent = None
        self.root = None
        if isinstance(k2, list):
            self.storage = {k1: []}
        elif isinstance(k2, dict):
            self.storage = {}
        elif isinstance(k2, str):
            self.storage = {k1: {k2: {}}}
        else:
            self.storage = {k1: {}}

    def update(self, data: dict) -> None:
        if isinstance(self.k2, str):
            self.storage[self.k1][self.k2].update(data)
        elif isinstance(self.k2, list):
            self.storage[self.k1].append(data)
        elif isinstance(self.k2, dict):
            self.storage.update(data)
        else:
            self.storage[self.k1].update(data)

    def get_store(self):
        return self.storage


class Stack:
    """ returns a stack that keeps track of stanza schema start and end block"""

    def __init__(self):
        self.stack = []
        self.state = False
        self.last = None
        self.current = None
        self.len = 0
        self.by_who = None

    def update_state(self, line: str) -> bool:
        self.last = self.current
        self.current = line
        if self.current.endswith("{"):
            self.stack.append("{")
            self.len += 1
            self.by_who = line
        # elif self.current.strip() == "}":
        elif self.current == "}":
            self.stack.pop()
            self.len -= 1
            if self.len == 0:
                self.state = True
                self.by_who = line
        return self.state

    def is_balanced(self):
        return self.state

    def get_stack(self):
        return self.stack


### regex compile ###

# re_keys below covers cases where there are spaces in "/Common/space here"
re_keys = re.compile(r'("[^{}]+"|[^{} ]+)')

store_contex = {"ltm:virtual": ["stuff"]}

## policy helpers ##


def clean_data_chunk(chunk: str) -> str:
    """cleans up a F5 configuration chunk

    clean_empty_lines: removes any empty lines only [\n] is supported

    clean_broken_line: there are cases where the F5 config has lines that are
        broken specially seen in long quoted strings, this fixes it by replacing
        the trailing space and newline with a single space (this might require more testing)
    """
    clean_empty_lines = re.compile(r"[\n]+")
    clean_broken_line = re.compile(r"\s+\n")
    c = chunk.strip()
    c = clean_empty_lines.sub("\n", c)
    return clean_broken_line.sub(" ", c)


def create_new_objects(
    line: str, storage_stack: object, obj_stack: object, context: str = None
) -> object:
    """creates new storage and this_stack objects
    if the obj_stack contains a previous object
    this new_node object's parent attribute is set
    this allows a direct update once we encounter and end of a stanza block

    context: root key for this config block

    """
    new_node = Storage(*is_parent(line, context=context))
    if len(storage_stack) > 0:
        new_node.parent = storage_stack[-1]
    storage_stack.append(new_node)
    new_stack = Stack()
    new_stack.update_state(line)
    obj_stack.append(new_stack)
    return new_stack


### parsers ###


def parse_singleton(data: str) -> object:
    """parse single line objects
    e.g.
        apm client-packaging /Common/client-packaging
    """
    new_node = Storage(*is_parent(data))
    return new_node.get_store()


def is_parent(line: str, context: str = None) -> Tuple:
    """if the line ends with  `word {`, this represents the start of a
    new objectk if a line is multiple words:
        `level1 word2 /Common/level2 {}`
    we pair the first 2 words to represent the parent key
    and return a nested structure:
        -> {"level1:word2" : {"/Common/level2" : {}}
    other wise if the line is `level1 {}`
        -> {"level1" : {}}
    this function works together with Storage to create the correct
    data structure for the current object
    """
    if line == "{":
        return None, {}
    results = re_keys.findall(line)
    if results:
        if len(results) > 1:
            level2 = results.pop(-1)
            level1 = ":".join(results)
            try:
                level2 = storage_context.get(context).get(level2, level2)
                return level1, level2
            except:
                return level1, level2
        # if we got this far we expect level2 to be type None
        # we only need to do a level1 lookup on the storage_context to see if we
        # should return a list, or it self as a default value type(str) other
        # wise Storage class will take care of choosing the correct structure for this object
        level2 = None
        try:
            level1 = storage_context.get(context).get(level1, level1)
            return level1, level2
        except:
            level1 = results[0]
        try:
            level2 = storage_context.get(context).get(level1, level2)
            return level1, level2
        except:
            return level1, level2


def get_context(line: str) -> str:
    """get context for for this object
    e.g.
        ltm pool /common/awesome/pool { <- context = "ltm:pool"
            somekey somevalue
        }
    """
    if line.strip() == "{":
        return "no_root_key"
    results = re_keys.findall(line)
    if results:
        if len(results) > 1:
            _ = results.pop(-1)
            root_key = ":".join(results)
            return root_key
        root_key = results[0]
    return root_key


def parse_policy(policy: str, b64: bool = False, encode_this: list = None) -> object:
    """parse a stanza object from f5 and return python dict

    policy: a block of F5 config, e.g. parent { attribute value }
        one probably should regex-fu the blocks out of a config text document
        before sending them here

    b64: optionaly embed original config block encoded in base64
        parse_policy(data, b64=True)

    encode_this: list of object parent keys e.g. "ltm:rule" to by pass parsing
        and skip to encoding. avoids building complex expressions for data that
        is not necessary for migration correlation.
    """
    if not encode_this:
        encode_this = []
    lines = clean_data_chunk(policy).splitlines()
    if len(lines) == 1:
        return parse_singleton(lines[0])
    storage_stack: List[object] = []
    obj_stack: List[object] = []
    context = get_context(lines[0])
    for line in lines:
        line = line.strip()
        # if 'this' in line:
        #     __import__("ipdb").set_trace(context=5)
        if line == "}" and this_stack.is_balanced():
            if storage_stack[-1].parent and len(storage_stack) != 1:
                storage_stack[-1].parent.update(storage_stack[-1].get_store())
                storage_stack.pop()
                this_stack = obj_stack.pop()
            continue
        if line == "}":
            this_stack.update_state(line)
            if this_stack.is_balanced() and len(obj_stack) != 0:
                this_stack = obj_stack.pop()
                if storage_stack[-1].parent and len(storage_stack) != 1:
                    storage_stack[-1].parent.update(storage_stack[-1].get_store())
                    storage_stack.pop()
                continue
        if line.endswith("{"):
            this_stack = create_new_objects(
                line, storage_stack, obj_stack, context=context
            )
            if storage_stack[-1].k1 in encode_this:
                storage_stack[-1].update(
                    {"b64": f"{b64encode(policy.encode()).decode()}"}
                )
                return storage_stack[0].get_store()
            continue
        storage_stack[-1].update(kv_context(line, context=context))
    if b64:
        storage_stack[0].update({"b64": f"{b64encode(policy.encode()).decode()}"})
    # TODO: 08/05/2021 | implement device id
    storage_stack[0].update({"from_device_id": "mydevice01"})
    return storage_stack[0].get_store()
