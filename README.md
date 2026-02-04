# lldb-formatters

This is a collection of formatters I use with LLDB. It's very much a WIP and used to test the native PDB parser.

There is no test-suite yet, but I'd like to add one at some point. That would make it easier to upgrade versions of libraries.

## Use

Most libraries can be used by running `command script import <path-to-script>`.
When running with lldb-dap, having `enableSyntheticChildDebugging` enabled helps a lot.

> [!NOTE]
>
> When running on Windows, consider linking with LLD instead of the default linker (`link.exe`).
> There are some bugs with LLDB and PDBs produced by `link.exe` with incremental linking that I haven't been able to reliably reproduce.

## Test

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
