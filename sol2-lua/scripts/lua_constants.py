LUA_TNONE = -1
LUA_TNIL = 0
LUA_TBOOLEAN = 1
LUA_TLIGHTUSERDATA = 2
LUA_TNUMBER = 3
LUA_TSTRING = 4
LUA_TTABLE = 5
LUA_TFUNCTION = 6
LUA_TUSERDATA = 7
LUA_TTHREAD = 8

LUA_NUMTYPES = 9

LUA_TUPVAL = LUA_NUMTYPES
"""upvalues"""
LUA_TPROTO = LUA_NUMTYPES + 1
"""function prototypes"""

LUA_NOREF = -2
LUA_REFNIL = -1


def _make_variant(t: int, v: int):
    return t | (v << 4)


LUA_VNIL = _make_variant(LUA_TNIL, 0)
"""Standard nil"""
LUA_VEMPTY = _make_variant(LUA_TNIL, 1)
"""Empty slot (which might be different from a slot containing nil)"""
LUA_VABSTKEY = _make_variant(LUA_TNIL, 2)
"""Value returned for a key not found in a table (absent key)"""
LUA_VFALSE = _make_variant(LUA_TBOOLEAN, 0)
"""constant false"""
LUA_VTRUE = _make_variant(LUA_TBOOLEAN, 1)
"""constant true"""
LUA_VTHREAD = _make_variant(LUA_TTHREAD, 0)
"""lua thread"""
LUA_VNUMINT = _make_variant(LUA_TNUMBER, 0)
"""integer numbers"""
LUA_VNUMFLT = _make_variant(LUA_TNUMBER, 1)
"""float numbers"""
LUA_VSHRSTR = _make_variant(LUA_TSTRING, 0)
"""short strings"""
LUA_VLNGSTR = _make_variant(LUA_TSTRING, 1)
"""long strings"""
LUA_VLIGHTUSERDATA = _make_variant(LUA_TLIGHTUSERDATA, 0)
"""lightuserdata"""
LUA_VUSERDATA = _make_variant(LUA_TUSERDATA, 0)
"""userdata"""
LUA_VPROTO = _make_variant(LUA_TPROTO, 0)
"""function prototype"""
LUA_VUPVAL = _make_variant(LUA_TUPVAL, 0)
"""upvalue"""
LUA_VLCL = _make_variant(LUA_TFUNCTION, 0)
"""Lua closure"""
LUA_VLCF = _make_variant(LUA_TFUNCTION, 1)
"""light C function"""
LUA_VCCL = _make_variant(LUA_TFUNCTION, 2)
"""C closure"""
LUA_VTABLE = _make_variant(LUA_TTABLE, 0)
"""table"""
