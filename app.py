import dash
import re

app = dash.Dash()
server = app.server
app.config.suppress_callback_exceptions = True

def uid_gen(sub_app_name):
    return lambda id_: '{}_{}'.format(sub_app_name.replace('.', '-').replace('_', '-'), id_)
