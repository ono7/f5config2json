1. add lname field for case insensite match, index
2. add timestamp for lastupdate

```python
from datetime import datetime
 c.test.test.insert({'db_added': datetime.utcnow()})
```

3. add "gtm or ltm" to `_id` e.g. `{"_id": "type:gtm /Common/blah"}`

4. figure out current db issues

- mongoshell:
  db.stats() -> returns db stats
  db.getCollecctionsName() -> returns all collections
  db.getCollection('colection_name').stats() -> returns stats about a collection

```
The .find() method takes additional keyword arguments. One of them is
no_cursor_timeout which you need to set to True

cursor = collection.find({}, no_cursor_timeout=True) You don't need to write
your own generator function. The find() method returns a generator like object.

for c in cursor:
  print(c)
```
