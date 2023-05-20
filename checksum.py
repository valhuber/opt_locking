import decimal

def check_sum(list_arg: list):
    skip_none = True  # work-around for non-repeatable None hash
    if skip_none:     # https://bugs.python.org/issue19224
        real_tuple = []
        for each_entry in list_arg:
            if each_entry is None:
                real_tuple.append(13)
            else:
                real_tuple.append(each_entry)
        result = \
            list(
                map(
                    lambda l:
                        hash(tuple(l)),
                    [ real_tuple ]
                )
            )
    else:
        result = \
            list(
                map(
                    lambda l:
                        hash(tuple(l)),
                    [ list_arg ]
                )
            )
    print(f'check_sum({list_arg}) = {result}')
    return result

checksum_3_lists = \
    list(  # thanks: https://stackoverflow.com/questions/39583070/checksum-for-a-list-of-numbers
        map(
            lambda l:
                hash(tuple(l)),
            [ [1,2], [3,4], [5,6]]
        )
    )
print(f'checksum_3_lists = {checksum_3_lists} - e.g, [-3550055125485641917, 1079245023883434373, -7007623702649218251]\n')

expected = -3550055125485641917
assert expected == check_sum([1, 2])[0], "not repeatable ints"
assert expected == check_sum([1, 2])[0], "not repeatable ints"  # ensure works twice in a row

variable_1_2 = [1, 2]
assert expected == check_sum(variable_1_2)[0], "not repeatable variable"

expected = 6378967857448501442
assert expected == check_sum([1, "hello", decimal.Decimal(2)])[0], "mixed types"

expected = -6838578810036353648
if expected == check_sum([1, "hello", decimal.Decimal(2), None])[0]:
    print( "mixed types with None succeeds with work-around for hash(None)")
else:
    print( "..FAILS - None makes hash fail...\n")

assert 1 == hash(1), "hash 1"
assert -4594863902769663758 == hash('abc'), "hash 'abc'"
expected_value = -9223372036584854238
hash_none = hash(None)
if hash(None) == expected_value:
    print("None Hashes")
else:  # https://bugs.python.org/issue19224
    print(f"FAILS - Hash(None) {hash_none} is not repeatable - {hash(None)}, {hash(None)}")
    print(f"... {hash(None)}")

"""
    values do differ with/without None: 
         2009162113655571948 without None, else 
        -4254551246225705588 with    None

    BUT, the values are not repeatable over runs, so server would not compute same value on retrieval then update??
        This appears to be a showstopper for checksum

    Aha, hash is based on a random seed, with you can override with env variable (see run config)
        Hash results are then repeatable
            EXCEPT in presence of None (??)
"""
