import subprocess
import os
import socket
import signal

from gettext import gettext as _

class Utilities():
    """Utilities
    """
    # I18N
    _IPS = _('IPs')
    _PROCESSID = _('Process ID')
    _HOSTNAME = _('Hostname')

    def __init__(self):
        """Constructor
        """
        pass

    def checkProgramStatus(self, programName):
        """
        Check if 'programName' is running
        Returns: [ A, [ B ] ]
        A: True | False if the program is running
        B: list of PID
        """
        result = []

        ps = subprocess.Popen(["pidof",programName],stdout=subprocess.PIPE)
        pid = ps.communicate()[0].strip().split(b" ")
        ps.stdout.close()
        pids = []

        for p in pid:
            p = p.strip()

            if p != b"":
                pids.append(p)

        if len(pids) > 0:
            return [True, pids]

        return [False, []]

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
            output = subprocess.getoutput(cmd)
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

        for interface, ip in ips.items():
            if info != "":
                info += "\n         "

            info += interface + ": " + ip

        return info

    def endProgram(self, programName):
        status = self.checkProgramStatus(programName)

        if status [ 0 ] == True:
            pids = status[1]
            for pid in pids:
                os.system(b"kill -9 " + pid)

    def startProgram(self, programName, args=[]):
        fname = "/usr/bin/" + programName
        if not os.path.isfile(fname):
            fname = "./" + programName

        cmd = [fname]

        if len(args) > 0:
            for arg in args:
                cmd.append(arg)

        subprocess.call(cmd, shell=False)

    def getNetworkProcessInfo(self,programName):
        status = self.checkProgramStatus(programName)
        pid = ""
        if status [ 0 ]:
            pid = ",".join(p.decode(errors='ignore') for p in status[1])

        txt = self._PROCESSID + " = " + pid
        txt += "\n"
        txt += self._HOSTNAME + " = " + self.getHostname()
        txt += "\n"
        txt += self._IPS + " = " + self.getNetworkInfo()

        return txt
