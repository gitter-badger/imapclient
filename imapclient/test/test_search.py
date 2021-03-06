from __future__ import unicode_literals

from .imapclient_test import IMAPClientTest
from .testable_imapclient import TestableIMAPClient as IMAPClient


class TestSearch(IMAPClientTest):

    def test_with_uid(self):
        self.client.use_uid = True
        self.client._imap.uid.return_value = ('OK', [b'1 2 44'])

        result = self.client.search('FOO')

        self.client._imap.uid.assert_called_once_with('SEARCH', '(FOO)')
        self.assertEqual(result, [1, 2, 44])
        self.assertEqual(result.modseq, None)

    def test_with_uid_none(self):
        self.client.use_uid = True
        self.client._imap.uid.return_value = ('OK', [None])

        result = self.client.search('FOO')

        self.client._imap.uid.assert_called_once_with('SEARCH', '(FOO)')
        self.assertEqual(result, [])
        self.assertEqual(result.modseq, None)

    def test_without_uid(self):
        self.client.use_uid = False
        self.client._imap.search.return_value = ('OK', [b'1 2 44'])

        result = self.client.search('FOO')

        self.client._imap.search.assert_called_once_with(None, '(FOO)')
        self.assertEqual(result, [1, 2, 44])
        self.assertEqual(result.modseq, None)

    def test_with_uid_with_charset(self):
        self.client.use_uid = True
        self.client._imap.uid.return_value = ('OK', [b'1 2 44'])

        result = self.client.search('FOO', 'UTF9')

        self.client._imap.uid.assert_called_once_with(
            'SEARCH',
            b'CHARSET', 'UTF9',
            '(FOO)')
        self.assertEqual(result, [1, 2, 44])

    def test_without_uid_with_charset(self):
        self.client.use_uid = False
        self.client._imap.search.return_value = ('OK', [b'1 2 44'])

        result = self.client.search('FOO', 'UTF9')

        self.client._imap.search.assert_called_once_with('UTF9', '(FOO)')
        self.assertEqual(result, [1, 2, 44])

    def test_with_multiple_criteria_and_charset(self):
        self.client.use_uid = False
        self.client._imap.search.return_value = ('OK', [b'1 2 44'])

        result = self.client.search(['FOO', 'BAR'], 'UTF9')

        self.client._imap.search.assert_called_once_with('UTF9', '(FOO)', '(BAR)')
        self.assertEqual(result, [1, 2, 44])

    def test_modseq(self):
        self.client._imap.uid.return_value = ('OK', [b'1 2 (MODSEQ 51101)'])

        result = self.client.search(['MODSEQ 40000'])

        self.client._imap.uid.assert_called_once_with('SEARCH', '(MODSEQ 40000)')
        self.assertEqual(result, [1, 2])
        self.assertEqual(result.modseq, 51101)

    def test_error_from_server(self):
        self.client._imap.uid.return_value = ('NO', [b'bad karma'])

        self.assertRaisesRegex(IMAPClient.Error,
                               'bad karma',
                               self.client.search, b'FOO')


class TestGmailSearch(IMAPClientTest):

    def test_with_uid(self):
        self.client.use_uid = True
        self.client._imap.uid.return_value = ('OK', [b'1 2 44'])

        result = self.client.gmail_search('FOO')

        self.client._imap.uid.assert_called_once_with('SEARCH', b'X-GM-RAW')
        self.assertEqual(self.client._imap.literal, b'FOO')
        self.assertEqual(result, [1, 2, 44])

    def test_without_uid(self):
        self.client.use_uid = False
        self.client._imap.search.return_value = ('OK', [b'1 2 44'])

        result = self.client.gmail_search('FOO')

        self.client._imap.search.assert_called_once_with(None, b'X-GM-RAW')
        self.assertEqual(self.client._imap.literal, b'FOO')
        self.assertEqual(result, [1, 2, 44])

    def test_with_uid_with_charset(self):
        self.client.use_uid = True
        self.client._imap.uid.return_value = ('OK', [b'1 2 44'])

        result = self.client.gmail_search('\u2620', 'UTF8')

        self.client._imap.uid.assert_called_once_with(
            'SEARCH',
            b'CHARSET', 'UTF8',
            b'X-GM-RAW')
        self.assertEqual(self.client._imap.literal, b'\xe2\x98\xa0')
        self.assertEqual(result, [1, 2, 44])

    def test_without_uid_with_charset(self):
        self.client.use_uid = False
        self.client._imap.search.return_value = ('OK', [b'1 2 44'])

        result = self.client.gmail_search('\u2620', 'UTF8')

        self.client._imap.search.assert_called_once_with('UTF8', b'X-GM-RAW')
        self.assertEqual(self.client._imap.literal, b'\xe2\x98\xa0')
        self.assertEqual(result, [1, 2, 44])

    def test_error_from_server(self):
        self.client._imap.uid.return_value = ('NO', [b'bad karma'])

        self.assertRaisesRegex(IMAPClient.Error,
                               'bad karma',
                               self.client.gmail_search, b'FOO')
