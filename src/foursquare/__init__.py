import urlparse
import time
import urllib
import simplejson

ERRORS = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error',
    }

ERROR_TYPES = {
    'invalid_auth': 'OAuth token was not provided or was invalid.',
    'param_error': 'A required parameter was missing or a parameter was malformed. This is also used if the resource ID in the path is incorrect.',
    'endpoint_error': 'The requested path does not exist.',
    'not_authorized': 'Although authentication succeeded, the acting user is not allowed to see this information due to privacy restrictions.',
    'rate_limit_exceeded': 'Rate limit for this hour exceeded.',
    'deprecated': 'Something about this request is using deprecated functionality, or the response format may be about to change.',
    'server_error': 'Server is currently experiencing issues. Check status.foursquare.com for udpates.',
    'other': 'Some other type of error occurred.',
    }

FS_SERVER = 'foursquare.com'
FS_AUTH_URL = 'https://%s/oauth2/authenticate' % FS_SERVER
FS_TOKEN_URL = 'https://%s/oauth2/access_token' % FS_SERVER
FS_ENDPOINT_URL = 'https://api.%s/v2' % FS_SERVER


class Foursquare(object):

    def __init__(self, client_id, client_secret, userless=False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.userless = userless

    @property
    def userless_params(self):
        params = {'client_id': self.client_id,
                  'client_secret': self.client_secret
                  }
        return params

    def do_request(self, url, params):
        """Performs the passed request and returns meaninful data"""
        if self.userless:
            params.update(self.userless_params)
        url = '%s%s?%s'% (FS_ENDPOINT_URL, url, urllib.urlencode(params))
        response = urllib.urlopen(url).read()
        result = simplejson.loads(response)
        if not result.get('meta'):
            raise ValueError('Got an invalid response')
        response_code = result['meta'].get('code')
        if response_code != 200:
            error_message = ERRORS[response_code] \
                            if response_code in ERRORS else 'Unkown Error'
            raise ValueError(error_message)
        return result['response']


    def auth_url(self, redirect_url):
        data = {'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': redirect_url}
        return '%s?%s'% (FS_AUTH_URL, urllib.urlencode(data))

    def read_response(self, request):
        return request.GET.get('code')

    def get_token(self, request, redirect_url):
        code = self.read_response(request)
        if not code:
            return False
        data = {'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_url,
                'code': code,
                }
        url =  '%s?%s'% (FS_TOKEN_URL, urllib.urlencode(data))
        result = simplejson.loads(urllib.urlopen(url).read())
        if 'access_token' in result:
            return result['access_token']
        return False

    def search_venues(self, latitude, longitude, extra_params=None):
        """Search venues with the given params.
        Returns a json list of venues
        http://developer.foursquare.com/docs/venues/search.html
        Optional extra params
        llAcc	10000.0	Accuracy of latitude and longitude, in meters.
        alt	0	Altitude of the user's location, in meters.
        altAcc	10000.0	Accuracy of the user's altitude, in meters.
        query	donuts	A search term to be applied against titles.
        limit	10	Number of results to return, up to 50.
        """
        params = {'ll': '%s,%s' % (latitude, longitude)}
        if extra_params:
            params.update(extra_params)
        return self.do_request('/venues/search', params)
