# coding: utf-8
# from typing import @override
from sqlalchemy import Boolean, Column, DECIMAL, Date, Float, ForeignKey, ForeignKeyConstraint, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base


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

import database.models_mix as models_mix

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

from safrs import jsonapi_attr
from abc import ABC
class SAFRSBaseX(SAFRSBase):
    """ injects to_dict() to remove _proper_salary_, and compute CheckSum """

    __abstract__ = True  # utter magic!!

    # @override
    def to_dict(self, *args, **kwargs):
        """
        Create a dictionary with all the instance "attributes"
        this method will be called by SAFRSJSONEncoder to serialize objects

        :return: dictionary with jsonapi attributes
        """
        result = {}
        remove_proper_salary = False
        for key, value in self._s_jsonapi_attrs.items():
            if remove_proper_salary and key.startswith("_") and key.endswith("_"):
                pass  # eg, remove __proper_salary__, not called on update
            else:
                result[key] = value
        return result  # self._s_jsonapi_attrs for overridden behavior

    #   explore adding checksum generically
    # add derived attribute: https://github.com/thomaxxl/safrs/blob/master/examples/demo_pythonanywhere_com.py
    # @add_method(cls)
    @jsonapi_attr
    def _check_mix_(self):  # type: ignore [no-redef]
        if hasattr(self, "_check_mix_property"):
            return self._check_mix_property
        else:
            # print("class")
            return None  # decimal.Decimal(10)

    # @add_method(cls)
    @_check_mix_.setter
    def _check_mix_(self, value):  # type: ignore [no-redef]
        self._check_mix_property = value
        print(f'_check_mix_property = {self._check_mix_property}')
        pass

    CheckMix = _check_mix_
    
    


class Category(SAFRSBaseX, Base):
    __tablename__ = 'CategoryTableNameTest'
    _s_collection_name = 'Category'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    CategoryName = Column(String(8000))
    Description = Column(String(8000))
    Client_id = Column(Integer)


class Customer(SAFRSBase, Base):
    __tablename__ = 'Customer'
    _s_collection_name = 'Customer'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(String(8000), primary_key=True)
    CompanyName = Column(String(8000))
    ContactName = Column(String(8000))
    ContactTitle = Column(String(8000))
    Address = Column(String(8000))
    City = Column(String(8000))
    Region = Column(String(8000))
    PostalCode = Column(String(8000))
    Country = Column(String(8000))
    Phone = Column(String(8000))
    Fax = Column(String(8000))
    Balance = Column(DECIMAL)
    CreditLimit = Column(DECIMAL)
    OrderCount = Column(Integer, server_default=text("0"))
    UnpaidOrderCount = Column(Integer, server_default=text("0"))
    Client_id = Column(Integer)
    allow_client_generated_ids = True

    OrderList = relationship('Order', cascade_backrefs=True, backref='Customer')


class CustomerDemographic(SAFRSBase, Base):
    __tablename__ = 'CustomerDemographic'
    _s_collection_name = 'CustomerDemographic'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(String(8000), primary_key=True)
    CustomerDesc = Column(String(8000))
    allow_client_generated_ids = True


class Department(SAFRSBase, Base):
    __tablename__ = 'Department'
    _s_collection_name = 'Department'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    DepartmentId = Column(ForeignKey('Department.Id'))
    DepartmentName = Column(String(100))

    # see backref on parent: Department = relationship('Department', remote_side=[Id], cascade_backrefs=True, backref='DepartmentList')

    Department = relationship('Department', remote_side=[Id], cascade_backrefs=True, backref='DepartmentList')  # special handling for self-relationships
    EmployeeList = relationship('Employee', primaryjoin='Employee.OnLoanDepartmentId == Department.Id', cascade_backrefs=True, backref='Department')
    EmployeeList1 = relationship('Employee', primaryjoin='Employee.WorksForDepartmentId == Department.Id', cascade_backrefs=True, backref='Department1')


class Location(SAFRSBase, Base):
    __tablename__ = 'Location'
    _s_collection_name = 'Location'  # type: ignore
    __bind_key__ = 'None'

    country = Column(String(50), primary_key=True)
    city = Column(String(50), primary_key=True)
    notes = Column(String(256))
    allow_client_generated_ids = True

    OrderList = relationship('Order', cascade_backrefs=True, backref='Location')


