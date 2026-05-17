# lldb-formatters

This is a collection of formatters I use with LLDB. It's very much a WIP and used to test the native PDB parser.

**Tested Platforms**

All tests use LLDB 22.

- Windows, clang-cl 22+, PDB/CodeView
- Linux, Clang 21+ and GCC 15+

## Use

Clone this repository.
You don't need to configure or build anything if you only want to use the formatters.

```
# Requried for all formatters
command script import scripts/nerix_common.py
# For each library (see below)
command script import <library-name>/scripts/<library_name>.py
```

> [!NOTE]
>
> When running on Windows, consider linking with LLD instead of the default linker (`link.exe`).
> There are some bugs with LLDB and PDBs produced by `link.exe` with incremental linking (https://github.com/llvm/llvm-project/issues/187883).

## Test

Make sure to clone the submodules (`git submodule update --init --recursive`).
Use the `build-test-debug` preset to build and test the project:

```
cmake --preset base-test-debug
cd build
ninja
ctest
```

## Libraries

### Qt 6

- **Directory**: `qt6`
- **Available Types**: See readme in [qt6/](./qt6/README.md#types).
- **Install**:
  ```sh
  command script import <path-to>/qt6/scripts/qt6.py
  ```

> [!NOTE]
>
> The QJson\* formatters require the `QJson{Array,Object,Value}` types to be available.
> This might not always be the case.
> Check if the types are available using `type lookup QJsonArray`.

### Lua and Sol2

Both Lua and sol2 share the same Python file.

- **Lua Version**: 5.4
- **Directory**: `sol2-lua`
- **Available Types**:
  - [x] `TValue`
  - [x] `TString`
  - [x] `Table`
  - [x] `CClosure`
  - [x] `global_State`
  - [x] `lua_State`
  - [x] `Udata`
  - [x] `sol::variadic_args`
  - [x] `sol::basic_reference`
  - [x] `sol::basic_object`
  - [x] `sol::basic_table_core`
  - [x] `sol::basic_protected_function`

- **Install**:
  ```sh
  command script import <path-to>/sol2-lua/scripts/lua.py
  ```

### Boost.Unordered

- **Directory**: [`boost-unordered`](./boost-unordered)
- **Available Types**:
  - [x] `boost::unordered::unordered_(multi)(map|set)`
  - [x] `boost::unordered::unordered_(node|flat)_(map|set)`
  - [x] `boost::unordered::concurrent_(node|flat)_(map|set)`
  - [x] Map/Set iterators

- **Install**:
  ```sh
  command script import <path-to>/boost-unordered/scripts/boost_unordered.py
  ```

### Boost.Json

- **Directory**: [`boost-json`](./boost-json)
- **Available Types**:
  - [x] `boost::json::value`
  - [x] `boost::json::object`
  - [x] `boost::json::array`
  - [x] `boost::json::string`
  - [x] `boost::json::key_value_pair`

- **Install**:
  ```sh
  command script import <path-to>/boost-json/scripts/boost_json.py
  ```

### Boost.CircularBuffer

- **Directory**: [`boost-circular-buffer`](./boost-circular-buffer)
- **Available Types**:
  - [x] `boost::circular_buffer`
  - [x] `boost::circular_buffer_space_optimized`
  - [x] Iterators

- **Install**:
  ```sh
  command script import <path-to>/boost-circular-buffer/scripts/boost_circular_buffer.py
  ```

### Rapidjson

- **Directory**: [`rapidjson`](./rapidjson)
- **Available Types**:
  - [x] `rapidjson::GenericValue<*>`

- **Install**:
  ```sh
  command script import <path-to>/rapidjson/scripts/rapidjson.py
  ```
