
'''
Copyright 2021 Delta Electronic Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import time
import sys
import os
import json
from collections import OrderedDict
from poe_common import *
from pyroute2.netlink.generic.ethtool import NlEthtool

class PoeDriver_mainline(object)
    def get_ports_information(self, portList, more_info=True):
        ports_info = []
        for portidx in portList:
            info = poePort(self, portidx).get_current_status(more_info)
            ports_info.append(info)
        return ports_info

class poePort(object):
    def __init__(self, poe_plat, port_id):
        self.poe_plat = poe_plat
        self.port_id = port_id
        self.enDis = 1
        self.status = ""
        self.priority = ""
        self.protocol = ""
        self.latch = 0x00
        self.class_type = 0
        self.FPairEn = 0
        self.power_consump = 0
        self.power_limit = 0
        self.voltage = 0
        self.current = 0
        self.measured_class = 0

    def update_port_status(self):
        if self._4wire_bt == 1:
            params = self.poe_plat.get_bt_port_parameters(self.port_id)
            params_class = self.poe_plat.get_bt_port_class(self.port_id)
            self.status = TBL_BT_STATUS_TO_CFG[params.get(STATUS)]
            self.enDis = TBL_ENDIS_TO_CFG[params.get(ENDIS)]
            self.measured_class = params_class.get(MEASURED_CLASS) >> 4
            # Delivers power, port status: 0x80-0x91
            if params.get(STATUS) >= 0x80 and params.get(STATUS) <= 0x91:
                if self.measured_class >= 0 and self.measured_class <= 4:
                    self.protocol = "IEEE802.3AF/AT"
                elif self.measured_class >= 5 and self.measured_class <= 8:
                    self.protocol = "IEEE802.3BT"
                else:
                    self.protocol = "NA"
            else:
                self.protocol = "NA"

            self.priority = TBL_PRIORITY_TO_CFG[params.get(PRIORITY)]

            power_limit = self.poe_plat.get_bt_port_class(self.port_id)
            port_class = (power_limit.get(CLASS) >> 4)
            self.class_type = TBL_BT_CLASS_TO_CFG[port_class]
            self.power_limit = power_limit.get(TPPL)

            meas = self.poe_plat.get_bt_port_measurements(self.port_id)
            self.current = meas.get(CURRENT)
            self.power_consump = meas.get(POWER_CONSUMP)
            self.voltage = meas.get(VOLTAGE)
        else:
            status = self.poe_plat.get_port_status(self.port_id)
            self.enDis = TBL_ENDIS_TO_CFG[status.get(ENDIS)]
            self.status = TBL_STATUS_TO_CFG[status.get(STATUS)]
            self.latch = status.get(LATCH)
            self.class_type = TBL_CLASS_TO_CFG[status.get(CLASS)]
            self.protocol = TBL_PROTOCOL_TO_CFG[status.get(PROTOCOL)]
            self.FPairEn = status.get(EN_4PAIR)

            priority = self.poe_plat.get_port_priority(self.port_id)
            self.priority = TBL_PRIORITY_TO_CFG[priority.get(PRIORITY)]

            power_limit = self.poe_plat.get_port_power_limit(self.port_id)
            self.power_limit = power_limit.get(PPL)

            meas = self.poe_plat.get_port_measurements(self.port_id)
            self.current = meas.get(CURRENT)
            self.power_consump = meas.get(POWER_CONSUMP)
            self.voltage = meas.get(VOLTAGE)

    def get_current_status(self, more_info=True):
        self.update_port_status()
        port_status = OrderedDict()
        port_status[PORT_ID] = self.port_id
        port_status[ENDIS] = self.enDis
        port_status[PRIORITY] = self.priority
        port_status[POWER_LIMIT] = self.power_limit
        if more_info == True:
            port_status[STATUS] = self.status
            port_status[LATCH] = self.latch
            port_status[PROTOCOL] = self.protocol
            port_status[EN_4PAIR] = self.FPairEn
            port_status[CLASS] = self.class_type
            port_status[POWER_CONSUMP] = self.power_consump
            port_status[VOLTAGE] = self.voltage / 10
            port_status[CURRENT] = self.current

        return port_status
