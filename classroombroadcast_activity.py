# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,

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
import socket
import commands

from sugar.presence import presenceservice

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

    # Telepathy
    _presence = None
    _owner = None

    def __init__(self, handle):
        """Class constructor
        """

        # Initialize parent class
        activity.Activity.__init__(self, handle)

        # Debug msg
        logging.debug("Starting Class Room Broadcast Activity")

        # Load GUI
        self.loadGUI()

        # Telepathy handler
        self.telepathyHandler()

    def telepathyHandler(self):
        """Telepathy handler
        """
        self._presence = presenceservice.get_instance()
        self._owner = self._presence.get_owner()

        # Event subscribers
        self.connect('shared', self._shared_cb)
        self.connect('joined', self._joined_cb)

    def _sharing_setup(self):
        """Setup variables for sharing action
        """
        if not self._shared_activity:
            return

        self.conn       = self._shared_activity.telepathy_conn
        self.tubes_chan = self._shared_activity.telepathy_tubes_chan
        self.text_chan  = self._shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal('NewTube', self._new_tube_cb)

        self._shared_activity.connect('buddy-joined', self._buddy_joined_cb)
        self._shared_activity.connect('buddy-left',   self._buddy_left_cb)


    def _shared_cb(self, activity):
        """Handler for share state
        """
        status = self.checkStatus()

        # If server is running abort this method
        if status[0]:
            return

        self._sharing_setup()

        estructura = "%s %s" % (SERVIDOR, "-viewonly -forever -solid -shared -wireframe")
        self.server = subprocess.Popen(estructura, shell=True, stdin=subprocess.PIPE,
        stdout=open(STDOUT, "w+b"), stderr=open(STDOUT, "r+b"), universal_newlines=True)
        ids = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(SERVICE, {})



    def _joined_cb(self, activity):
        # me conecto.
        if not self._shared_activity:
                return
        self.initiating = False
        self._sharing_setup()
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(reply_handler=self._list_tubes_reply_cb, error_handler=self._list_tubes_error_cb)



    def loadGUI(self):
        """Create and show GUI
        """

        # Toolbar
        toolbox = ActivityToolbox(self)
        self._toolbar = toolbox.get_activity_toolbar()
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
            self.setButtonLabel(_("Start"))
            self.setLabelTXT("")
        else:
            self.setButtonBG(self._redBG)
            self.setButtonLabel(_("Stop"))
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

    def startServer(self):
        """Start vnc server
        """
        cmd = ["x11vnc", "-viewonly", "-shared", "-bg", "-forever", "-solid", "-wireframe"]

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
        """Get server name
        """
        return socket.gethostname()

    def getNetworkInterfaces(self):
        """Get server network interfaces names
        """
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
        """Get server IPs per interface
        """
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
        """Get server network map {IFACE:IP}
        """
        info = ""

        interfaces = self.getNetworkInterfaces()
        ips = self.getNetworkIPs(interfaces)

        for interface, ip in ips.iteritems():
            if info != "":
                info += "\n         "

            info += interface + ": " + ip

        return info

    def checkStatus(self):
        """Check if X11VNC is running
        """
        result = []

        ps = subprocess.Popen(["pidof","x11vnc"],stdout=subprocess.PIPE)
        pid = ps.communicate()[0].strip().split(" ")
        ps.stdout.close()
        pids = []

        # Cleaning step
        for p in pid:
            p = p.strip()

            if p != "":
                pids.append(p)


        if len(pids) > 0:
            return [True, pids]

        return [False, []]

        """
        THIS METHOD IS LESS EFFICIENT THAN USING SHELL COMMAND 'pidof'
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
        """
