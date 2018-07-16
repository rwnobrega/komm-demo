import dash
import re

app = dash.Dash()
server = app.server
app.config.suppress_callback_exceptions = True

def uid_gen(sub_app_name):
    return lambda id_: '{}_{}'.format(sub_app_name.replace('.', '-').replace('_', '-'), id_)

def explode_dict(dict_in):  # Meh.
    if dict_in is None:
        return {}

    dict_out = {}
    for key, value in dict_in.items():
        if isinstance(key, str):
            regex_result = re.match(r'(\w*)\[([0-9]*)\]', key, re.IGNORECASE)
        else:
            regex_result = None
        if isinstance(key, str) and '.' in key:
            new_key, new_value = key.split('.', maxsplit=1)
            if new_key in dict_out:
                dict_out[new_key][new_value] = value
            else:
                dict_out[new_key] = {new_value: value}
        elif regex_result:
            new_key, index = regex_result[1], regex_result[2]
            if new_key in dict_out:
                dict_out[new_key][int(index)] = value
            else:
                dict_out[new_key] = {int(index): value}
        else:
            dict_out[key] = value

    for key, value in dict_out.items():
        if isinstance(value, dict):
            if 0 in value:
                dict_out[key] = [value[k] for k in sorted(value.keys())]
            else:
                dict_out[key] = explode_dict(value)

    return dict_out
