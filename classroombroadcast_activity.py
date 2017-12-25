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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from sugar3.activity import bundlebuilder
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics import style

from broadcast import Broadcast


class ClassRoomBroadcastActivity(activity.Activity):
    """Class Room Broadcast Activity
    """

    # Broadcast Component
    _broadcast = None

    # UI
    _toolbar = None

    def __init__(self, handle):
        """Constructor
        """
        # initialize activity
        activity.Activity.__init__(self, handle)

        # debug msg
        logging.debug("Starting Classroom Broadcast Activity")

        # UI
        self.loadUI()

        # create broadcast component
        self._broadcast = Broadcast(self)
        self._broadcast.loadUI()

        # Show UI
        self.showUI()

        # Show status
        self._broadcast.showStatus()

    def loadUI(self):
        """Create and show UI
        """

        # we do not have collaboration features
        # make the share option insensitive
        self.max_participants = 1

        # Toolbar
        toolbar_box = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

    def showUI(self):
        """Show UI elements
        """
        self.show_all()
