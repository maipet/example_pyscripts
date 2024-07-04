import requests
import re


def read_data(url):
    resp = requests.get(url)
    data = resp.text
    return data
def replacement(string, replace_dict):
    replacement = dict((re.escape(k), v)  for k, v in replace_dict.items())
    pattern = re.compile("|".join(replacement.keys()))
    replaced_string = pattern.sub(lambda m: replacement[re.escape(m.group(0))], string.replace("'", '"'))
    return replaced_string
def write_outfile(new_text, name):
    with open("/home/petra/resodate_changed_mappings/test/%sMapping.py" %name, "w") as outfile:
        outfile.write("import search_index_import_commons.constants.KimHochschulfaechersystematik as Subject\n" + new_text)

subjects = "https://gitlab.com/oersi/sidre/sidre-import-scripts-commons/-/raw/main/search_index_import_commons/constants/KimHochschulfaechersystematik.py?ref_type=heads"

resp_subjects = read_data(subjects)
subject_lines = resp_subjects.splitlines()

replace_dict = {}
pattern_key = re.compile(r'https[^"]+')
pattern_value = re.compile(r'^[\S]+')
for line in subject_lines:
    match = pattern_key.search(line)
    key = match.group()
    match_value = pattern_value.search(line)
    value = match_value.group()
    replace_dict.update({'"'+key+'"': "Subject."+ value})

namelist = ["JDAData", "Fordatis", "BonnData", "DaRUS", "DataCite", "DepositOnce", "GROdata", "TUdatalib", "FZJuelich"]
for name in namelist:
    raw_data_uri = "https://gitlab.com/TIBHannover/resodate/resodate-import-scripts/-/raw/master/python/%sMapping.py?ref_type=heads" % name
    resp = read_data(raw_data_uri)
    write_outfile(replacement(resp, replace_dict), str(name))


