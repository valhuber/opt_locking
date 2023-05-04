import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import logging


logger = logging.getLogger(__name__)

def sys_logic_setup(session):
    pass

    from sqlalchemy import event

    @event.listens_for(session, 'loaded_as_persistent')
    def receive_loaded_as_persistent(session, instance):
        "listen for the 'loaded_as_persistent' event"

        logger.debug(f'{__name__} - hello there instance: {instance}')
        if isinstance(instance, models.Department):
            logger.debug(f'{__name__} - hello there DEPT instance: {instance}')
        elif isinstance(instance, models.Employee):
            logger.debug(f'{__name__} - hello there EMP instance: {instance}')
        else:
            logger.debug(f'{__name__} - hello there instance: {instance}')