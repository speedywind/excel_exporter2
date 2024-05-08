from json import dumps as json_dumps
from xml.dom.minidom import parseString

from dicttoxml import dicttoxml

from .lua_table_dump import dumps as lua_dumps

config = {
    'localize':{
        'zh_cn': True,
        'zh_tw': True,
    },
    'target': {
        'client': {
            'flag': 1,
            'output': {'lua'}
        },
        'server': {
            'flag': 2,
            'output': {'lua'}
        },
        'all': {
            'flag': 3,
            'output': {'py'}
        },
    },
    'outputFileTypes': {
        'lua': {
            'convert_func': lambda d: lua_dumps(d, indent=2),
            'format': False,
            'format_func': None,
            'file_structs': "-- {0}\nreturn {1}",
        },
        'json': {
            'convert_func': lambda d: json_dumps(d, indent=2),
            'format': False,
            'format_func': None
        },
        'py': {
            'convert_func': lambda d: str(d),
            'format': False,
            'format_func': None
        },
        'xml': {
            'convert_func': lambda d: dicttoxml(d).decode('utf-8'),
            'format': False,
            'format_func': lambda txt: parseString(txt).toprettyxml(),
        }
    }
}
