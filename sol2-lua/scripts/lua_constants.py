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

CIST_OAH = 1 << 0
"""original value of 'allowhook'"""
CIST_C = 1 << 1
"""call is running a C function"""
CIST_FRESH = 1 << 2
"""call is on a fresh "luaV_execute" frame"""
CIST_HOOKED = 1 << 3
"""call is running a debug hook"""
CIST_YPCALL = 1 << 4
"""doing a yieldable protected call"""
CIST_TAIL = 1 << 5
"""call was tail called"""
CIST_HOOKYIELD = 1 << 6
"""last hook called yielded"""
CIST_FIN = 1 << 7
"""function "called" a finalizer"""
CIST_TRAN = 1 << 8
"""'ci' has transfer information"""
CIST_CLSRET = 1 << 9
"""function is closing tbc variables"""


# Constants for OpCode. CodeView doesn't include typedefs, so we can't find OpCode there.
class OpCode:
    OP_MOVE = 0x0
    OP_LOADI = 0x1
    OP_LOADF = 0x2
    OP_LOADK = 0x3
    OP_LOADKX = 0x4
    OP_LOADFALSE = 0x5
    OP_LFALSESKIP = 0x6
    OP_LOADTRUE = 0x7
    OP_LOADNIL = 0x8
    OP_GETUPVAL = 0x9
    OP_SETUPVAL = 0xA
    OP_GETTABUP = 0xB
    OP_GETTABLE = 0xC
    OP_GETI = 0xD
    OP_GETFIELD = 0xE
    OP_SETTABUP = 0xF
    OP_SETTABLE = 0x10
    OP_SETI = 0x11
    OP_SETFIELD = 0x12
    OP_NEWTABLE = 0x13
    OP_SELF = 0x14
    OP_ADDI = 0x15
    OP_ADDK = 0x16
    OP_SUBK = 0x17
    OP_MULK = 0x18
    OP_MODK = 0x19
    OP_POWK = 0x1A
    OP_DIVK = 0x1B
    OP_IDIVK = 0x1C
    OP_BANDK = 0x1D
    OP_BORK = 0x1E
    OP_BXORK = 0x1F
    OP_SHRI = 0x20
    OP_SHLI = 0x21
    OP_ADD = 0x22
    OP_SUB = 0x23
    OP_MUL = 0x24
    OP_MOD = 0x25
    OP_POW = 0x26
    OP_DIV = 0x27
    OP_IDIV = 0x28
    OP_BAND = 0x29
    OP_BOR = 0x2A
    OP_BXOR = 0x2B
    OP_SHL = 0x2C
    OP_SHR = 0x2D
    OP_MMBIN = 0x2E
    OP_MMBINI = 0x2F
    OP_MMBINK = 0x30
    OP_UNM = 0x31
    OP_BNOT = 0x32
    OP_NOT = 0x33
    OP_LEN = 0x34
    OP_CONCAT = 0x35
    OP_CLOSE = 0x36
    OP_TBC = 0x37
    OP_JMP = 0x38
    OP_EQ = 0x39
    OP_LT = 0x3A
    OP_LE = 0x3B
    OP_EQK = 0x3C
    OP_EQI = 0x3D
    OP_LTI = 0x3E
    OP_LEI = 0x3F
    OP_GTI = 0x40
    OP_GEI = 0x41
    OP_TEST = 0x42
    OP_TESTSET = 0x43
    OP_CALL = 0x44
    OP_TAILCALL = 0x45
    OP_RETURN = 0x46
    OP_RETURN0 = 0x47
    OP_RETURN1 = 0x48
    OP_FORLOOP = 0x49
    OP_FORPREP = 0x4A
    OP_TFORPREP = 0x4B
    OP_TFORCALL = 0x4C
    OP_TFORLOOP = 0x4D
    OP_SETLIST = 0x4E
    OP_CLOSURE = 0x4F
    OP_VARARG = 0x50
    OP_VARARGPREP = 0x51
    OP_EXTRAARG = 0x52
