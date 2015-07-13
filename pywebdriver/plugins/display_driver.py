# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

meta = {
    'name': "POS Display",
    'description': """This plugin add the support of customer display for your
        pywebdriver""",
    'require_pip': ['pyposdisplay'],
    'require_debian': ['python-pyposdisplay'],
}

from pywebdriver import app
from flask_cors import cross_origin
from flask import request, jsonify
from base_driver import ThreadDriver, check
import simplejson

try:
    import pyposdisplay
except:
    installed=False
else:
    installed=True
    class DisplayDriver(ThreadDriver, pyposdisplay.Driver):
        """ Display Driver class for pywebdriver """

        def __init__(self, *args, **kwargs):
            ThreadDriver.__init__(self)
            pyposdisplay.Driver.__init__(self, *args, **kwargs)

    display_driver = DisplayDriver(app.config)

@app.route(
    '/hw_proxy/send_text_customer_display',
    methods=['POST', 'GET', 'PUT', 'OPTIONS'])
@cross_origin(headers=['Content-Type'])
@check(installed, meta)
def send_text_customer_display():
    app.logger.debug('LCD: Call send_text')
    text_to_display = request.json['params']['text_to_display']
    lines = simplejson.loads(text_to_display)
    display_driver.push_task('send_text', lines)
    return jsonify(jsonrpc='2.0', result=True)
