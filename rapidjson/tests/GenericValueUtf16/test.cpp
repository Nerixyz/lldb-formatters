#include <rapidjson/document.h>
#include <rapidjson/rapidjson.h>

using Value = rapidjson::GenericValue<rapidjson::UTF16<char16_t>>;

int main()
{
    rapidjson::MemoryPoolAllocator<> alloc;
    Value empty;
    Value vInt(1234);
    Value vUint(1234u);
    Value vInt64(1234LL);
    Value vUint64(1234ULL);
    Value vDouble(1.25);
    Value vTrue(true);
    Value vFalse(false);
    Value vShortStr(u"short", alloc);
    Value vLongStr(u"quite a long string that has to be allocated...", alloc);

    Value vArray(rapidjson::kArrayType);
    vArray.PushBack(rapidjson::kNullType, alloc);
    vArray.PushBack(1234, alloc);
    vArray.PushBack(1234u, alloc);
    vArray.PushBack(-1234, alloc);
    vArray.PushBack(true, alloc);
    vArray.PushBack(false, alloc);
    vArray.PushBack(u"short", alloc);
    vArray.PushBack(u"quite a long string that has to be allocated2...", alloc);

    Value vArray2(rapidjson::kArrayType);
    vArray2.PushBack(u"abc", alloc);
    vArray.PushBack(Value(vArray2, alloc), alloc);

    Value vSmallObj(rapidjson::kObjectType);
    vSmallObj.AddMember(u"a", true, alloc);
    vSmallObj.AddMember(u"b", false, alloc);
    vSmallObj.AddMember(u"c", u"abc", alloc);
    vArray.PushBack(Value(vSmallObj, alloc), alloc);

    Value vObject(rapidjson::kObjectType);
    vObject.AddMember(u"int", 123, alloc);
    vObject.AddMember(u"null", rapidjson::kNullType, alloc);
    vObject.AddMember(u"uint", 456u, alloc);
    vObject.AddMember(u"int64", 123LL, alloc);
    vObject.AddMember(u"uint64", 123ULL, alloc);
    vObject.AddMember(u"double", 1.25, alloc);
    vObject.AddMember(u"true", true, alloc);
    vObject.AddMember(u"false", false, alloc);
    vObject.AddMember(u"string", u"abc", alloc);
    vObject.AddMember(u"longString",
                      u"a long string so write something here to overshoot",
                      alloc);
    vObject.AddMember(u"array", Value(vArray, alloc), alloc);
    vObject.AddMember(u"object", Value(vSmallObj, alloc), alloc);
    vObject.AddMember(u"aLongMemberNameThatHasToBeAllocated", u"ok", alloc);

    return 0;  // break here
}
