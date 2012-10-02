# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2009       Nick Hall
# Copyright (C) 2010       Benny Malengier
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Person Tree View
"""

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gui.views.listview import LISTTREE
from gramps.plugins.lib.libpersonview import BasePersonView
from gui.views.treemodels.peoplemodel import PersonTreeModel
import gen.lib
from gen.errors import WindowActiveError
from gui.editors import EditPerson
from gen.utils.db import preset_name

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# PersonTreeView
#
#-------------------------------------------------------------------------
class PersonTreeView(BasePersonView):
    """
    A hierarchical view of the people based on family name.
    """
    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        BasePersonView.__init__(self, pdata, dbstate, uistate,
                               _('People Tree View'), PersonTreeModel,
                               nav_group=nav_group)

    def type_list(self):
        """
        set the listtype, this governs eg keybinding
        """
        return LISTTREE

    def get_viewtype_stock(self):
        """
        Override the default icon.  Set for hierarchical view.
        """
        return 'gramps-tree-group'
        
    def define_actions(self):
        """
        Define actions for the popup menu specific to the tree view.
        """
        BasePersonView.define_actions(self)

        self.all_action.add_actions([
                ('OpenAllNodes', None, _("Expand all Nodes"), None, None, 
                 self.open_all_nodes),  
                ('CloseAllNodes', None, _("Collapse all Nodes"), None, None, 
                 self.close_all_nodes), 
                ])

    def additional_ui(self):
        """
        Defines the UI string for UIManager
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
                <menuitem action="HomePerson"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
                <menuitem action="Merge"/>
             </placeholder>
              <menuitem action="SetActive"/>
              <menuitem action="FilterEdit"/>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="HomePerson"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
              <toolitem action="Merge"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <menuitem action="HomePerson"/>
            <separator/>
            <menuitem action="OpenAllNodes"/>
            <menuitem action="CloseAllNodes"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <menuitem action="Merge"/>
            <separator/>
            <menu name="QuickReport" action="QuickReport"/>
            <menu name="WebConnect" action="WebConnect"/>
          </popup>
        </ui>'''

    def add(self, obj):
        person = gen.lib.Person()
        
        # attempt to get the current surname
        (model, pathlist) = self.selection.get_selected_rows()
        name = gen.lib.Name()
        #the editor requires a surname
        name.add_surname(gen.lib.Surname())
        name.set_primary_surname(0)
        basepers = None
        if len(pathlist) == 1:
            path = pathlist[0]
            pathids = path.get_indices()
            if len(pathids) == 1:
                path = Gtk.TreePath((pathids[0], 0))
            nodeiter = model.do_get_iter(path)[1]
            node = model.get_node_from_iter(nodeiter)
            handle = model.get_handle(node)
            basepers = self.dbstate.db.get_person_from_handle(handle)
        if basepers:
            preset_name(basepers, name)
        person.set_primary_name(name)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass