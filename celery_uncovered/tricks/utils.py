from json import loads
import codecs
import environ


FIXTURE_PATH = (environ.Path(__file__) - 1).path('fixtures')


def read_json(fpath):
    with codecs.open(fpath, 'rb', encoding='utf-8') as fp:
        return loads(fp.read())


def read_fixture(*subpath):
    fixture_file = str(FIXTURE_PATH.path(*subpath))
    return read_json(fixture_file)
