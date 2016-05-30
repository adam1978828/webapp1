#!/usr/bin/env python
"""

"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session
from base import Base

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class MovieDataLoadType(Base):
    __tablename__ = u'movie_data_load_type'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(2, 0), primary_key=True, )
    name = sa.Column('name', sa.String(40))
    alias = sa.Column('alias', sa.String(40))

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()