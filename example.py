#!/usr/bin/env python
""" converts f5 stanza config blocks to JSON

    Thu Jul 22 00:09:24 2021

    __author__ = 'Jose Lima'
"""
# TODO: 07/31/2021 | fix issue where k, v, k= "some long string with spaces"
# TODO: 07/31/2021 | add key filters so they are denormalized ahead of time

from json import dumps
from tojson import parse_policy
import logging

logging.basicConfig(
    format="%(levelname)s %(asctime)s %(name)s : %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
    filename="error.log",
    filemode="w",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)
# logger.error(e, exc_info=True)


ltm_re = r"(?sm)((^ltm rule.*?^\}\n\})|^\w.*?(?=^\w|\Z))"

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
    test "
    translate-address enabled
    translate-port enabled
    vs-cursor 2
}
"""

irule = """ltm rule /Common/test {
# test
when this {
  isthis working? thest
 }
}
}
"""

lines3 = """ltm virtual "/Common/Spaced out" {
    description "this line is broken.  
Export this description. 
"
    destination 10.1.30.30:https
}"""

# TODO: 07/31/2021 | fix "key a b c" value
lines = """ltm pool /test/context {
    description "testing context"
    load-balancing-mode least-connections-members
    members {
        /common/test/member {
            address 1.1.1.1
            monitor /test/monitor and /test/monitor/2
        }
    }
    service-downaction reset
}
"""
# print(dumps(parse_policy(lines, b64=True), indent=2))
data = [lines, lines3]
encode = ["ltm:rule"]
for d in data:
    try:
        print(dumps(parse_policy(d, encode_this=encode, b64=True), indent=2))
    except:
        logger.warning(d, exc_info=True)

# parsed = {"ltm:virtual": {}}
# for block in blocks:
#     p = parse_policy(block)
#     parsed.setdefault("ltm:virtual", {}).update(p["ltm:virtual"])

# print(dumps(parsed, indent=2))
