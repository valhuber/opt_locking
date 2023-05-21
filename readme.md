Optimistic locking is a valuable feature.  It is a blocker for companies who might otherwise migrate to API Logic Server from CA Live API Creator.  [This project](https://github.com/valhuber/opt_locking) explores approaches. 

&nbsp;

## TL;DR - Compute virtual attribute `_check_sum_` in `loaded_as_persistent`, verify on save

We want **virtual attributes** that can be computed on retrieval, not stored in the database, and attached to API rows as they are sent / returned from the client.  The returned `_check_sum_` can then be tested (in logic) to make sure it was unchanged.

1. SQLAlchemy provides the `loaded_as_persistent` event, enabling us to compute the `check_sum`, store it in the row, and check it on update.

    * Storing it in the row is critical because we do not want to maintain server state between client calls.  Nor do we want to force customers to include special fields in their schema.<br><br>

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

1. In `database/models.py` -- **inline**, in `Employees`
    * **seems to work??**
2. In `database/models.py` -- in super class `SafrsBaseX`
    * not working
3. In `database/customize_models.py`
    * not working

## 3. Clients include read-checksum in `Patch`

**Important:** Admin App is not sending unchanged attributes; we must convince it to send the CheckSum.

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
            "Salary": 97000,
            "_chx_sum_property": 157,
            "_check_sum_property": 6785985870086950264,
            "_check_mix_property": 27,
            "ChkSum": 157,
            "CheckSum": 6785985870086950264,
            "CheckMix": 27,
            "Proper_Salary": 50000,
            "Id": 5},
        "type": "Employee",
        "id": 5
    }
}'
```

Not visible on update: ChkSum, CheckMix
Visible: CheckSum

Or, swagger payload:

```json
{
    "data": {
        "attributes": {
            "Salary": 200000,
            "_chx_sum_property": 157,
            "_check_sum_property": 57,
            "_check_mix_property": 27,
            "ChkSum": 157,
            "CheckSum": 6785985870086950000,
            "CheckMix": 27,
            "Proper_Salary": 50000,
            "Id": 5},
        "type": "Employee",
        "id": 5
    }
}
```

Get (6785985870086950264):

```
curl -X 'GET' \
  'http://localhost:5656/api/Employee/5/?fields%5BEmployee%5D=Id%2CLastName%2CFirstName%2CTitle%2CTitleOfCourtesy%2CBirthDate%2CHireDate%2CAddress%2CCity%2CRegion%2CPostalCode%2CCountry%2CHomePhone%2CExtension%2CNotes%2CReportsTo%2CPhotoPath%2CEmployeeType%2CSalary%2CWorksForDepartmentId%2COnLoanDepartmentId%2CUnionId%2CDues%2C_check_sum_%2CCheckSum%2C__proper_salary__%2CProperSalary%2C_chx_sum_%2CChxSum' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/vnd.api+json'
```
&nbsp;


Test unmodelled attr -- ToDict_Checksum is not marshalled into row on update

```
curl -X 'PATCH' \
  'http://localhost:5656/api/Employee/5/' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/json' \
  -d '{
    "data": {
        "attributes": {
            "Salary": 200000,
            "_chx_sum_property": 157,
            "_check_sum_property": 6785985870086950264,
            "_check_mix_property": 27,
            "ToDict_Checksum": 42,
            "ChkSum": 157,
            "CheckSum": 57,
            "CheckMix": 27,
            "Proper_Salary": 50000,
            "Id": 5},
        "type": "Employee",
        "id": 5
    }
}'
```

&nbsp;

Also verify works with alias Entity / Attr names, using Category (-4130312969102546939)

```
curl -X 'GET' \
  'http://localhost:5656/api/Category/1/?fields%5BCategory%5D=Id%2CCategoryName%2CDescription%2CClient_id%2C_check_sum_%2CCheckSum' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/vnd.api+json'
```

```
curl -X 'PATCH' \
  'http://localhost:5656/api/Category/1/' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/json' \
  -d '{
  "data": {
    "attributes": {
      "Description": "x",
      "CheckSum": "-4130312969102546939"
    },
    "type": "Category",
    "id": "1"
  }
}'
```


## 4. Check `_check_sum_` in logic

We can test the various strategies, as follows:

1. Set breakpoint as shown in `logic/declare_logic.py`
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

where `database/models_mix.Employee_mix` is a user-alterable (not rebuilt) file that defines virtual attributes (`_check_mix_`).  

However, this ***does not appear to work*** for `@jsonapi_attr` -- it is not called when retrieving rows, and `ProperSalary` does not appear in swagger.  

Also, a flawed in that the dynamic `@add_method(cls)` is not generic... what `cls` should be passed to add_method?

Unclear how to resolve.

**Explored in this hand-altered prototype.**

&nbsp;

### Option 3: declare in super type

Got error: `metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases`


