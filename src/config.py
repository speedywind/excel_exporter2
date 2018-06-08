import json
import dicttoxml
from xml.dom.minidom import parseString
from lua_table_dump import dumps

config = {
    'lua': {
        'enable': True,
        'native': False,
        'convert_func': lambda d: dumps(d, indent=2),
        'format': False,
        'format_func': None,
        'file_structs': "-- {0}\nreturn {1}",
    },
    'js': {
        'enable': False,
        'native': True,
        'except_files': [],
        'format': False,
        'format_func': None,
        'file_structs': "// {0}\nmodule.exports = {1}",
    },
    'json': {
        'enable': False,
        'native': True,
        'except_files': [],
        'format': True,
        'format_func': lambda txt: json.dumps(json.loads(txt), indent=2)
    },
    'xml': {
        'enable': False,
        'native': False,
        'convert_func': lambda d: dicttoxml.dicttoxml(d).decode('utf-8'),
        'format': False,
        'format_func': lambda txt: parseString(txt).toprettyxml(),
    },
}
