local function in_a_file(a0, a1)
	local gotten = a0[a1]
	a_c_function_from_file()
	local defined_after = 67
	local used_after = gotten + defined_after
end
function run_in_file()
	local a_table = { foo = 1234 }
	local a_int = 5678
	local a_string = "foo"
	pcall(in_a_file, a_table, a_string)
end