class Product(SAFRSBase, Base):
    __tablename__ = 'Product'
    _s_collection_name = 'Product'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    ProductName = Column(String(8000))
    SupplierId = Column(Integer, nullable=False)
    CategoryId = Column(Integer, nullable=False)
    QuantityPerUnit = Column(String(8000))
    UnitPrice = Column(DECIMAL, nullable=False)
    UnitsInStock = Column(Integer, nullable=False)
    UnitsOnOrder = Column(Integer, nullable=False)
    ReorderLevel = Column(Integer, nullable=False)
    Discontinued = Column(Integer, nullable=False)
    UnitsShipped = Column(Integer)

    OrderDetailList = relationship('OrderDetail', cascade_backrefs=True, backref='Product')


class Region(SAFRSBase, Base):
    __tablename__ = 'Region'
    _s_collection_name = 'Region'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    RegionDescription = Column(String(8000))


class SampleDBVersion(SAFRSBase, Base):
    __tablename__ = 'SampleDBVersion'
    _s_collection_name = 'SampleDBVersion'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    Notes = Column(String(800))


class Shipper(SAFRSBase, Base):
    __tablename__ = 'Shipper'
    _s_collection_name = 'Shipper'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    CompanyName = Column(String(8000))
    Phone = Column(String(8000))


class Supplier(SAFRSBase, Base):
    __tablename__ = 'Supplier'
    _s_collection_name = 'Supplier'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    CompanyName = Column(String(8000))
    ContactName = Column(String(8000))
    ContactTitle = Column(String(8000))
    Address = Column(String(8000))
    City = Column(String(8000))
    Region = Column(String(8000))
    PostalCode = Column(String(8000))
    Country = Column(String(8000))
    Phone = Column(String(8000))
    Fax = Column(String(8000))
    HomePage = Column(String(8000))


class Territory(SAFRSBase, Base):
    __tablename__ = 'Territory'
    _s_collection_name = 'Territory'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(String(8000), primary_key=True)
    TerritoryDescription = Column(String(8000))
    RegionId = Column(Integer, nullable=False)
    allow_client_generated_ids = True

    EmployeeTerritoryList = relationship('EmployeeTerritory', cascade_backrefs=True, backref='Territory')


class Union(SAFRSBase, Base):
    __tablename__ = 'Union'
    _s_collection_name = 'Union'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    Name = Column(String(80))

    EmployeeList = relationship('Employee', cascade_backrefs=True, backref='Union')


t_sqlite_sequence = Table(
    'sqlite_sequence', metadata,
    Column('name', NullType),
    Column('seq', NullType)
)


class Employee(SAFRSBaseX, Base):  # explore using SafrsBaseX (brings in _check_mix_)
    """
    This fails as a mixin 
    
    but works by enabling in-class code below
    """
    __tablename__ = 'Employee'
    _s_collection_name = 'Employee'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    LastName = Column(String(8000))
    FirstName = Column(String(8000))
    Title = Column(String(8000))
    TitleOfCourtesy = Column(String(8000))
    BirthDate = Column(String(8000))
    HireDate = Column(String(8000))
    Address = Column(String(8000))
    City = Column(String(8000))
    Region = Column(String(8000))
    PostalCode = Column(String(8000))
    Country = Column(String(8000))
    HomePhone = Column(String(8000))
    Extension = Column(String(8000))
    Notes = Column(String(8000))
    ReportsTo = Column(Integer, index=True)
    PhotoPath = Column(String(8000))
    EmployeeType = Column(String(16), server_default=text("Salaried"))
    Salary = Column(DECIMAL)
    WorksForDepartmentId = Column(ForeignKey('Department.Id'))
    OnLoanDepartmentId = Column(ForeignKey('Department.Id'))
    UnionId = Column(ForeignKey('Union.Id'))
    Dues = Column(DECIMAL)

    # see backref on parent: Department = relationship('Department', primaryjoin='Employee.OnLoanDepartmentId == Department.Id', cascade_backrefs=True, backref='EmployeeList')
    # see backref on parent: Union = relationship('Union', cascade_backrefs=True, backref='EmployeeList')
    # see backref on parent: Department1 = relationship('Department', primaryjoin='Employee.WorksForDepartmentId == Department.Id', cascade_backrefs=True, backref='EmployeeList_Department1')

    EmployeeAuditList = relationship('EmployeeAudit', cascade_backrefs=True, backref='Employee')
    EmployeeTerritoryList = relationship('EmployeeTerritory', cascade_backrefs=True, backref='Employee')
    OrderList = relationship('Order', cascade_backrefs=True, backref='Employee')

    # enable this code to expose check_sum as virtual attribute
    from safrs import jsonapi_attr
    # add derived attribute: https://github.com/thomaxxl/safrs/blob/master/examples/demo_pythonanywhere_com.py
    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        if isinstance(self, Employee):
            try:
              return self._check_sum_property
            except:
              print(f'{__name__}: no _check_sum_property in {self}')
              return -1
        else:
            print("class")
            return None  # decimal.Decimal(10)

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value
        # setattr(self, "__check_sum", value)
        # print(f'_check_sum_property={self._check_sum_property}')
        pass

    CheckSum = _check_sum_
    
    

