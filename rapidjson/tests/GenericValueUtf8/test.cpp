#include <rapidjson/document.h>
#include <rapidjson/rapidjson.h>

int main()
{
    rapidjson::MemoryPoolAllocator<> alloc;
    rapidjson::Value empty;
    rapidjson::Value vInt(1234);
    rapidjson::Value vUint(1234u);
    rapidjson::Value vInt64(1234LL);
    rapidjson::Value vUint64(1234ULL);
    rapidjson::Value vDouble(1.25);
    rapidjson::Value vTrue(true);
    rapidjson::Value vFalse(false);
    rapidjson::Value vShortStr("short", alloc);
    rapidjson::Value vLongStr("quite a long string that has to be allocated...",
                              alloc);

    rapidjson::Value vArray(rapidjson::kArrayType);
    vArray.PushBack(rapidjson::kNullType, alloc);
    vArray.PushBack(1234, alloc);
    vArray.PushBack(1234u, alloc);
    vArray.PushBack(-1234, alloc);
    vArray.PushBack(true, alloc);
    vArray.PushBack(false, alloc);
    vArray.PushBack("short", alloc);
    vArray.PushBack("quite a long string that has to be allocated2...", alloc);

    rapidjson::Value vArray2(rapidjson::kArrayType);
    vArray2.PushBack("abc", alloc);
    vArray.PushBack(rapidjson::Value(vArray2, alloc), alloc);

    rapidjson::Value vSmallObj(rapidjson::kObjectType);
    vSmallObj.AddMember("a", true, alloc);
    vSmallObj.AddMember("b", false, alloc);
    vSmallObj.AddMember("c", "abc", alloc);
    vArray.PushBack(rapidjson::Value(vSmallObj, alloc), alloc);

    rapidjson::Value vObject(rapidjson::kObjectType);
    vObject.AddMember("int", 123, alloc);
    vObject.AddMember("null", rapidjson::kNullType, alloc);
    vObject.AddMember("uint", 456u, alloc);
    vObject.AddMember("int64", 123LL, alloc);
    vObject.AddMember("uint64", 123ULL, alloc);
    vObject.AddMember("double", 1.25, alloc);
    vObject.AddMember("true", true, alloc);
    vObject.AddMember("false", false, alloc);
    vObject.AddMember("string", "abc", alloc);
    vObject.AddMember("longString",
                      "a long string so write something here to overshoot",
                      alloc);
    vObject.AddMember("array", rapidjson::Value(vArray, alloc), alloc);
    vObject.AddMember("object", rapidjson::Value(vSmallObj, alloc), alloc);
    vObject.AddMember("aLongMemberNameThatHasToBeAllocated", "ok", alloc);

    return 0;  // break here
}
