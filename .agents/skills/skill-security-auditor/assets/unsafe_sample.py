#!/usr/bin/env python3
"""Deliberately unsafe sample skill script — used as audit fixture.

Every dangerous pattern below is intentional; the expected audit output in
expected_outputs/ documents the findings a clean auditor run must produce.
"""

import os
import pickle

def run(user_input):
    os.system("echo " + user_input)  # noqa flag-expected: CMD-INJECT fixture
    return eval(user_input)          # noqa flag-expected: CODE-EXEC fixture

def load(path):
    with open(path, "rb") as f:
        return pickle.load(f)        # noqa flag-expected: DESERIALIZE fixture
