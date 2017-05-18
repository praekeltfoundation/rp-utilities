import os.path

import pytest

from rputilities import campaigns


@pytest.fixture(scope='module')
def file_location():
    return os.path.join(os.path.dirname(__file__), 'files')


class TestGetCampaignEventsFromCsv:

    def test_valid_without_translations(self, file_location):
        fn = os.path.join(file_location, 'valid-one-lang.csv')
        events = campaigns.get_campaign_events_from_csv(fn)
        assert list(events) == [
            campaigns.CampaignEvent(
                relative_to='edd', offset=-1, unit='days',
                delivery_hour=8, message='Test Message One'
            ),
            campaigns.CampaignEvent(
                relative_to='edd', offset=0, unit='days',
                delivery_hour=8, message='Test Message Two'
            ),
            campaigns.CampaignEvent(
                relative_to='edd', offset=1, unit='days',
                delivery_hour=8, message='Test Message Three'
            ),
        ]

    def test_valid_with_translations(self, file_location):
        fn = os.path.join(file_location, 'valid-multi-lang.csv')
        events = campaigns.get_campaign_events_from_csv(fn)
        assert list(events) == [
            campaigns.CampaignEvent(
                relative_to='edd', offset=-1, unit='days',
                delivery_hour=8, message={"eng": "One", "fre": "Un", "ita": "Uno"}
            ),
            campaigns.CampaignEvent(
                relative_to='edd', offset=0, unit='days',
                delivery_hour=8, message={"eng": "Two", "fre": "Deux", "ita": "Duo"}
            ),
            campaigns.CampaignEvent(
                relative_to='edd', offset=1, unit='days',
                delivery_hour=8, message={"eng": "Three", "fre": "Trois", "ita": "Tre"}
            ),
        ]

    def test_invalid_structure(self, file_location):
        fn = os.path.join(file_location, 'invalid-format.csv')
        with pytest.raises(ValueError) as exc:
            list(campaigns.get_campaign_events_from_csv(fn))
        assert 'Invalid CSV format: A minimum of' in str(exc.value)

    def test_invalid_lang_pairs(self, file_location):
        fn = os.path.join(file_location, 'invalid-lang-pairs.csv')
        with pytest.raises(ValueError) as exc:
            list(campaigns.get_campaign_events_from_csv(fn))
        assert 'Pairs of lang_code, message columns expected' in str(exc.value)

    def test_invalid_file(self, file_location):
        fn = os.path.join(file_location, 'no-such-file.csv')
        with pytest.raises(IOError) as exc:
            list(campaigns.get_campaign_events_from_csv(fn))
        assert 'No such file or directory' in str(exc.value)
