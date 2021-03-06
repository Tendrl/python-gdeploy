from python_gdeploy.wrapper import gdeploy_features as gf
from python_gdeploy.wrapper.gdeploy_wrapper import cook_gdeploy_config
from python_gdeploy.wrapper.gdeploy_wrapper import invoke_gdeploy


def create_volume(volume_name, brick_details, transport=None,
                  replica_count=None, disperse_count=None,
                  redundancy_count=None, tuned_profile=None,
                  force=False):
    """Brick details should be of following form, its a list of list

    where each sublist is a collection of bricks which forms a replica

    set(in case of replicated volume) or a subvolume(in case of a

    distributed dispersed volume)

    [

        [

         {"hostname1": "brick1"},

         {"hostname2": "brick1"},

         {"hostname3": "brick1"},

         {"hostname4": "brick1"}

        ],

        [

         {"hostname1": "brick2"},

         {"hostname2": "brick2"},

         {"hostname3": "brick2"},

         {"hostname4": "brick2"}

        ],

        [

         {"hostname1": "brick3"},

         {"hostname2": "brick3"},

         {"hostname4": "brick3"},

         {"hostname3": "brick3"}

        ],

    ]

    """

    recipe = []
    brick_list = []
    host_list = set()
    if replica_count:
        if len(brick_details[0]) != int(replica_count):
            out = "insufficient brick sets for replica count" + \
                  ": %s. Brick set count %s" % (
                      replica_count, len(brick_details[0])
                  )
            err = out
            rc = 1
            return out, err, rc

    if disperse_count and redundancy_count:
        if len(brick_details[0]) != (
                int(disperse_count) + int(redundancy_count)):
            out = "insufficient nos bricks for disperse count" + \
                  ": %s and redundancy count: %s. Brick count: %s" % (
                      disperse_count,
                      redundancy_count,
                      len(brick_details[0])
                  )
            err = out
            rc = 1
            return out, err, rc

    set_length = len(brick_details[0])
    for replica_set in brick_details:
        if len(replica_set) != set_length:
            out = "number of bricks in different sets are not same" + \
                  "Bricks passed: %s" % (
                      str(brick_details)
                  )
            err = out
            rc = 1
            return out, err, rc

        for el in replica_set:
            host_list.add(el.keys()[0])
            brick_list.append(el.keys()[0] + ":" + el.values()[0])
    recipe.append(gf.get_hosts(list(host_list)))

    arg_dict = {}
    force = "yes" if force else "no"
    arg_dict.update({"force": force})
    args = [volume_name, "create", brick_list]

    if transport:
        arg_dict.update({"transport": transport})
    if replica_count:
        arg_dict.update({"replica_count": replica_count})
    if disperse_count and redundancy_count:
        arg_dict.update({"disperse_count": disperse_count,
                         "redundancy_count": redundancy_count,
                         "disperse": "yes"})

    recipe.append(
        gf.get_volume(*args, **arg_dict)
    )

    if tuned_profile:
        recipe.append(
            gf.get_tuned_profile(tuned_profile)
        )

    config_str = cook_gdeploy_config(recipe)

    out, err, rc = invoke_gdeploy(config_str)

    return out, err, rc
