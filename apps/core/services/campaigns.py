"""Conservative channel policy: do not enable outbound cold DMs."""
from apps.core.models import Prospect

def can_contact(prospect:Prospect,provider:str,has_verified_consent:bool=False)->bool:
 if prospect.opted_out:return False
 # Verified consent alone is not a Meta messaging permission. Official window/entry point
 # checks must be added to the provider before enabling outbound actions.
 if provider=='instagram':return False
 return bool(has_verified_consent and provider=='local_test')
