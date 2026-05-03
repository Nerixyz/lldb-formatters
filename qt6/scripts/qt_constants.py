class QDateTimeConstants:
    MSECS_PER_SEC = 1000
    SECS_PER_MIN = 60
    MINS_PER_HOUR = 60
    SECS_PER_HOUR = SECS_PER_MIN * MINS_PER_HOUR
    SECS_PER_DAY = SECS_PER_HOUR * 24
    MSECS_PER_MIN = SECS_PER_MIN * MSECS_PER_SEC
    MSECS_PER_HOUR = SECS_PER_HOUR * MSECS_PER_SEC
    MSECS_PER_DAY = SECS_PER_DAY * MSECS_PER_SEC

    JULIAN_DAY_FOR_EPOCH = 2440588
    """result of QDate(1970, 1, 1).toJulianDay()"""
    JULIAN_DAY_MAX = 784354017364
    JULIAN_DAY_MIN = -784350574879

    # https://github.com/qt/qtbase/blob/3814e28f00b4d551b4691f40431c0d324e88e55d/src/corelib/time/qcalendarmath_p.h#L114-L115
    FOUR_YEARS = 4 * 365 + 1
    FIVE_MONTHS = 31 + 30 + 31 + 30 + 31  # Mar-Jul or Aug-Dec.
    FOUR_CENTURIES = 400 * 365 + 97
    # Julian Day number of Gregorian 1 BCE, February 29th:
    LEAP_DAY_GREGORIAN_1BCE = 1721119
    BASE_JD = LEAP_DAY_GREGORIAN_1BCE

    STATUS_TIME_SPEC_MASK = 0x30
    STATUS_TIME_SPEC_SHIFT = 4
    """corelib/time/qdatetime_p.h (QDateTimePrivate::StatusFlag::TimeSpecMask)"""
    STATUS_VALID_DATETIME_MASK = 0x06
    TIME_SPEC_LOCAL = 0


class QHashConstants:
    """QHashPrivate::SpanConstants"""

    SPAN_SHIFT = 7
    N_ENTRIES = 1 << SPAN_SHIFT
    ELEMENT_MASK = N_ENTRIES - 1
    UNUSED_ENTRY = 0xFF


# https://github.com/qt/qtbase/blob/18f23ca2f1b6b7b3ce78819de2ba3bf7fd89b1b0/src/corelib/serialization/qcborvalue.h#L71-L95
# and
# https://github.com/qt/qtbase/blob/18f23ca2f1b6b7b3ce78819de2ba3bf7fd89b1b0/src/corelib/serialization/qcborcommon.h#L29-L34
# enum QCborValue::Type : int {
#   Integer         = 0x00,
#   ByteArray       = 0x40,
#   String          = 0x60,
#   Array           = 0x80,
#   Map             = 0xa0,
#   Tag             = 0xc0,
#
#   // range 0x100 - 0x1ff for Simple Types
#   SimpleType      = 0x100,
#   False           = SimpleType + int(QCborSimpleType::False),     // = 0x114
#   True            = SimpleType + int(QCborSimpleType::True),      // = 0x115
#   Null            = SimpleType + int(QCborSimpleType::Null),      // = 0x116
#   Undefined       = SimpleType + int(QCborSimpleType::Undefined), // = 0x117
#
#   Double          = 0x202,
#
#   // extended (tagged) types
#   DateTime        = 0x10000,
#   Url             = 0x10020,
#   RegularExpression = 0x10023,
#   Uuid            = 0x10025,
#
#   Invalid         = -1
# };
# enum class QCborSimpleType : quint8 {
#   False = 20,    // = 0x14
#   True = 21,     // = 0x15
#   Null = 22,     // = 0x16
#   Undefined = 23 // = 0x17
# };
class QCborValueType:
    """QCborValue::Type"""

    Integer = 0x00
    ByteArray = 0x40
    String = 0x60
    Array = 0x80
    Map = 0xA0
    Tag = 0xC0
    SimpleType = 0x100
    CFalse = 0x114
    CTrue = 0x115
    Null = 0x116
    Undefined = 0x117
    Double = 0x202
    DateTime = 0x10000
    Url = 0x10020
    RegularExpression = 0x10023
    Uuid = 0x10025
    Invalid = -1

    @staticmethod
    def is_simple(ty: int):
        return ty != QCborValueType.Array and ty != QCborValueType.Map


QCBORVALUE_NULL = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x16\x01\0\0\0\0\0\0"
QCBORVALUE_UNDEFINED = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x17\x01\0\0\0\0\0\0"


# https://github.com/qt/qtbase/blob/18f23ca2f1b6b7b3ce78819de2ba3bf7fd89b1b0/src/corelib/serialization/qcborvalue_p.h#L41-L46
# enum ValueFlag : quint32 {
#   IsContainer     = 0x0001,
#   HasByteData     = 0x0002,
#   StringIsUtf16   = 0x0004,
#   StringIsAscii   = 0x0008,
# };
class QtCborElementValueFlag:
    """QtCbor::Element::ValueFlag"""

    IsContainer = 0x0001
    HasByteData = 0x0002
    StringIsUtf16 = 0x0004
    StringIsAscii = 0x0008
