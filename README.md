# lldb-formatters

This is a collection of formatters I use with LLDB. It's very much a WIP and used to test the native PDB parser.

There is no test-suite yet, but I'd like to add one at some point. That would make it easier to upgrade versions of libraries.

## Use

Most libraries can be used by running `command script import <path-to-script>`.
When running with lldb-dap, having `enableSyntheticChildDebugging` enabled helps a lot.

> [!NOTE]
>
> When running on Windows, consider linking with LLD instead of the default linker (`link.exe`).
> There are some bugs with LLDB and PDBs produced by `link.exe` with incremental linking (https://github.com/llvm/llvm-project/issues/187883).

## Test

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
> Some formatters, most notably the ones for the `QJson*` types, require Qt to be compiled with debug info. On Windows, add the debug info files when installing and use `settings append target.debug-file-search-paths <path-to>/msvc2022_64/bin` to add the files to the search path.

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

TODO

### Boost.Json

TODO

### Rapidjson

TODO
