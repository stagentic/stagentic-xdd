def values_passed_to(spy, name):
    return [call.kwargs[name] for call in spy.call_args_list]


def value_passed_to(spy, name):
    return values_passed_to(spy, name)[-1]
