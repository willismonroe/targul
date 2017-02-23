import json
import jsonschema
import csv

SOURCE = "Table of Cuneiform Signs.csv"
HEADER = 2
FIELDNAMES = ['sign', 'codepoint', 'name', 'Borger(2003)', 'Borger(1981)', 'comments']
SCHEMA = open('sign_schema.json').read()


def validate(json_object):
    try:


with open(SOURCE) as f:
    lines = f.readlines()[HEADER:]
    reader = csv.DictReader(lines, FIELDNAMES)

for line in list(reader):
    sign = line['sign']
    codepoint = line['codepoint']
    name = line['name']
    # for now the value will be the name
    value = line['name']
    comments = line['comments']
    json_string = {
        "codepoint": codepoint,
        "name": name,
        "glyph": [
            {
                "glyph": sign
            }
        ],
        "value": [
            {
                "value": value
            }
        ],
        "notes": comments
    }
    json_sign = json.dumps(json_string)
    try:
        jsonschema.validate(json_sign, open('sign_schema.json').read())
    except jsonschema.ValidationError:
        print("ValidationError")
