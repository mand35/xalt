#-----------------------------------------------------------------------
# XALT: A tool to track the programs on a cluster.
# Copyright (C) 2013-2014 Robert McLay and Mark Fahey
# 
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of 
# the License, or (at your option) any later version. 
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser  General Public License for more details. 
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA 02111-1307 USA
#-----------------------------------------------------------------------
from __future__  import print_function
import os, sys, json, base64

from XALTdb      import XALTdb
from XALT_Rmap   import Rmap
from xalt_global import *

class XALT_transmission_factory(object):
  def __init__(self, syshost, kind):
    self.__syshost = syshost
    self.__kind    = kind

  def _syshost(self):
    return self.__syshost

  def _kind(self):
    return self.__kind

  @staticmethod
  def build(name, syshost, kind, fn):
    name = name.lower()
    if (name == "syslog"):
      obj = Syslog(syshost, kind)
    elif (name == "directdb"):
      obj = DirectDB(syshost, kind)
    else:                 
      # file
      obj = File(syshost, kind, fn)
      
    return obj

class Syslog(XALT_transmission_factory):

  def __init__(self, syshost, kind):
    super(Syslog, self).__init__(syshost, kind)
  def save(self, resultT):
    sA = []
    sA.append("logger -t XALT_LOGGING")
    sA.append(" \"")
    sA.append(self._kind())
    sA.append(":")
    sA.append(self._syshost())
    sA.append(":")
    sA.append(base64.b64encode(json.dumps(resultT)))
    sA.append("\"")
    s = "".join(sA)
    os.system(s)
    

class File(XALT_transmission_factory):

  def __init__(self, syshost, kind, fn):
    super(File, self).__init__(syshost, kind)
    self.__fn      = fn
  def save(self, resultT):
    s           = json.dumps(resultT, sort_keys=True,
                             indent=2, separators=(',',': '))
    dirname, fn = os.path.split(self.__fn)
    tmpFn       = os.path.join(dirname, "." + fn)
    if (not os.path.isdir(dirname)):
      os.mkdir(dirname);
    
    f = open(tmpFn,"w")
    f.write(s)
    f.close()
    os.rename(tmpFn, self.__fn)


class DirectDB(XALT_transmission_factory):

  def __init__(self, syshost, kind):
    super(DirectDB, self).__init__(syshost, kind)
  def save(self, resultT):
    ConfigFn     = pathJoin(XALT_ETC_DIR,"xalt_db.conf")
    RMapFn       = pathJoin(XALT_ETC_DIR,"reverseMapD")

    xalt        = XALTdb(ConfigFn)
    reverseMapT = Rmap(RMapFn).reverseMapT()
    if (self._kind() == "link"):
      xalt.link_to_db(reverseMapT, resultT)
    else: 
      # kind == "run"
      xalt.run_to_db(reverseMapT, resultT)

