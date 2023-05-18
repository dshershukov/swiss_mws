"""
Provide some basic validators and a template for new ones
"""
import re

from tkinter.messagebox import showerror


class Validator:
    def __init__(self, complete_test: str, partial_test: str, error_message: str):
        self.complete_test = re.compile(complete_test)
        self.partial_test = re.compile(partial_test)
        self.error_message = error_message

    def __call__(self, value, reason) -> bool:
        # If somehow the value in the widget got wrong,
        # we should be able to enter it to change
        if reason == 'focusin':
            return True

        # During input, if validation does not pass, TK reverts change, so we do not need messages
        if reason == 'key':
            if not self.partial_test.match(value):
                return False

        # On focusout the entire value should be correct
        if reason == 'focusout':
            if not self.complete_test.match(value):
                showerror(message=self.error_message)
                return False

        # If forced change sets invalid data, we're in deep trouble
        if reason == 'forced':
            if not self.complete_test.match(value):
                showerror(message='An invalid value was set automatically. ' + self.error_message)
                return False

        return True

    def clone_with_new_message(self, error_message: str) -> 'Validator':
        validator = Validator(self.complete_test.pattern, self.partial_test.pattern, error_message)
        return validator


integer_validator = Validator(r'^-?\d+$', r'^-?\d*$', 'Value must be integer')
nonnegative_integer_validator = Validator(r'^\d+$', r'^\d*$', 'Value must be nonnegative integer')
