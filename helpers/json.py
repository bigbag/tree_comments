# -*- coding: utf-8 -*-

"""Should be used as a drop-in replacement of the bundled `json` module."""

from __future__ import absolute_import

import uuid
import json
import decimal
import datetime


class Encoder(json.JSONEncoder):
    """Copy of the `django.core.serializers.json.DjangoJSONEncoder`"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, uuid.UUID):
            return str(o)

        return super(Encoder, self).default(o)


def dumps(*args, **kwargs):
    kwargs['cls'] = Encoder

    return json.dumps(*args, **kwargs)


#: Re-exporting required functions
dump = json.dump
loads = json.loads
load = json.load
