from lldb import SBDebugger
from pathlib import Path


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    root_dir = Path(__file__).parent.parent
    # Requrired for all formatters
    dbg.HandleCommand(f"command script import -- {root_dir}/scripts/nerix_common.py")

    def import_one(name: str, script_name = None):
        if not script_name:
            script_name = name

        dbg.HandleCommand(f"command script import -- {root_dir}/{name}/scripts/{script_name}.py")

    import_one("boost-circular-buffer", "boost_circular_buffer")
    import_one("boost-json", "boost_json")
    import_one("boost-unordered", "boost_unordered")
    import_one("qt6")
    import_one("rapidjson")
    import_one("sol2-lua", "lua")

