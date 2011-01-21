from clog.tests import TestModel, model, Session

from datetime import datetime

RANDOM_ID = 'ffffffffffffffff'

FIXTURES = [
    {
        'timestamp': u'2011-01-20 19:00:01',
        'tag': u'foo',
        'tag_id': RANDOM_ID,
        'value': None,
        'type': u'start',
    },
    {
        'timestamp': u'2011-01-20 19:00:02',
        'tag': u'foo',
        'tag_id': RANDOM_ID,
        'value': None,
        'type': u'stop',
    },
    {
        'timestamp': u'2011-01-20 19:00:01',
        'tag': u'foo',
        'tag_id': RANDOM_ID,
        'value': u'1',
        'type': u'duration',
    },
]
FIXTURES.sort()

class TestImportExport(TestModel):
    def test_dataset(self):
        for d in FIXTURES:
            model.Entry.__import__(d)

        Session.commit()
        new_fixtures = []
        for e in Session.query(model.Entry):
            new_fixtures += [e.__export__()]

        new_fixtures.sort()
        self.assertEqual(FIXTURES, new_fixtures)
