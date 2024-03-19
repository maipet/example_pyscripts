import pandas as pd
import rdflib.term
from rdflib import Graph, Literal, RDF, URIRef, Namespace

url_stb = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/raw/main/studierende/STB.csv?raw=true"
url_studienfach = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Studienfach.csv?raw=true"
url_faechergruppe = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Faechergruppe.csv?raw=true"

df_stb = pd.read_csv(url_stb, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str)
df_studienfach = pd.read_csv(url_studienfach, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str)
df_faechergruppe = pd.read_csv(url_faechergruppe, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str)

def create_studifaecher_dict(bereichs_key):
    dict_list = []
    for i, r in df_studienfach.iterrows():
        if r[3] == bereichs_key:
            studifaecher_dict = {r[0]: r[2]}
            dict_list.append(studifaecher_dict)
    return dict_list

faechergruppe_dict = dict(zip(df_faechergruppe[0], df_faechergruppe[2]))
studibereich_dict = dict(zip(df_stb[0], df_stb[2]))
destatis_dict = {}

for index, row in df_stb.iterrows():
    if row[3] in destatis_dict.keys():
        studifaecher_dict = create_studifaecher_dict(row[0])
        destatis_dict[row[3]].append({row[0]: studifaecher_dict})
    else:
        studibereich_dicts = [{row[0]:  create_studifaecher_dict(row[0])}]
        destatis_dict.update({row[3]: studibereich_dicts})

g = Graph()

vann = Namespace('http://purl.org/vocab/vann/')
dct = Namespace('http://purl.org/dc/terms/')
owl = Namespace('http://www.w3.org/2002/07/owl#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace('https://schema.org/')
g.bind("schema", schema)

#conceptScheme
g.add((URIRef('scheme'), RDF['type'], skos['ConceptScheme']))
g.add((URIRef('scheme'), dct['title'], Literal('Destatis-Systematik der Fächergruppen, Studienbereiche und Studienfächer', lang='de')))
g.add((URIRef('scheme'), dct['alternative'], Literal('Hochschulfächersystematik', lang='de')))
g.add((URIRef('scheme'), dct['description'], Literal('Diese SKOS-Klassifikation basiert auf der Destatis-[\"Systematik der Fächergruppen, Studienbereiche und Studienfächer\"](https://bartoc.org/en/node/18919).', lang='de')))
g.add((URIRef('scheme'), dct['issued'], Literal('2019-12-11')))
g.add((URIRef('scheme'), dct['publisher'], rdflib.term.URIRef('https://oerworldmap.org/resource/urn:uuid:fd06253e-fe67-4910-b923-51db9d27e59f')))
g.add((URIRef('scheme'), vann['preferredNamespaceUri'], rdflib.term.URIRef('https://w3id.org/kim/hochschulfaechersystematik/')))
g.add((URIRef('scheme'), schema['isBasedOn'], rdflib.term.URIRef('http://bartoc.org/node/18919')))

for top_level in destatis_dict.keys():
    top_level = "n"+top_level.lstrip("0")
    g.add((URIRef('scheme'), skos['hasTopConcept'], (URIRef(top_level))))

g.add((URIRef('n0'), RDF['type'], skos['Concept']))
g.add((URIRef('n0'), skos['prefLabel'], Literal('Fachübergreifend', lang='de')))
g.add((URIRef('n0') , skos['notation'], Literal('0')))
g.add((URIRef('n0'), skos['topConceptOf'], (URIRef('scheme'))))

# add each graph
for key, value in destatis_dict.items():
    g.add((URIRef('n%s' % key.lstrip('0')), RDF['type'], skos['Concept']))
    g.add((URIRef('n%s' % key.lstrip('0')), skos['prefLabel'], Literal(faechergruppe_dict[key], lang='de')))
    g.add((URIRef('n%s' % key.lstrip('0')), skos['notation'], Literal(key.lstrip('0'))))
    g.add((URIRef('n%s' % key.lstrip('0')), skos['topConceptOf'], (URIRef('scheme'))))
    for bereich in value:
        for k,v in bereich.items():
            g.add((URIRef('n%s' % k), RDF['type'], skos['Concept']))
            g.add((URIRef('n%s' % k), skos['prefLabel'], Literal(studibereich_dict[k], lang='de')))
            g.add((URIRef('n%s' % k), skos['notation'], Literal(k)))
            g.add((URIRef('n%s' % k), skos['inScheme'], (URIRef('scheme'))))
            g.add((URIRef('n%s' % k), skos['broader'], (URIRef('n%s' % key.lstrip('0')))))
            for fach_items in v:
                for fach_notation, fach_label in fach_items.items():
                    g.add((URIRef('n%s' % fach_notation), RDF['type'], skos['Concept']))
                    g.add((URIRef('n%s' % fach_notation), skos['prefLabel'], Literal(fach_label, lang='de')))
                    g.add((URIRef('n%s' % fach_notation), skos['notation'], Literal(fach_notation)))
                    g.add((URIRef('n%s' % fach_notation), skos['inScheme'], (URIRef('scheme'))))
                    g.add((URIRef('n%s' % fach_notation), skos['broader'], (URIRef('n%s' % k))))

g.serialize('output.ttl', format='turtle')
