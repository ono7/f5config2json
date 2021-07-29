<!---->TODO: 07/29/2021 | create context for "ltm:virtuals", fix rules from list of dicts to list

fix rule parser so that list items are not kv pairs
"rules": [
{
"/common/test" : null
}
]

should be:

"rules" : [
"/common/test"
]

"images, variables, rows" should be a list
