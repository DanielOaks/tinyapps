#!/usr/bin/env python3
# TinyApps - Jinja2 Filters and Utilities
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the BSD 2-clause license


# filters
def metric(original, metric_list=[[10 ** 9, 'B'], [10 ** 6, 'M'], [10 ** 3, 'k']]):
    """Returns user-readable string representing given value.

    Arguments:
    num is the base value we're converting.
    metric_list is the list of data we're working off.
    additive is whether we add the various values together, or separate them.

    Return:
    a string such as 345K or 24.4B"""
    num = int(original)

    output = ''
    for metric_count, metric_char in metric_list:
        if num > metric_count:
            format_str = '{:.1f}{}'

            num = (float(num) / metric_count)
            output += format_str.format(num, metric_char)

            return output

    return str(num)


# applying it all
def apply_filters(env):
    """Apply our filters to the given Jinja2 environment."""
    env.filters['metric'] = metric
