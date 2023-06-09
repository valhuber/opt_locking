from safrs import SAFRSAPI
# from safrs.safrs_api import SAFRSAPI
import safrs
import importlib
import pathlib
import logging as logging

# use absolute path import for easier multi-{app,model,db} support
database = __import__('database')

app_logger = logging.getLogger(__name__)

app_logger.debug("\napi/expose_api_models.py - endpoint for each table")


def expose_models(api: SAFRSAPI, method_decorators = []):  # th 
    """
        Declare API - on existing SAFRSAPI 
            This exposes each model (note: end point names are table names) 
            Including get (filtering, pagination, related data access) 
            And post/patch/update (including logic enforcement) 
        You typically do not customize this file 
            See https://apilogicserver.github.io/Docs/Tutorial/#customize-and-debug 
    """
    api.expose_object(database.models.Category, method_decorators= method_decorators)
    api.expose_object(database.models.Customer, method_decorators= method_decorators)
    api.expose_object(database.models.CustomerDemographic, method_decorators= method_decorators)
    api.expose_object(database.models.Department, method_decorators= method_decorators)
    api.expose_object(database.models.Employee, method_decorators= method_decorators)
    api.expose_object(database.models.Union, method_decorators= method_decorators)
    api.expose_object(database.models.EmployeeAudit, method_decorators= method_decorators)
    api.expose_object(database.models.EmployeeTerritory, method_decorators= method_decorators)
    api.expose_object(database.models.Territory, method_decorators= method_decorators)
    api.expose_object(database.models.Location, method_decorators= method_decorators)
    api.expose_object(database.models.Order, method_decorators= method_decorators)
    api.expose_object(database.models.OrderDetail, method_decorators= method_decorators)
    api.expose_object(database.models.Product, method_decorators= method_decorators)
    api.expose_object(database.models.Region, method_decorators= method_decorators)
    api.expose_object(database.models.SampleDBVersion, method_decorators= method_decorators)
    api.expose_object(database.models.Shipper, method_decorators= method_decorators)
    api.expose_object(database.models.Supplier, method_decorators= method_decorators)
    return api
