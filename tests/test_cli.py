from unittest import TestCase, mock

from getpass import getpass

from pyeti.cli import confirm, required_input, password_confirm, prompt

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


class RequiredInputTests(TestCase):

    def setUp(self):
        self.__message = _faker.sentence()

    def test_it_uses_the_supplied_method(self):
        method = mock.Mock(return_value='test')
        required_input(self.__message, method)
        method.assert_called_once_with(self.__message)

    def test_it_returns_the_methods_return_value(self):
        method = mock.Mock(return_value='testing!')
        self.assertEqual('testing!', required_input(self.__message, method))

    def test_it_loops_until_an_answer_is_supplied(self):
        method = mock.Mock(side_effect=['', 'second'])
        self.assertEqual('second', required_input(self.__message, method))
        self.assertEqual(method.call_count, 2)


class PasswordConfirmTests(TestCase):

    @mock.patch('pyeti.cli.required_input', return_value='my_password')
    def test_it_uses_the_supplied_messages(self, mock_input):
        message = _faker.sentence()
        confirm_message = _faker.sentence()
        password_confirm(message, confirm_message)
        self.assertEqual(2, mock_input.call_count)
        mock_input.assert_has_calls([
            mock.call(message, method=getpass),
            mock.call(confirm_message, method=getpass)
        ])

    def test_it_returns_the_password_if_they_match(self):
        patcher = mock.patch('pyeti.cli.required_input', return_value='my_password')
        patcher.start()

        try:
            self.assertEqual('my_password', password_confirm())
        finally:
            patcher.stop()

    def test_it_returns_false_if_they_do_not_match(self):
        patcher = mock.patch('pyeti.cli.required_input', side_effect=[
            'my_password', 'not_my_password'
        ])
        patcher.start()

        try:
            self.assertFalse(password_confirm())
        finally:
            patcher.stop()


class PromptTests(TestCase):

    __choices = [
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
    ]

    def setUp(self):
        super().setUp()
        patcher = mock.patch('pyeti.cli.input', return_value='1')
        self.__mock_input = patcher.start()
        self.addCleanup(patcher.stop)

    def test_it_displays_a_list_of_enumerated_choices(self):
        prompt(self.__choices)
        message = self.__mock_input.call_args[0][0]
        self.assertIn('1) First', message)
        self.assertIn('2) Second', message)
        self.assertIn('3) Third', message)

    def test_it_prompts_for_a_choice(self):
        prompt(self.__choices)
        message = self.__mock_input.call_args[0][0]
        self.assertIn('Please select a choice:', message)

    def test_it_continues_prompting_until_a_valid_choice_is_entered(self):
        del self.__mock_input.return_value
        self.__mock_input.side_effect = ['15', '1']
        prompt(self.__choices)
        self.assertEqual(self.__mock_input.call_count, 2)
        self.__mock_input.assert_has_calls([
            mock.call(mock.ANY),
            mock.call('Please enter a valid choice: ')
        ])

    def test_it_returns_the_choice(self):
        self.assertEqual('first', prompt(self.__choices))

    def test_raises_if_the_choices_list_is_empty(self):
        self.assertRaises(ValueError, prompt, [])
