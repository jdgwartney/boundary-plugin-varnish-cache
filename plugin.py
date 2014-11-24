from __future__ import (absolute_import, division, print_function, unicode_literals)
import logging
import datetime
import time
import sys
import urllib2
import json
import subprocess

import boundary_plugin
import boundary_accumulator

"""
If getting statistics fails, we will retry up to this number of times before
giving up and aborting the plugin.  Use 0 for unlimited retries.
"""
PLUGIN_RETRY_COUNT = 0
"""
If getting statistics fails, we will wait this long (in seconds) before retrying.
"""
PLUGIN_RETRY_DELAY = 5


class VarnishCachePlugin(object):
    def __init__(self, boundary_metric_prefix):
        self.boundary_metric_prefix = boundary_metric_prefix
        self.settings = boundary_plugin.parse_params()
        self.accumulator = boundary_accumulator

    def get_stats(self, instance_name):
        cmd = "varnishstat -1 -j"
        if instance_name:
            # WARNING: There is a shell injection vulnerability here, where anyone with access to modify the
            # "instance-name" parameter can execute arbitrary shell commands.  However, this is a non-issue
            # because the "shell" Boundary plugin exposes this functionality by design so there's nothing
            # to protect here.
            cmd += " -n %s" % instance_name
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        del p
        # Ignore invalid instance names (which return no data) silently
        if not out:
            return {}
        data = json.loads(out)
        return data

    def get_stats_with_retries(self, *args, **kwargs):
        """
        Calls the get_stats function, taking into account retry configuration.
        """
        retry_range = xrange(PLUGIN_RETRY_COUNT) if PLUGIN_RETRY_COUNT > 0 else iter(int, 1)
        for _ in retry_range:
            try:
                return self.get_stats(*args, **kwargs)
            except Exception as e:
                logging.error("Error retrieving data: %s" % e)
                time.sleep(PLUGIN_RETRY_DELAY)

        logging.fatal("Max retries exceeded retrieving data")
        raise Exception("Max retries exceeded retrieving data")

    @staticmethod
    def get_metric_list():
        return (
            ('accept_fail', 'VARNISH_CACHE_ACCEPT_FAIL', True),
            ('backend_busy', 'VARNISH_CACHE_BACKEND_BUSY', True),
            ('backend_conn', 'VARNISH_CACHE_BACKEND_CONN', True),
            ('backend_fail', 'VARNISH_CACHE_BACKEND_FAIL', True),
            ('backend_recycle', 'VARNISH_CACHE_BACKEND_RECYCLE', True),
            ('backend_req', 'VARNISH_CACHE_BACKEND_REQ', True),
            ('backend_retry', 'VARNISH_CACHE_BACKEND_RETRY', True),
            ('backend_reuse', 'VARNISH_CACHE_BACKEND_REUSE', True),
            ('backend_toolate', 'VARNISH_CACHE_BACKEND_TOOLATE', True),
            ('backend_unhealthy', 'VARNISH_CACHE_BACKEND_UNHEALTHY', True),
            ('cache_hit', 'VARNISH_CACHE_CACHE_HIT', True),
            ('cache_hitpass', 'VARNISH_CACHE_CACHE_HITPASS', True),
            ('cache_miss', 'VARNISH_CACHE_CACHE_MISS', True),
            ('client_conn', 'VARNISH_CACHE_CLIENT_CONN', True),
            ('client_drop', 'VARNISH_CACHE_CLIENT_DROP', True),
            ('client_drop_late', 'VARNISH_CACHE_CLIENT_DROP_LATE', True),
            ('client_req', 'VARNISH_CACHE_CLIENT_REQ', True),
            ('fetch_1xx', 'VARNISH_CACHE_FETCH_1XX', True),
            ('fetch_204', 'VARNISH_CACHE_FETCH_204', True),
            ('fetch_304', 'VARNISH_CACHE_FETCH_304', True),
            ('fetch_failed', 'VARNISH_CACHE_FETCH_FAILED', True),
            ('fetch_head', 'VARNISH_CACHE_FETCH_HEAD', True),
            ('losthdr', 'VARNISH_CACHE_LOSTHDR', True),
            ('s_bodybytes', 'VARNISH_CACHE_S_BODYBYTES', True),
            ('s_fetch', 'VARNISH_CACHE_S_FETCH', True),
            ('s_hdrbytes', 'VARNISH_CACHE_S_HDRBYTES', True),
            ('s_pass', 'VARNISH_CACHE_S_PASS', True),
            ('s_pipe', 'VARNISH_CACHE_S_PIPE', True),
            ('s_req', 'VARNISH_CACHE_S_REQ', True),
            ('s_sess', 'VARNISH_CACHE_S_SESS', True),
        )

    def handle_metrics(self, data, instance_name):
        for metric_item in self.get_metric_list():
            metric_name, boundary_name, accumulate = metric_item[:3]
            metric_data = data.get(metric_name, {}).get('value', None)
            if not metric_data:
                # If certain metrics do not exist or have no value
                # (e.g. disabled in the server or just inactive) - skip them.
                continue
            if accumulate:
                value = self.accumulator.accumulate(metric_name, metric_data)
            else:
                value = metric_data
            boundary_plugin.boundary_report_metric(self.boundary_metric_prefix + boundary_name,
                                                   value, source=instance_name)

    def main(self):
        logging.basicConfig(level=logging.ERROR, filename=self.settings.get('log_file', None))
        reports_log = self.settings.get('report_log_file', None)
        if reports_log:
            boundary_plugin.log_metrics_to_file(reports_log)
        boundary_plugin.start_keepalive_subprocess()

        instances = [i['instance_name'] for i in self.settings.get("items", [{'instance_name': None}])]
        while True:
            for instance_name in instances:
                data = self.get_stats_with_retries(instance_name)
                self.handle_metrics(data, instance_name)
            boundary_plugin.sleep_interval()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        logging.basicConfig(level=logging.INFO)

    plugin = VarnishCachePlugin('')
    plugin.main()