class EmployeeAudit(SAFRSBase, Base):
    __tablename__ = 'EmployeeAudit'
    _s_collection_name = 'EmployeeAudit'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    Title = Column(String)
    Salary = Column(DECIMAL)
    LastName = Column(String)
    FirstName = Column(String)
    EmployeeId = Column(ForeignKey('Employee.Id'))
    CreatedOn = Column(Text)

    # see backref on parent: Employee = relationship('Employee', cascade_backrefs=True, backref='EmployeeAuditList')


class EmployeeTerritory(SAFRSBase, Base):
    __tablename__ = 'EmployeeTerritory'
    _s_collection_name = 'EmployeeTerritory'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(String(8000), primary_key=True)
    EmployeeId = Column(ForeignKey('Employee.Id'), nullable=False)
    TerritoryId = Column(ForeignKey('Territory.Id'))
    allow_client_generated_ids = True

    # see backref on parent: Employee = relationship('Employee', cascade_backrefs=True, backref='EmployeeTerritoryList')
    # see backref on parent: Territory = relationship('Territory', cascade_backrefs=True, backref='EmployeeTerritoryList')


class Order(SAFRSBase, Base):
    __tablename__ = 'Order'
    _s_collection_name = 'Order'  # type: ignore
    __bind_key__ = 'None'
    __table_args__ = (
        ForeignKeyConstraint(['Country', 'City'], ['Location.country', 'Location.city']),
    )

    Id = Column(Integer, primary_key=True)
    CustomerId = Column(ForeignKey('Customer.Id'), nullable=False, index=True)
    EmployeeId = Column(ForeignKey('Employee.Id'), nullable=False, index=True)
    OrderDate = Column(String(8000))
    RequiredDate = Column(Date)
    ShippedDate = Column(String(8000))
    ShipVia = Column(Integer)
    Freight = Column(DECIMAL, server_default=text("0"))
    ShipName = Column(String(8000))
    ShipAddress = Column(String(8000))
    ShipCity = Column(String(8000))
    ShipRegion = Column(String(8000))
    ShipPostalCode = Column(String(8000))
    ShipCountry = Column(String(8000))
    AmountTotal = Column(DECIMAL(10, 2))
    Country = Column(String(50))
    City = Column(String(50))
    Ready = Column(Boolean, server_default=text("TRUE"))
    OrderDetailCount = Column(Integer, server_default=text("0"))
    CloneFromOrder = Column(ForeignKey('Order.Id'))

    # see backref on parent: parent = relationship('Order', remote_side=[Id], cascade_backrefs=True, backref='OrderList')
    # see backref on parent: Location = relationship('Location', cascade_backrefs=True, backref='OrderList')
    # see backref on parent: Customer = relationship('Customer', cascade_backrefs=True, backref='OrderList')
    # see backref on parent: Employee = relationship('Employee', cascade_backrefs=True, backref='OrderList')

    parent = relationship('Order', remote_side=[Id], cascade_backrefs=True, backref='OrderList')  # special handling for self-relationships
    OrderDetailList = relationship('OrderDetail', cascade='all, delete', cascade_backrefs=True, backref='Order')  # manual fix


class OrderDetail(SAFRSBase, Base):
    __tablename__ = 'OrderDetail'
    _s_collection_name = 'OrderDetail'  # type: ignore
    __bind_key__ = 'None'

    Id = Column(Integer, primary_key=True)
    OrderId = Column(ForeignKey('Order.Id'), nullable=False, index=True)
    ProductId = Column(ForeignKey('Product.Id'), nullable=False, index=True)
    UnitPrice = Column(DECIMAL)
    Quantity = Column(Integer, server_default=text("1"), nullable=False)
    Discount = Column(Float, server_default=text("0"))
    Amount = Column(DECIMAL)
    ShippedDate = Column(String(8000))

    # see backref on parent: Order = relationship('Order', cascade_backrefs=True, backref='OrderDetailList')
    # see backref on parent: Product = relationship('Product', cascade_backrefs=True, backref='OrderDetailList')
