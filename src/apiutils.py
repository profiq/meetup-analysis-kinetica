import time


class MeetupThrottle:
    """
    Meetup.com API allows for only `max_requests` requests during `period` seconds long period of time
    This class can be used to control number of API requests in other parts of code.

    At the time of writing this code the limit was 30 requests per 10 seconds per IP address.

    Example:
        throttle = MeetupThrottle(30, 10)
        while True:
            throttle.wait_for_request_permission()
            ... make your request ...
            throttle.increment_counter()
    """

    def __init__(self, max_requests, period, verbose=False):
        """
        :param int max_requests: Maximum number of requests allowed in during one period
        :param int period: Length of a period in seconds
        :param bool verbose: Print debug information
        """
        self._max_requests = max_requests
        self._period = period
        self._counter = 0
        self._last_period_reset_time = time.time()
        self._verbose = verbose

    def increment_counter(self):
        self._counter += 1

    def wait_for_request_permission(self):
        self._print('Cnt: %d' % self._counter)
        if self._counter == self._max_requests:
            self._print('Counter reached maximum')
            time_from_last_reset = time.time() - self._last_period_reset_time
            if time_from_last_reset < self._period:
                self._print('Need to wait until period ends')
                time_to_sleep = self._period - time_from_last_reset
                time.sleep(time_to_sleep)
            self._counter = 0

    def _print(self, msg):
        """
        :param str msg: Message to be printed
        """
        if self._verbose:
            print('[throttle] %s' % msg)
