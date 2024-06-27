from flask import Flask
import shares, bonds

app = Flask(__name__, instance_relative_config=False)

CONF = [shares.get_summary, bonds.get_summary]

@app.route("/load/<fund_code>")
def load(fund_code):
    for callback in CONF:
        load_summary(fund_code, callback)

    return 'Loaded'

def load_summary(fund_code, get_summary):
    get_summary(fund_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8282)
