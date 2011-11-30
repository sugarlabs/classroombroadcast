# Copyright (C) 2011, Ariel Calzada <ariel.calzada@gmail.com>.
# Copyright (C) 2008, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
from gettext import gettext as _
from sugar.activity import activity
from sugar.activity.activity import ActivityToolbox
import gtk
import subprocess
import os
import signal
import socket
import fcntl
import struct
import commands


class ClassRoomBroadcastActivity(activity.Activity):
    """Class Room Broadcast Activity
    """

    # Color constants
    _greenBG = '#00E500'
    _redBG = '#FF0000'

    # GUI
    _box = None
    _button = None
    _label = None
    _toolbar = None
    _boxAlign = None

    def __init__(self, handle):
        """Class constructor
        """

        # Initialize parent class
        activity.Activity.__init__(self, handle)

        # Remove colaboration features
        self.max_participants = 1

        # Debug msg
        logging.debug("Starting Class Room Broadcast Activity")

        # Load GUI
        self.loadGUI()

    def loadGUI(self):
        """Create and show GUI
        """

        # Toolbar
        toolbox = ActivityToolbox(self)
        self._toolbar = toolbox.get_activity_toolbar()
        self._toolbar.remove(self._toolbar.share)
        self._toolbar.share = None
        self.set_toolbox(toolbox)

        # Box
        self._box = gtk.VBox()

        # Label
        self._label = gtk.Label()

        # Button
        self._button = gtk.Button()
        status = self.checkStatus()

        if status[0]:
            self.showServerStatus("on")
        else:
            self.showServerStatus("off")

        self._button.set_size_request(200, 200)
        self._button.connect("clicked", self.buttonClicked)

        # Add button to box
        self._box.pack_start(self._button)

        # Add label to box
        self._box.pack_start(self._label, padding=20)

        # Box Align (xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0)
        self._boxAlign = gtk.Alignment(0.5, 0.5, 0, 0)
        self._boxAlign.add(self._box)

        # Set canvas with box alignment
        self.set_canvas(self._boxAlign)

        # Show all
        self.show_all()

    def setButtonBG(self, color):
        """Change button bg color
        """
        self._button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))

    def setButtonLabel(self, txt):
        """Change button label
        """
        self._button.set_label(txt)

    def setLabelTXT(self, txt):
        """Change button label
        """
        self._label.set_label(txt)

    def showServerStatus(self, state="off"):
        if state == "off":
            self.setButtonBG(self._greenBG)
            self.setButtonLabel("Start")
            self.setLabelTXT("")
        else:
            self.setButtonBG(self._redBG)
            self.setButtonLabel("Stop")
            status = self.checkStatus()
            txt = "Process ID = " + ",".join(status[1])
            txt += "\n"
            txt += "Hostname = " + self.getHostname()
            txt += "\n"
            txt += "IPs = " + self.getNetworkInfo()
            self.setLabelTXT(txt)

    def buttonClicked(self, widget, data=None):
        """Button clicked event handler
        """

        status = self.checkStatus()

        if status[0]:
            self.stopServer()
            self.showServerStatus("off")
        else:
            self.startServer()
            self.showServerStatus("on")

    def checkStatus(self):
        """Check if X11VNC is running
        """
        result = []

        psCMD = ['ps', 'ax']
        ps = subprocess.Popen(psCMD, stdout=subprocess.PIPE)

        grepCMD = ['grep', 'x11vnc']
        grep = subprocess.Popen(grepCMD, stdin=ps.stdout, stdout=subprocess.PIPE)

        output = grep.communicate()[0]

        ps.stdout.close()
        grep.stdout.close()

        procs = output.split("\n")

        for proc in procs:
            if proc == "":
                continue

            fields = proc.split()

            procName = fields[4]
            pid = fields[0]

            if procName != "x11vnc":
                continue

            result.append(pid)

        if len(result) > 0:
            return [True, result]

        return [False, []]

    def startServer(self):
        """Start vnc server
        """
        cmd = ["x11vnc", "-viewonly", "-shared", "-bg"]
        subprocess.call(cmd, shell=False)

    def stopServer(self):
        """Stop vnc server
        """
        status = self.checkStatus()
        pids = status[1]

        for pid in pids:
            os.system("kill -9 " + pid)

        self.showServerStatus("off")

    def getHostname(self):
        return socket.gethostname()

    def getNetworkInterfaces(self):
        f = open('/proc/net/dev', 'r')
        lines = f.readlines()
        f.close()
        lines.pop(0)
        lines.pop(0)

        interfaces = []
        for line in lines:
            interface = line.strip().split(" ")[0].split(":")[0].strip()
            interfaces.append(interface)

        return interfaces

    def getNetworkIPs(self, interfaces):
        pattern = "inet addr:"
        cmdName = "/sbin/ifconfig"
        ips = {}

        for interface in interfaces:
            cmd = cmdName + " " + interface
            output = commands.getoutput(cmd)
            inet = output.find(pattern)

            if inet >= 0:
                start = inet + len(pattern)
                end = output.find(" ", start)

                ip = output[start:end]
                ips[interface] = ip
            else:
                ips[interface] = ""

        return ips

    def getNetworkInfo(self):
        info = ""

        interfaces = self.getNetworkInterfaces()
        ips = self.getNetworkIPs(interfaces)

        for interface, ip in ips.iteritems():
            if info != "":
                info += "\n         "

            info += interface + ": " + ip

        return info
