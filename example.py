#!/usr/bin/env python
""" converts f5 stanza config blocks to JSON

    Thu Jul 22 00:09:24 2021

    __author__ = 'Jose Lima'
"""

from json import dumps
from limatools import parse_policy

lines = """ltm virtual export_me {
    description "This is for export.  Export this description."
    destination 10.1.30.30:https
    ip-protocol tcp
    mask 255.255.255.255
    policies {
        linux-high { }
    }
    pool test-pool
    profiles {
    ASM_asm-policy-linux-high-security_policy { }
        clientssl {
        context clientside
        }
        http { }
        serverssl {
        context serverside
        }
        tcp-lan-optimized {

        context serverside
        }
        tcp-wan-optimized {
        context clientside
        }
        websecurity { }
    }
    source 0.0.0.0/0
    source-address-translation {
        type automap
    }
    translate-address enabled
    translate-port enabled
    vs-cursor 2
}
"""


# print(dumps(parse_policy(lines, b64=True), indent=2))
print(dumps(parse_policy(lines), indent=2))

# parsed = {"ltm:virtual": {}}
# for block in blocks:
#     p = parse_policy(block)
#     parsed.setdefault("ltm:virtual", {}).update(p["ltm:virtual"])

# print(dumps(parsed, indent=2))
