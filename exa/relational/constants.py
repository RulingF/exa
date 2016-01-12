# -*- coding: utf-8 -*-
'''
Physical Constants
===============================================
'''
from exa.relational.base import Base, Column, String, Float
from exa.relational.base import session, commit
from exa.relational.base import Meta as _Meta


class Meta(_Meta):
    '''
    '''
    def _getitem(self, key):
        '''
        '''
        obj = session.query(self).filter(self.symbol == key).all()
        if len(obj) == 1:
            return obj[0]
        else:
            raise ValueError('Value {0} not found in {1}'.format(key, self.__tablename__))

    def __getitem__(self, key):
        commit()
        return self._getitem(key)


class Constant(Base):
    '''
    Physical constants.
    '''
    symbol = Column(String, nullable=False)
    value = Column(Float, nullable=False)
