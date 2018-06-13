import json
import dicttoxml
from xml.dom.minidom import parseString
from lua_table_dump import dumps

config = {
    'lua': {
        'enable': True,
        'convert_func': lambda d: dumps(d, indent=2),
        'format': False,
        'format_func': None,
        'file_structs': "-- {0}\nreturn {1}",
    },
    'json': {
        'convert_func': lambda d: json.dumps(d, indent=2),
        'enable': False,
        'format': False,
        'format_func': None
    },
    'xml': {
        'enable': False,
        'convert_func': lambda d: dicttoxml.dicttoxml(d).decode('utf-8'),
        'format': False,
        'format_func': lambda txt: parseString(txt).toprettyxml(),
    },
}
