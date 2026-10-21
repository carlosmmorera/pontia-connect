import os
import pytest

os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-test-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "dummy-test-region"
os.environ["PONTIA_CONNECT_SHEET_ID"] = "dummy-test-sheet-id"