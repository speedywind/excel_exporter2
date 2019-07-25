from json import dumps as json_dumps
from xml.dom.minidom import parseString

from dicttoxml import dicttoxml

from .lua_table_dump import dumps as lua_dumps

config = {
    'target': {
        'client': 1,
        'server': 2,
    },
    'outputFileTypes': {
        'lua': {
            'enable': True,
            'convert_func': lambda d: lua_dumps(d, indent=2),
            'format': False,
            'format_func': None,
            'file_structs': "-- {0}\nreturn {1}",
        },
        'json': {
            'enable': False,
            'convert_func': lambda d: json_dumps(d, indent=2),
            'format': False,
            'format_func': None
        },
        'xml': {
            'enable': False,
            'convert_func': lambda d: dicttoxml(d).decode('utf-8'),
            'format': False,
            'format_func': lambda txt: parseString(txt).toprettyxml(),
        }
    }
}
