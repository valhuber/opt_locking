# coding: utf-8
from sqlalchemy import Boolean, Column, DECIMAL, Date, Float, ForeignKey, ForeignKeyConstraint, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
from safrs import jsonapi_attr

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# mypy: ignore-errors

from safrs import SAFRSBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *
########################################################################################################################


class Category_mix():
    pass


class Customer_mix():
    pass


class CustomerDemographic_mix():
    pass


class Department_mix():
    pass

class Location_mix():
   pass


class Product_mix():
    pass


class Region_mix():
    pass


class SampleDBVersion_mix():
    pass


class Shipper_mix():
    pass


class Supplier_mix():
    pass


class Territory_mix():
    pass

class Union_mix():
    pass


t_sqlite_sequence = Table(
    'sqlite_sequence', metadata,
    Column('name', NullType),
    Column('seq', NullType)
)


class Employee_mix():
    """
    Add virtual attributes here, to preserve over rebuild-from-model.

    Not working, though adding abstract might help... to be explored.
    """

    # add derived attribute: https://github.com/thomaxxl/safrs/blob/master/examples/demo_pythonanywhere_com.py
    @jsonapi_attr
    def proper_salary(self):  # type: ignore [no-redef]
        import database.models as models
        if isinstance(self, models.Employee):
            import decimal
            rtn_value = self.Salary
            rtn_value = decimal.Decimal('1.25') * rtn_value
            self._proper_salary = int(rtn_value)
            return self._proper_salary
        else:
            print("class")
            return db.Decimal(10)

    @proper_salary.setter
    def proper_salary(self, value):  # type: ignore [no-redef]
        self._proper_salary = value
        print(f'_proper_salary={self._proper_salary}')
        pass

    ProperSalary = proper_salary  # fails to be recognized as API property

class EmployeeAudit_mix():
    pass

class EmployeeTerritory_mix():
    pass

class Order_mix():
    pass

class OrderDetail_mix():
    pass