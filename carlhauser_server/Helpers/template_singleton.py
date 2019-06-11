#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from weakref import WeakValueDictionary


class Singleton(type):
    # For more info : https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    _instances = WeakValueDictionary()
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # This variable declaration is required to force a
            # strong reference on the instance.
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]

