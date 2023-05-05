from database import models
import logging
from safrs import jsonapi_attr
from sqlalchemy.orm import relationship, remote, foreign
from functools import wraps # This convenience func preserves name and docstring
import decimal as decimal

"""
    If you wish to drive models from the database schema,
    you can use this file to customize your schema (add relationships, derived attributes),
    and preserve customizations over iterations (regenerations of models.py).
"""

app_logger = logging.getLogger(__name__)

def add_method(cls):
  """
  decorator to add method to class
  https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
  """
  def decorator(func):
    @wraps(func) 
    def wrapper(self, *args, **kwargs): 
      return func(*args, **kwargs)
    setattr(cls, func.__name__, wrapper)
    # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
    return func # returning func means func can still be used normally
  return decorator

# add relationship: https://docs.sqlalchemy.org/en/13/orm/join_conditions.html#specifying-alternate-join-conditions
models.Employee.Manager = relationship('Employee', cascade_backrefs=True, backref='Manages',
                                       primaryjoin=remote(models.Employee.Id) == foreign(models.Employee.ReportsTo))
"""
added relationships appear in your api / swagger, automatically.

They must be manually added to your ui/admin/admin.yaml, e.g.

      - direction: tomany
        fks:
          - ReportsTo
        name: Manages
        resource: Employee
      - direction: toone
        fks:
        - ReportsTo
        name: Manager
        resource: Employee

"""


# add derived attribute: https://github.com/thomaxxl/safrs/blob/master/examples/demo_pythonanywhere_com.py
@add_method(models.Employee)
@jsonapi_attr
def __proper_salary__(self):  # type: ignore [no-redef]
    if isinstance(self, models.Employee):
        import decimal
        rtn_value = self.Salary
        rtn_value = decimal.Decimal('1.25') * rtn_value
        self._proper_salary = int(rtn_value)
        return self._proper_salary
    else:
        print("class")
        return None  # decimal.Decimal(10)

@add_method(models.Employee)
@__proper_salary__.setter
def __proper_salary__(self, value):  # type: ignore [no-redef]
    self._proper_salary = value
    print(f'_proper_salary={self._proper_salary}')
    pass

models.Employee.ProperSalary = __proper_salary__


@add_method(models.Employee)
@jsonapi_attr
def _chx_sum_(self):  # type: ignore [no-redef]
    if isinstance(self, models.Employee):
        try:
          return self._chx_sum_property
        except:
          print(f'{__name__}: no _chx_sum_ in {self}')
          return -1
    else:
        print("class")
        return None  # decimal.Decimal(10)

@add_method(models.Employee)
@_chx_sum_.setter
def _chx_sum_(self, value):  # type: ignore [no-redef]
    self._chx_sum_property = value
    print(f'_chx_sum_={self._chx_sum_property}')
    pass

models.Employee.ChxSum = _chx_sum_

app_logger.info("..database/customize_models.py: models.Employee.Manager(manages), Employee.ProperSalary")
