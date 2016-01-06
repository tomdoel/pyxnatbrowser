# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

class Utilities(object):

    @staticmethod
    def get_optional_property(base_object, property_name):
        if hasattr(base_object, property_name):
            return base_object.property
        else:
            return None

    @staticmethod
    def get_optional_dict_value(base_object, key_name):
        if key_name in base_object:
            return base_object[key_name]
        else:
            return None
