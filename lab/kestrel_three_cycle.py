#!/usr/bin/env python3
"""Kestrel Lab: deterministic three-iteration test/score/repair cycle.

Runs only on the isolated kestrel/lab-3cycle branch. It records a baseline,
applies one bounded repair per iteration, adds regression tests, reruns the full
suite after every change, and emits a Markdown/JSON scorecard.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime