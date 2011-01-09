from clog.model.meta import Session, metadata
from clog.model.objects import *

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
