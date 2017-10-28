import postgresql
import flask
import json
from flask import request

app = flask.Flask(__name__)

# disables JSON pretty-printing in flask.jsonify
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


def db_conn():
    return postgresql.open('pq://login:password@localhost:5432/database_single')


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


def affected_num_to_code(cnt):
    code = 200
    if cnt == 0:
        code = 404
    return code


# e.g. failed to parse json
@app.errorhandler(400)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(404)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(405)
def page_not_found(e):
    return resp(405, {})


@app.route('/api-relay/v1.0/status', methods=['GET'])
def get_data():
    with db_conn() as db:
        extension = request.args.get('extension', type = int)
        callerid = request.args.get('callerid', type = str)
        callstatus = request.args.get('callstatus', type = int)
        if 5225 <= extension <= 5230:
            tuples = db.query("SELECT * FROM myphone_callhistory_v14 where dnowner='%s' AND party_name='%s' AND end_status=%s" % (extension, callerid, callstatus))
            status = []
            for (idmpch14, call_id, calltype, dnowner, party_dn, party_dntype, party_name, party_callerid, via_role, via_dn, via_dntype, via_dnname, via_callerid, start_time, established_time, end_time, end_status, end_status_hint, divert_dn, divert_dntype, divert_dnname, divert_callerid, dialed_number) in tuples:
                status.append({"id": idmpch14, "Extension": dnowner, "CallerID": party_callerid, "Call Status": end_status})
        else:
            status = []

        return resp(200, {"status": status})

if __name__ == '__main__':
    app.debug = True  # enables auto reload during development
    app.run(host='127.0.0.1', port=3333)
