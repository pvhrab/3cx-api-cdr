import postgresql
import flask
import json
import datetime
from flask import request

app = flask.Flask(__name__)

# disables JSON pretty-printing in flask.jsonify
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


def db_conn():
    return postgresql.open('pq://login:pass@localhost:5432/database_single')


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


@app.route('/api-relay/v1.0/missedcalls', methods=['GET'])
def get_data():
    with db_conn() as db:
        extension = request.args.get('ext', type = int)
        turgetday = request.args.get('date', type = str)
        if 5221 <= extension <= 5235:
            tuples = db.query("SELECT call_id,dnowner,party_callerid,start_time,end_time,end_status FROM myphone_callhistory_v14 where dnowner='%s' AND DATE(end_time)='%%%s%%' AND end_status='5'" % (extension, turgetday))
            status = []
            for (call_id, dnowner, party_callerid, start_time, end_time, end_status) in tuples:
                status.append ({"id": call_id, "Extension": dnowner, "CallerID": party_callerid, "StartTime": str(start_time), "EndTime": str(end_time), "Call Status": end_status})
        else:
            status = []

        return resp(200, {"status": status})

@app.route('/api-relay/v1.0/calls/outgoing', methods=['GET'])
def get_data2():
    with db_conn() as db:
        extension = request.args.get('ext', type = int)
        turgetday = request.args.get('date', type = str)
        if 5221 <= extension <= 5235:
            tuples = db.query("select call_id,seg_id,seg_type,seg_order,start_time,end_time,src_dn_type,src_dn,src_display_name,src_firstlastname,dst_start_time,dst_answer_time,dst_end_time,dst_dn,dst_display_name,dst_firstlastname,dst_caller_number,src_recording_url from cdr_status where src_dn='%s' AND DATE(end_time)='%%%s%%' AND dst_answer_time IS NOT NULL" % (extension, turgetday))
            status = []
            for (call_id, seg_id, seg_type, seg_order, start_time, end_time, src_dn_type, src_dn, src_display_name, src_firstlastname, dst_start_time, dst_answer_time, dst_end_time, dst_dn, dst_display_name, dst_firstlastname, dst_caller_number, src_recording_url) in tuples:
                status.append ({"ID": call_id, "EXT": src_dn, "EXT Name": src_display_name, "CID_dn": dst_dn, "CID_id": dst_display_name , "Start": str(dst_start_time), "Answer": str(dst_answer_time), "EndTime": str(dst_end_time), "Recording": src_recording_url})
        else:
            status = []

        return resp(200, {"status": status})

@app.route('/api-relay/v1.0/calls/incoming', methods=['GET'])
def get_data3():
    with db_conn() as db:
        extension = request.args.get('ext', type = int)
        turgetday = request.args.get('date', type = str)
        if 5220 <= extension <= 5235:
            tuples = db.query("select call_id,seg_id,seg_type,seg_order,start_time,end_time,src_dn_type,src_dn,src_display_name,src_firstlastname,dst_start_time,dst_answer_time,dst_end_time,dst_dn,dst_display_name,dst_firstlastname,dst_caller_number,dst_recording_url from cdr_status where dst_dn='%s' AND DATE(end_time)='%%%s%%' AND dst_answer_time IS NOT NULL" % (extension, turgetday))
            status = []
            for (call_id, seg_id, seg_type, seg_order, start_time, end_time, src_dn_type, src_dn, src_display_name, src_firstlastname, dst_start_time, dst_answer_time, dst_end_time, dst_dn, dst_display_name, dst_firstlastname, dst_caller_number, dst_recording_url) in tuples:
                status.append ({"ID": call_id, "EXT": dst_dn, "EXT Name": dst_display_name, "CID_dn": src_dn, "CID_id": src_display_name , "Start": str(dst_start_time), "Answer": str(dst_answer_time), "EndTime": str(dst_end_time), "Recording": dst_recording_url})
        else:
            status = []

        return resp(200, {"status": status})

@app.route('/api-relay/v1.0/calls', methods=['GET'])
def get_data4():
    with db_conn() as db:
        extension = request.args.get('ext', type = int)
        turgetday = request.args.get('date', type = str)
        if 5221 <= extension <= 5235:
            tuples = db.query("select * from cdr_status where src_dn='%s' or dst_dn='%s' AND DATE(end_time)='%%%s%%'" % (extension, extension, turgetday))
            status = []
            for (call_id, seg_id, seg_type, seg_order, start_time, end_time, src_dn_type, src_dn, src_display_name, src_firstlastname, src_recording_url, dst_start_time, dst_answer_time, dst_end_time, dst_recording_url, dst_billing_rate, dst_dn_type, dst_dn, dst_display_name, dst_firstlastname, dst_caller_number, dst_dn_class, act, act_dn_type, act_dn, act_display_name, act_firstlastname) in tuples:
                status.append ({"call_id": call_id, "seg_id": seg_id, "seg_type": seg_type, "seg_order": seg_order, "start_time": str(start_time), "end_time": str(end_time), "src_dn": src_dn, "src_display_name": src_display_name, "src_firstlastname": src_firstlastname, "src_recording_url": src_recording_url, "dst_start_time": str(dst_start_time), "dst_answer_time": str(dst_answer_time), "dst_end_time": str(dst_end_time), "dst_recording_url": dst_recording_url, "dst_billing_rate": dst_billing_rate, "dst_dn_type": dst_dn_type, "dst_dn": dst_dn, "dst_display_name": dst_display_name, "dst_firstlastname": dst_firstlastname, "dst_caller_number": dst_caller_number, "dst_dn_class": dst_dn_class, "act": act, "act_dn_type": act_dn_type, "act_dn": act_dn, "act_display_name": act_display_name, "act_firstlastname": act_firstlastname})
        else:
            status = []

        return resp(200, {"status": status})

if __name__ == '__main__':
    app.debug = True  # enables auto reload during development
    app.run(host='127.0.0.1', port=3333)
