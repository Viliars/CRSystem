import itertools

BATCH_SIZE = 500
API_CALLS = 19

def resp_to_id_type_members(batches, calls_resp):
    group_types = calls_resp[::4]
    group_closes = calls_resp[1::4]
    group_deacts = calls_resp[2::4]
    group_members = calls_resp[3::4]
    for inner_call, \
        inner_types, \
        inner_members, \
        inner_closes, \
        inner_deacts \
    in zip(batches, group_types, group_members, group_closes, group_deacts):
        for group_id, \
            group_type, \
            group_size, \
            group_closed, \
            group_deact \
        in zip(inner_call, inner_types, inner_members, inner_closes, inner_deacts):
            num_group_type = 10
            if group_deact == "banned":
                num_group_type = 5
            elif group_deact == "deleted":
                num_group_type = 6
            elif group_type == "group" and group_closed == 0:
                num_group_type = 1
            elif group_type == "group" and group_closed == 1:
                num_group_type = 4
            elif group_type == "page":
                num_group_type = 2
            elif group_type == "event":
                num_group_type = 3
            yield (group_id, num_group_type, group_size)

def get_apicall_line(vars_num, group_ids):
    pat = """
var a{0} = API.groups.getById({{"group_ids":[{1}],"fields":"members_count, is_closed, deactivated"}});
var t{0} = a{0}@.type;
var c{0} = a{0}@.is_closed;
var d{0} = a{0}@.deactivated;
var m{0} = a{0}@.members_count;
""".replace("\n", "")

    return pat.format(vars_num, ",".join((str(x) for x in group_ids)))

def gen_vkscript(call_params):
    pat = """
{0}
return [{1}];
""".replace("\n", "")
    vkscript_apicalls = []
    vkscript_vars = []
    for i, inner_call_groups in enumerate(call_params):
        apicall = get_apicall_line(i, inner_call_groups)
        vkscript_apicalls.append(apicall)
        vkscript_vars.append("t{}".format(i))
        vkscript_vars.append("c{}".format(i))
        vkscript_vars.append("d{}".format(i))
        vkscript_vars.append("m{}".format(i))

    return pat.format("".join(vkscript_apicalls), ",".join(vkscript_vars))

def get_n_batches(n, batch_size, it):
    batches = []
    generating = True
    while generating:
        one_batch = list(itertools.islice(it, batch_size))
        if len(one_batch) > 0:
            batches.append(one_batch)
            n -= 1
            generating = n > 0
        else:
            generating = False

    return batches

def gen_vkcall(groups_it):
    batches = get_n_batches(API_CALLS, BATCH_SIZE, groups_it)
    while len(batches) > 0:
        vkscript = gen_vkscript(batches)
        yield (batches, vkscript)
        batches = get_n_batches(API_CALLS, BATCH_SIZE, groups_it)
