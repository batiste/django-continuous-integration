# To keep tests running
from django.conf import settings
    
INT_DIR = getattr(settings, 'DJANGO_INTEGRATION_DIRECTORY', '/tmp/dji/')
COV_CANDIDATES = getattr(settings, 'DJANGO_INTEGRATION_COV_CANDIDATES',
        ['htmlcov', 'covhtml', 'cov', 'coverage'])
TESTED_APP_DIR = getattr(settings, 'DJANGO_TESTED_APP_DIR', 'tested_app/')

# 20 minutes max running time for the tests
MAX_RUNNING_TIME = getattr(settings, 'MAX_RUNNING_TIME', 20 * 60)