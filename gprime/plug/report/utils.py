#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2008       James Friedmann <jfriedmannj@gmail.com>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2015-2016  Paul Franklin
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

"""
A collection of utilities to aid in the generation of reports.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# Gprime modules
#
#------------------------------------------------------------------------
from ...const import LOCALE as glocale
_ = glocale.translation.gettext
from ...datehandler import get_date
from ...display.place import displayer as _pd
from ...utils.file import media_path_full
from ..docgen import IndexMark, INDEX_TYPE_ALP

# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value): # enable deferred translations (see Python docs 22.1.3.4)
    return value

#-------------------------------------------------------------------------
#
#  Convert points to cm and back
#
#-------------------------------------------------------------------------
def pt2cm(pt):
    """
    Convert points to centimeters. Fonts are typically specified in points,
    but the :class:`.BaseDoc` classes use centimeters.

    :param pt: points
    :type pt: float or int
    :returns: equivalent units in centimeters
    :rtype: float
    """
    return pt/28.3465

def cm2pt(cm):
    """
    Convert centimeters to points. Fonts are typically specified in points,
    but the :class:`.BaseDoc` classes use centimeters.

    :param cm: centimeters
    :type cm: float or int
    :returns: equivalent units in points
    :rtype: float
    """
    return cm*28.3465

def rgb_color(color):
    """
    Convert color value from 0-255 integer range into 0-1 float range.

    :param color: list or tuple of integer values for red, green, and blue
    :type color: int
    :returns: (r, g, b) tuple of floating point color values
    :rtype: 3-tuple
    """
    r = float(color[0])/255.0
    g = float(color[1])/255.0
    b = float(color[2])/255.0
    return (r, g, b)

#-------------------------------------------------------------------------
#
#  Roman numbers
#
#-------------------------------------------------------------------------
def roman(num):
    """ Integer to Roman numeral converter for 0 < num < 4000 """
    if not isinstance(num, int):
        return "?"
    if not 0 < num < 4000:
        return "?"
    vals = (1000, 900, 500, 400, 100,  90,  50,  40,  10,   9,   5,   4,   1)
    nums = ( 'M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    retval = ""
    for i in range(len(vals)):
        amount  = int(num / vals[i])
        retval += nums[i] * amount
        num    -= vals[i] * amount
    return retval

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def place_name(db, place_handle):
    if place_handle:
        place = db.get_place_from_handle(place_handle)
        name = _pd.display(db, place)
    else:
        name = ""
    return str(name)

#-------------------------------------------------------------------------
#
# Functions commonly used in reports
#
#-------------------------------------------------------------------------
def insert_image(database, doc, photo, user,
                 w_cm=4.0, h_cm=4.0, alt="", style_name=None, align='right'):
    """
    Insert pictures of a person into the document.

    :type photo: :class:`~.mediaref.MediaRef`
    :type user:  :class:`.gen.user.User`
    :param alt: an alternative text to use. Useful for eg html reports
    :param style_name: style to use for the "alternative text" or captions
    :param align: image alignment: 'left', 'right', 'center', or 'single'
    """

    object_handle = photo.get_reference_handle()
    media = database.get_media_from_handle(object_handle)
    mime_type = media.get_mime_type()
    if mime_type and mime_type.startswith("image"):
        filename = media_path_full(database, media.get_path())
        if os.path.exists(filename):
            doc.add_media(filename, align, w_cm, h_cm,
                                 alt=alt, style_name=style_name,
                                 crop=photo.get_rectangle())
        else:
            user.warn(_("Could not add photo to page"),
                      "%s: %s" % (filename, _('File does not exist')))

#-------------------------------------------------------------------------
#
# find_spouse
#
#-------------------------------------------------------------------------
def find_spouse(person, family):
    spouse_handle = None
    if family:
        if person.get_handle() == family.get_father_handle():
            spouse_handle = family.get_mother_handle()
        else:
            spouse_handle = family.get_father_handle()
    return spouse_handle

#-------------------------------------------------------------------------
#
# find_marriage
#
#-------------------------------------------------------------------------
def find_marriage(database, family):
    for event_ref in family.get_event_ref_list():
        event = database.get_event_from_handle(event_ref.ref)
        if (event and event.type.is_marriage() and
            event_ref.role.is_family()):
            return event
    return None

#-------------------------------------------------------------------------
#
# Indexing function
#
#-------------------------------------------------------------------------
def get_person_mark(db, person):
    """
    Return a IndexMark that can be used to index a person in a report

    :param db: the Gramps database instance
    :param person: the key is for
    """
    if not person:
        return None

    name = person.get_primary_name().get_name()
    birth = " "
    death = " "
    key = ""

    birth_ref = person.get_birth_ref()
    if birth_ref:
        birthEvt = db.get_event_from_handle(birth_ref.ref)
        birth = get_date(birthEvt)

    death_ref = person.get_death_ref()
    if death_ref:
        deathEvt = db.get_event_from_handle(death_ref.ref)
        death = get_date(deathEvt)

    if birth == death == " ":
        key = name
    else:
        key = "%s (%s - %s)" % (name, birth, death)

    return IndexMark( key, INDEX_TYPE_ALP )

#-------------------------------------------------------------------------
#
# Address String
#
#-------------------------------------------------------------------------
def get_address_str(addr):
    """
    Return a string that combines the elements of an address

    :param addr: the Gramps address instance
    """
    str = ""
    elems = [ addr.get_street(),
              addr.get_locality(),
              addr.get_city(),
              addr.get_county(),
              addr.get_state(),
              addr.get_country(),
              addr.get_postal_code(),
              addr.get_phone()   ]

    for info in elems:
        if info:
            if str == "":
                str = info
            else:
                # translators: needed for Arabic, ignore otherwise
                str = _("%(str1)s, %(str2)s") % {'str1':str, 'str2':info}
    return str

#-------------------------------------------------------------------------
#
# People Filters
#
#-------------------------------------------------------------------------
def get_person_filters(person, include_single=True, name_format=None):
    """
    Return a list of filters that are relevant for the given person

    :param person: the person the filters should apply to.
    :type person: :class:`~.person.Person`
    :param include_single: include a filter to include the single person
    :type include_single: boolean
    :param name_format: optional format to control display of person's name
    :type name_format: None or int
    """
    from ...filters import GenericFilter, rules, CustomFilters, DeferredFilter
    from ...display.name import displayer as name_displayer

    if person:
        real_format = name_displayer.get_default_format()
        if name_format is not None:
            name_displayer.set_default_format(name_format)
        name = name_displayer.display(person)
        name_displayer.set_default_format(real_format)
        gid = person.get_gid()
    else:
        # Do this in case of command line options query (show=filter)
        name = _("PERSON")
        gid = ''

    if include_single:
        filt_id = GenericFilter()
        filt_id.set_name(name)
        filt_id.add_rule(rules.person.HasIdOf([gid]))

    all = DeferredFilter(_T_("Entire Database"), None)
    all.add_rule(rules.person.Everyone([]))

    # feature request 2356: avoid genitive form
    des = DeferredFilter(_T_("Descendants of %s"), name)
    des.add_rule(rules.person.IsDescendantOf([gid, 1]))

    # feature request 2356: avoid genitive form
    df = DeferredFilter(_T_("Descendant Families of %s"), name)
    df.add_rule(rules.person.IsDescendantFamilyOf([gid, 1]))

    # feature request 2356: avoid genitive form
    ans = DeferredFilter(_T_("Ancestors of %s"), name)
    ans.add_rule(rules.person.IsAncestorOf([gid, 1]))

    com = DeferredFilter(_T_("People with common ancestor with %s"), name)
    com.add_rule(rules.person.HasCommonAncestorWith([gid]))

    if include_single:
        the_filters = [filt_id, all, des, df, ans, com]
    else:
        the_filters = [all, des, df, ans, com]
    the_filters.extend(CustomFilters.get_filters('Person'))
    return the_filters

#-------------------------------------------------------------------------
#
# Family Filters
#
#-------------------------------------------------------------------------
def get_family_filters(database, family,
                       include_single=True, name_format=None):
    """
    Return a list of filters that are relevant for the given family

    :param database: The database that the family is in.
    :type database: DbBase
    :param family: the family the filters should apply to.
    :type family: :class:`~.family.Family`
    :param include_single: include a filter to include the single family
    :type include_single: boolean
    :param name_format: optional format to control display of person's name
    :type name_format: None or int
    """
    from ...filters import (GenericFilterFactory, rules, CustomFilters,
                            DeferredFamilyFilter)
    from ...display.name import displayer as name_displayer

    if family:
        real_format = name_displayer.get_default_format()
        if name_format is not None:
            name_displayer.set_default_format(name_format)
        fhandle = family.get_father_handle()
        if fhandle:
            father = database.get_person_from_handle(fhandle)
            father_name = name_displayer.display(father)
        else:
            father_name = _("unknown father")
        mhandle = family.get_mother_handle()
        if mhandle:
            mother = database.get_person_from_handle(mhandle)
            mother_name = name_displayer.display(mother)
        else:
            mother_name = _("unknown mother")
        gid = family.get_gid()
        name = _("%(father_name)s and %(mother_name)s (%(family_id)s)") % {
                    'father_name': father_name,
                    'mother_name': mother_name,
                    'family_id': gid}
        name_displayer.set_default_format(real_format)
    else:
        # Do this in case of command line options query (show=filter)
        name = _("FAMILY")
        gid = ''

    if include_single:
        FilterClass = GenericFilterFactory('Family')
        filt_id = FilterClass()
        filt_id.set_name(name)
        filt_id.add_rule(rules.family.HasIdOf([gid]))

    all = DeferredFamilyFilter(_T_("Every family"), None)
    all.add_rule(rules.family.AllFamilies([]))

    # feature request 2356: avoid genitive form
    df = DeferredFamilyFilter(_T_("Descendant Families of %s"), name)
    df.add_rule(rules.family.IsDescendantOf([gid, 1]))

    # feature request 2356: avoid genitive form
    ans = DeferredFamilyFilter(_T_("Ancestor Families of %s"), name)
    ans.add_rule(rules.family.IsAncestorOf([gid, 1]))

    if include_single:
        the_filters = [filt_id, all, df, ans]
    else:
        the_filters = [all, df, ans]
    the_filters.extend(CustomFilters.get_filters('Family'))
    return the_filters
