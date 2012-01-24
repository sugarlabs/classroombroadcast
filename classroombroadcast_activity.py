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
        self._broadcast.loadUI();

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
        toolbox = ActivityToolbox(self)
        self._toolbar = toolbox.get_activity_toolbar()

        self._toolbar.remove(self._toolbar.share)
        self._toolbar.share = None
        self._toolbar.remove(self._toolbar.keep)
        self._toolbar.keep = None
        self.set_toolbox(toolbox)

    def showUI(self):
        """Show UI elements
        """
        self.show_all()
