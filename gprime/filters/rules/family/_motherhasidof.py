#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from .. import RegExpIdBase
from ._memberbase import mother_base

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class MotherHasIdOf(RegExpIdBase):
    """Rule that checks for a person with a specific GID"""

    labels      = [ _('Person ID:') ]
    name        = _('Families having mother with Id containing <text>')
    description = _("Matches families whose mother has a specified "
                    "GID")
    category    = _('Mother filters')
    base_class = RegExpIdBase
    apply = mother_base
