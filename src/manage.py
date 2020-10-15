#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":

    # if ('celery' in sys.argv) and ('worker' in sys.argv):
    #     sys.argv = [word for word in sys.argv if "autoscale" not in word] + \
    #                ["-P", "eventlet", "-c", "100"]
    #     from eventlet import monkey_patch
    #
    #     monkey_patch()
    #
    #     if ("beat" not in sys.argv) and ("celerybeat" not in sys.argv) and ("backend" not in sys.argv):
    #         try:
    #             Popen("/cache/.bk/env/bin/python /data/app/code/manage.py celery worker -Q backend".split())
    #         except Exception:
    #             pass

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
