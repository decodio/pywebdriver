# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Sylvain CALADOR <sylvain.calador@akretion.com>
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

from pif import get_public_ip
from pywebdriver import app, config, drivers
from netifaces import interfaces, ifaddresses, AF_INET
from flask_cors import cross_origin
from flask import request, jsonify, render_template
from base_driver import ThreadDriver, check
import simplejson
import usb.core

meta = {
    'name': "ESCPOS Printer",
    'description': """This plugin add the support of ESCPOS Printer for your
        pywebdriver""",
    'require_pip': ['pyxmlescpos'],
    'require_debian': [],
}

try:
    from xmlescpos.printer import Usb
    from xmlescpos.supported_devices import device_list
    from xmlescpos.constants import *
except ImportError:
    installed = False
    print 'ESCPOS: xmlescpos python library not installed'
else:
    class ESCPOSDriver(ThreadDriver, Usb):
        """ ESCPOS Printer Driver class for pywebdriver """

        def __init__(self, *args, **kwargs):
            self.encoding = config.get('odoo', 'force_receipt_encoding')
            self.vendor_product = None
            ThreadDriver.__init__(self, args, kwargs)

        def supported_devices(self):
            return device_list

        def connected_usb_devices(self):
            connected = []

            for device in self.supported_devices():
                if usb.core.find(idVendor=device['vendor'], idProduct=device['product']) != None:
                    connected.append(device)

            return connected

        def open_printer(self):

            if self.device:
                return

            try:
                printers = self.connected_usb_devices()
                if printers:
                    printer = printers[0]
                    self.idVendor = printer.get('vendor')
                    self.idProduct = printer.get('product')
                    self.interface = printer.get('interface', 0)
                    self.in_ep = printer.get('in_ep', 0x82)
                    #self.in_ep = printer.get('in_ep', 0x01)
                    self.out_ep = printer.get('out_ep', 0x01)
                    self.open()
                    self.vendor_product = '%s_%s' % (
                        self.idVendor, self.idProduct
                    )

            except Exception as e:
                self.set_status('error',str(e))

        def open_cashbox(self,printer):
            self.open_printer()
            self.cashdraw(2)
            self.cashdraw(5)

        def get_status(self):
            messages = []
            self.open_printer()
            if not self.device:
                status = 'disconnected'
            else:
                try:
                    res = self.get_printer_status()
                    if res['printer']['online']:
                        status = 'connected'
                    else:
                        status = 'connecting'

                    if res['printer']['status_error']:
                        status = 'error'
                        messages.append('Error code: %i' % res['printer']['status_error'])

                except Exception, err:
                    status = 'error'
                    self.device = False
                    messages.append('Error: %s' % err)

            return {
                'status': status,
                'messages': messages,
            }

        def printstatus(self,eprint):
            #<PyWebDriver> Full refactoring of the function to allow
            # localisation and to make more easy the search of the ip

            self.open_printer()
            ip = get_public_ip()

            if not ip:
                msg = _(
                    """ERROR: Could not connect to LAN<br/><br/>"""
                    """Please check that your system is correc-<br/>"""
                    """tly connected with a network cable,<br/>"""
                    """ that the LAN is setup with DHCP, and<br/>"""
                    """that network addresses are available""")
                self.receipt('<div>'+msg+'</div>')
                self.cut()
            else:
                addr_lines = []
                for ifaceName in interfaces():
                    addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
                    addr_lines.append(
                        '<p>'+','.join(addresses) + ' (' + ifaceName + ')' + '</p>'
                    )
                msg = _(u"""
                       <div align="center">
                            <h4>PyWebDriver Software Status</h4>
                            <br/>
                            <h5>IP Addresses:</h5>
                            %s<br/>
                            %s<br/>
                            Port šđčćžŠĐČĆŽ: %i
                       </div>
                """) % (
                    ip + ' (' + _(u'Public') + ')',
                    ''.join(addr_lines),
                    config.getint('flask', 'port'),
                )
                self.receipt(msg)


        def force_encodings(self):
            return {
                    # TODO use ordering to prevent useless switches
                    # TODO Support other encodings not natively supported by python ( Thai, Khazakh, Kanjis )
                    'cp437': TXT_ENC_PC437,
                    'cp850': TXT_ENC_PC850,
                    'cp852': TXT_ENC_PC852,
                    'cp857': TXT_ENC_PC857,
                    'cp858': TXT_ENC_PC858,
                    'cp860': TXT_ENC_PC860,
                    'cp863': TXT_ENC_PC863,
                    'cp865': TXT_ENC_PC865,
                    'cp866': TXT_ENC_PC866,
                    'cp862': TXT_ENC_PC862,
                    'cp720': TXT_ENC_PC720,
                    #'cp936': TXT_ENC_PC936,
                    'iso8859_2': TXT_ENC_8859_2,
                    'iso8859_7': TXT_ENC_8859_7,
                    'iso8859_9': TXT_ENC_8859_9,
                    'cp1250'   : TXT_ENC_WPC1250,  # TXT_ENC_WPC1250 = '\x1b\x74\x2d' # WPC1250 Latin2
                    'cp1254'   : TXT_ENC_WPC1254,
                    'cp1255'   : TXT_ENC_WPC1255,
                    'cp1256'   : TXT_ENC_WPC1256,
                    'cp1257'   : TXT_ENC_WPC1257,
                    'cp1258'   : TXT_ENC_WPC1258,
            }

        def receipt(self,xml):
            if self.force_encodings().get(self.encoding, False):
                self._raw(self.force_encodings()[self.encoding])
            return super(ESCPOSDriver, self).receipt(xml)


    driver = ESCPOSDriver(app.config)
    drivers['escpos'] = driver
    installed=True

    @app.route(
            '/hw_proxy/print_xml_receipt',
            methods=['POST', 'GET', 'PUT', 'OPTIONS'])
    @cross_origin(headers=['Content-Type'])
    def print_xml_receipt_json():
        """ For Odoo 8.0+"""

        driver.open_printer()
        receipt = request.json['params']['receipt']
        driver.push_task('receipt', receipt)

        return jsonify(jsonrpc='2.0', result=True)

    @app.route('/print_status_deprec.html', methods=['GET'])
    @cross_origin()
    def print_status_http():
        driver.push_task('printstatus')
        return render_template('print_status.html')

    @app.route('/hw_proxy/open_cashbox', methods=['POST', 'GET', 'PUT', 'OPTIONS'])
    @cross_origin(headers=['Content-Type'])
    def open_cashbox():
        driver.push_task('open_cashbox')
        return jsonify(jsonrpc='2.0', result=True)

