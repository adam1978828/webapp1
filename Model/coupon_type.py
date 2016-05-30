# -*- coding: utf-8 -*-
import datetime
import pickle

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base


__author__ = 'D.Kalpakchi'


class CouponType(Base):
    """
    Enumerate coupon type
    pattern: saved as pickled string
    """
    __tablename__ = u'e_coupon_type'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric, primary_key=True)
    pattern = sa.Column('pattern', sa.String(100), unique=True)
    alias = sa.Column('alias', sa.String(100))

    def __init__(self, pattern, alias):
        self.pattern = pickle.dumps(pattern)
        self.alias = alias

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @hybrid_property
    def decoded_pattern(self):
        return pickle.loads(self.pattern)
