from unittest import TestCase
import mock

from pyeti.cli import confirm

from faker import Faker
_faker = Faker()


class ConfirmTests(TestCase):
    def setUp(self):
        self.__message = _faker.sentence()

    @mock.patch('pyeti.cli.input', return_value='y')
    def test_displays_the_passed_message(self, mock_input):
        confirm(self.__message)
        mock_input.assert_called_once_with(self.__message)

    @mock.patch('pyeti.cli.input', return_value='y')
    def test_returns_true_for_a_yes_answer(self, mock_input):
        result = confirm(self.__message)
        self.assertTrue(result)

    @mock.patch('pyeti.cli.input', return_value='n')
    def test_returns_false_for_a_no_answer(self, mock_input):
        result = confirm(self.__message)
        self.assertFalse(result)

    @mock.patch('pyeti.cli.input', return_value='Y')
    def test_is_case_insensitive(self, mock_input):
        result = confirm(self.__message)
        self.assertTrue(result)

    @mock.patch('pyeti.cli.input', side_effect=['not a yes or no', 'y'])
    def test_only_accepts_yes_or_no_answers_as_confirmation(self, mock_input):
        result = confirm(self.__message)
        mock_input.assert_has_calls([mock.ANY, mock.call('Please answer yes or no: ')])
        self.assertTrue(result)

    @mock.patch('pyeti.cli.input', side_effect=['', 'y'])
    def test_does_not_accept_empty_input_without_a_default(self, mock_input):
        result = confirm(self.__message)
        mock_input.assert_has_calls([mock.ANY, mock.call('Please answer yes or no: ')])
        self.assertTrue(result)

    @mock.patch('pyeti.cli.input', return_value='')
    def test_returns_the_default_if_an_empty_input_is_given(self, mock_input):
        default = _faker.word()
        result = confirm(self.__message, default=default)
        self.assertEqual(result, default)
