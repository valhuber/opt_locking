Optimistic locking is a valuable feature.  It is a blocker for companies who might otherwise migrate to API Logic Server from CA Live API Creator.  [This project](https://github.com/valhuber/opt_locking) explores approaches. 

&nbsp;

## TL;DR - Compute virtual attribute `_check_sum_` in `loaded_as_persistent`, verify on save

We want **virtual attributes** that can be computed on retrieval, not stored in the database, and attached to API rows as they are sent / returned from the client.  The returned `_check_sum_` can then be tested (in logic) to make sure it was unchanged.

1. SQLAlchemy provides the `loaded_as_persistent` event, enabling us to compute the `check_sum`, store it in the row, and check it on update.

    * Storing it in the row is critical because we do not want to maintain server state between client calls.  Nor do we want to force customers to include special fields in their schema.

2. For virtual attributes, we can use `@jsonapi_attr`.

3. Clients must include the read-checksum (virtual attribute) in the `Patch`

4. Logic will verify that the read-checksum equals the current-checksum

&nbsp;

## 1. Event `loaded_as_persistent` (works)

[This event](https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.SessionEvents.loaded_as_persistent) looks like this (see `logic/sys_logic.py`):

```python
        elif isinstance(instance, models.Employee):
            logger.debug(f'{__name__} - setting CheckSum in EMP instance: {instance}')
            setattr(instance, "_chx_sum_property", 155)
            setattr(instance, "_check_sum_property", 55)
            # instance.CheckSum = 55  # later, figure out algorithm for this
```

We set up the listener in `api_logic_server_run.py`.

&nbsp;

### Alternative: compute _check_sum_ in attr getter

This might also work...?

&nbsp;

## 2. safrs `@jsonapi_attr` (works - where to define?)

This provides a mechanism to define attributes as part of the row (so it sent to / returned from the client), and not saved to disk.  

The question is: ***where can this declaration be made.***  Options are discussed below.

&nbsp;

### Chosen Option: Add Dynamic Method

See `add_method.py`, courtesy: https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6

Appears to work, most preferable since requires no change to models.py (so can rebuild-from-database).

Though, `_check_sum_property` appears as an attr in json response.  

> This can be resolved by overriding `SAFRSBase`, as illustrated in `database/models.py`.

Additional choices remain - *where* to define:

1. In `database/models.py` -- **inline**, in `Employees` **<=== seems to work??**
2. In `database/models.py` -- in super class `SafrsBaseX` (test requires changes, not done)
3. In `database/customize_models.py`

## 3. Clients include read-checksum in `Patch`

To simulate the client:
1. Set the breakpoint noted below, and 
2. Use cURL (easiest) or swagger:

```curl
curl -X 'PATCH' \
  'http://localhost:5656/api/Employee/5/' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/json' \
  -d '{
    "data": {
        "attributes": {
            "Salary": 200000,
            "_chx_sum_property": 156,
            "_check_sum_property": 56,
            "ChkSum": 157,
            "CheckSum": 57,
            "Proper_Salary": 50000,
            "Id": 5},
        "type": "Employee",
        "id": 5
    }
}'
```

Or, swagger payload:

```json
{
    "data": {
        "attributes": {
            "Salary": 200000,
            "_chx_sum_property": 156,
            "_check_sum_property": 56,
            "ChkSum": 157,
            "CheckSum": 57,
            "Proper_Salary": 50000,
            "Id": 5},
        "type": "Employee",
        "id": 5
    }
}
```

&nbsp;

## 4. Check `_check_sum_` in logic

We can test the various strategies, as follows:

1. Set breakpoint @205 in `logic/declare_logic.py`
2. Use Run Config `ApiLogicServer - No Security`
3. Simulate the client using the cURL above
4. Observe the logged values - the **inline** approach appears to work

```log
logic sees: chk_ChxSumProperty=155 chk_CheckSumProperty=57, chk_ChxSum=155, chk_CheckSum=57
```
&nbsp;

![No Virtual Attrs](images/patch-virtuals.png)

---

&nbsp;

## Appendix: Other Options Considered for `@json_attr` definition

Skip this for now, it just documents other rejected approaches.

&nbsp;

### Option 1: Declare in subclass (but fails in logic)

It would not be difficult to generate current models with the suffix `_base`, then sublcass all these models in a customer-alterable file, initially empty.  

However, this failed, since LogicBank uses simple mechanisms to find attributes and relationships.  This might be an extensive change.

&nbsp;

### Option 2: Declare in mixin (but safrs fails to recognize property)

Other approach is to generate models like this:

```python
class Employee(SAFRSBase, Base, models_mix.Employee_mix):
```

where `database/models_mix.Employee_mix` is a user-alterable (not rebuilt) file that defines virtual attributes.  

However, this ***does not appear to work*** for `@jsonapi_attr` -- it is not called when retrieving rows, and `ProperSalary` does not appear in swagger.  Likely user error.

**Explored in this hand-altered prototype.**
