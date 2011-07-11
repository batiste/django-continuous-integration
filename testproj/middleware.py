import sys
from django.http import HttpResponseForbidden
from django.conf import settings

class RestrictMiddleware(object):
    """
    Reject all requests from IP addresses that are not on the whitelist.
    (We allow one exception for the sake of an unfuddle commit callback.)
    """
    IP_WHITELIST = []  				# override this with IP_WHITELIST in settings
    ACCESS_DENIED_MESSAGE = 'Access Denied'
    REQUIRED_CALLBACK_STRING = 'repository'   			# 'repository' is a good one for unfuddle
    CONFIRM_CALLBACK_STRINGS = ['my_company_domain.com',]	# override this in settings

    def process_request(self, request):
        """
        Check the request to see if access should be granted.
        """
        ipw = getattr(settings, 'IP_WHITELIST', self.IP_WHITELIST)
        if request.META['REMOTE_ADDR'] in ipw:
            # all requests from whitelisted IPs are allowed.
            return None

        # For now we just report some stuff.
        # Later we will add some explicit checks to
        #   restrict this to unfuddle commit callbacks..
        print request.method
        print "|%s|" % (request.path)
        for key, value in request.REQUEST.iteritems():
            print key, "::", value
        sys.stdout.flush()
        if request.method == "POST":
            if request.path == "/make":
                required_string = getattr(settings, 'REQUIRED_CALLBACK_STRING', self.REQUIRED_CALLBACK_STRING)
                callback_strings = getattr(settings, 'CONFIRM_CALLBACK_STRINGS', self.CONFIRM_CALLBACK_STRINGS)
                for key, value in request.REQUEST.iteritems():
                    if required_string in value:
                        for callback_string in callback_strings:
                            if callback_str in value:
                                return None

        # Unexpected request - deny!
        m = getattr(settings, 'RESTRICT_ACCESS_DENIED_MESSAGE', self.ACCESS_DENIED_MESSAGE)
        return HttpResponseForbidden(m)

