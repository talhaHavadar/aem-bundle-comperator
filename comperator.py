"""
A Hollymolly module that handles the good stuff.
In the cases like you have one instance runs well but other is not then maybe you want to
compare the bundles of this two instance.

@author Talha Can Havadar (havadartalha@gmail.com)
"""
import argparse
import sys
import csv

import requests

def get_instance_tuple(response):
    """
    Gets the response and converts it to meaningful tuple for the sake of the program.
    """
    json = response.json()
    total_bundle_count = json['s'][0]
    active_bundle_count = json['s'][1]
    data = json['data']
    bundles = dict()
    for bundle in data:
        symbolic_name = bundle['symbolicName']
        bundles[symbolic_name] = {'symbolicName': symbolic_name, 'state': bundle['state'],
                                  'fragment': bundle['fragment'], 'version': bundle['version']}

    return (total_bundle_count, active_bundle_count, bundles)


def get_mismatched_bundles(base, other):
    """
    Compares the bundles of two instances and returns the differences as list of dictionary.
    """
    result = list()
    other_bundles = other[2]
    for key, value in base[2].items():
        if key in other_bundles:
            if not value == other_bundles[key]:
                result.append({"base": value, "other": other_bundles[key]})
        else:
            result.append({"base": value, "other": {'symbolicName': ""}})

    return result


def main(base, other, username_base, pw_base, username_other, pw_other):
    """
    Does the magic
    """
    base = f"http://{base}/system/console/bundles.json"
    other = f"http://{other}/system/console/bundles.json"

    response = requests.get(base, auth=(username_base, pw_base))
    instance1 = get_instance_tuple(response)
    response = requests.get(other, auth=(username_other, pw_other))
    instance2 = get_instance_tuple(response)

    print("Base Instance", instance1[0:2])
    print("Other Instance", instance2[0:2])

    result = get_mismatched_bundles(instance1, instance2)

    with open('report.csv', 'w+', newline='') as report:
        header_names = ["symbolicName", "state", "fragment", "version"]
        writer = csv.DictWriter(report, fieldnames=header_names)
        writer.writeheader()
        for res in result:
            res['base']['symbolicName'] = res['base']['symbolicName'] + ' (Base)'
            res['other']['symbolicName'] = res['other']['symbolicName'] + ' (Other)'
            writer.writerow(res['base'])
            writer.writerow(res['other'])

    print(result)
    print("Count:", len(result))

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description="A Comperation tool to list differences the bundles of two AEM instances")
    print("Args:", sys.argv)
    PARSER.add_argument("base", help="The base instance which runs smoothly without any issue")
    PARSER.add_argument("other", help="The base instance which runs smoothly without any issue")
    PARSER.add_argument("--username-base", default="admin",
                        help="The username for the base instance to authentication. Default: admin")
    PARSER.add_argument("--password-base", default="admin",
                        help="The password for the base instance to authentication. Default: admin")
    PARSER.add_argument("--username-other", default="admin",
                        help="The username for the other instance to authentication. Default: admin")
    PARSER.add_argument("--password-other", default="admin",
                        help="The password for the other instance to authentication. Default: admin")

    ARGS = PARSER.parse_args()

    main(ARGS.base, ARGS.other, ARGS.username_base, ARGS.password_base,
         ARGS.username_other, ARGS.password_other)
