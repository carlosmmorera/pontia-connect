import os
import pytest

os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-test-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "dummy-test-region"
os.environ["GOOGLE_SEARCH_API_KEY"] = "dummy-test-api-key"
os.environ["GOOGLE_SEARCH_ENGINE_ID"] = "dummy-test-id"