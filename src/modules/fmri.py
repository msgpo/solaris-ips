#!/usr/bin/python
#
# CDDL HEADER START
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
# or http://www.opensolaris.org/os/licensing.
# See the License for the specific language governing permissions
# and limitations under the License.
#
# When distributing Covered Code, include this CDDL HEADER in each
# file and include the License file at usr/src/OPENSOLARIS.LICENSE.
# If applicable, add the following below this CDDL HEADER, with the
# fields enclosed by brackets "[]" replaced with your own identifying
# information: Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#
# Copyright 2007 Sun Microsystems, Inc.  All rights reserved.
# Use is subject to license terms.
#

import exceptions
import re
from version import Version, DotSequence

class PkgFmri(object):
        """The authority is the anchor of a package namespace.  Clients can
        choose to take packages from multiple authorities, and specify a default
        search path.  In general, package names may also be prefixed by a domain
        name, reverse domain name, or a stock symbol to avoid conflict.  The
        unprefixed namespace is expected to be managed by architectural review.

        The primary equivalence relationship assumes that packages of the same
        package name are forwards compatible across all versions of that
        package, and that higher build release versions are superior
        publications than lower build release versions."""

        def __init__(self, fmri, build_release):
                """XXX pkg:/?pkg_name@version not presently supported."""
                m = re.match("pkg://([^/]*)/([^@]*)@([\d\,\.\-\:]*)", fmri)
                if m != None:
                        self.authority = m.group(1)
                        self.pkg_name = m.group(2)
                        self.version = Version(m.group(3), build_release)

                        return

                m = re.match("pkg://([^/]*)/([^@]*)", fmri)
                if m != None:
                        self.authority = m.group(1)
                        self.pkg_name = m.group(2)
                        self.version = None

                        return

                m = re.match("pkg:/([^/][^@]*)@([\d\,\.\-\:]*)", fmri)
                if m != None:
                        # XXX Replace with server's default authority.
                        self.authority = None
                        self.pkg_name = m.group(1)
                        self.version = Version(m.group(2), build_release)

                        return

                m = re.match("pkg:/([^/][^@]*)", fmri)
                if m != None:
                        # XXX Replace with server's default authority.
                        self.authority = None
                        self.pkg_name = m.group(1)
                        self.version = None

                        return
                m = re.match("([^@]*)@([\d\,\.\-\:]*)", fmri)
                if m != None:
                        # XXX Replace with server's default authority.
                        self.authority = None
                        self.pkg_name = m.group(1)
                        self.version = Version(m.group(2), build_release)

                        return

                m = re.match("([^@]*)", fmri)
                if m != None:
                        # XXX Replace with server's default authority.
                        self.authority = None
                        self.pkg_name = m.group(1)
                        self.version = None

                        return

        def get_authority(self):
                return self.authority

        def set_authority(self, authority):
                self.authority = authority

        def __str__(self):
                """Return as specific an FMRI representation as possible."""
                if self.authority == None:
                        if self.version == None:
                                return "pkg:/%s" % self.pkg_name

                        return "pkg:/%s@%s" % (self.pkg_name, self.version)

                if self.version == None:
                        return "pkg://%s/%s" % (self.authority, self.pkg_name)

                return "pkg://%s/%s@%s" % (self.authority, self.pkg_name,
                                self.version)

        def get_pkg_stem(self):
                """Return a string representation of the FMRI without a specific
                version."""
                if self.authority == None:
                        return "pkg:/%s" % self.pkg_name

                return "pkg://%s/%s" % (self.authority, self.pkg_name)

        def is_same_pkg(self, other):
                if self.authority != other.authority:
                        return False

                # XXX XXX
                return

        def tuple(self):
                return self.authority, self.pkg_name, self.version

        def is_similar(self, fmri):
                """True if package names match exactly.  Not a pattern-based
                query."""
                return self.pkg_name == fmri.pkg_name

        def is_successor(self, fmri):
                if not self.pkg_name == fmri.pkg_name:
                        return False

                # XXX Unequal authorities as a strictness criteria?

                if fmri.version == None:
                        return False

                if self.version == None:
                        return True

                if self.version < fmri.version:
                        return False

                return True

        def set_timestamp(self, new_ts):
                self.version.set_timestamp(new_ts)

        def get_timestamp(self, new_ts):
                return self.version.get_timestamp()

if __name__ == "__main__":
        n1 = PkgFmri("pkg://pion/sunos/coreutils", "5.9")
        n2 = PkgFmri("sunos/coreutils", "5.10")
        n3 = PkgFmri("sunos/coreutils@5.10", "5.10")
        n4 = PkgFmri("sunos/coreutils@6.7,5.10-2:786868787", "5.10")
        n5 = PkgFmri("sunos/coreutils@6.6,5.10-2:786868787", "5.10")
        n6 = PkgFmri("coreutils", None)

        print n1
        print n2
        print n3

        assert not n1.is_successor(n2)
        assert n4.is_successor(n3)
        assert not n5.is_successor(n4)

        assert n4.is_similar(n2)
        assert n1.is_similar(n2)
        assert not n1.is_similar(n6)

