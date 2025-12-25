import re
import string


MAX_ORIGINAL_LENGTH = 2048
MAX_SHORT_LENGTH = 16
GENERATED_SHORT_LENGTH = 6
MAX_GENERATION_ATTEMPTS = 10
SHORT_CHARS = string.ascii_letters + string.digits
SHORT_PATTERN = re.compile(f'^[{re.escape(SHORT_CHARS)}]+$')
FILES_ENDPOINT = 'files'
