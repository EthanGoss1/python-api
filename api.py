from flask import Flask, request, Response
from flask_cors import CORS
import tempfile
import os
import subprocess
import json


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return '<h1>Flask Grader API</h1>'

@app.route('/grade', methods=['POST', "GET"])
def grade():
    # raw_text = request.data.decode('utf-8')

    if 'cppfile' not in request.files:
        return Response('Missing .cpp file', status=400, mimetype='text/plain')

    cpp_file = request.files['cppfile']
    # input_file = request.files['txtfile']
    response_obj = {}

    with tempfile.TemporaryDirectory() as tempdir:
        cpp_path = os.path.join(tempdir, 'program.cpp')
        exe_path = os.path.join(tempdir, 'program.exe')
        input_path = os.path.join(tempdir, 'input.txt')

        # input_file.save(input_path)
        cpp_file.save(cpp_path)

        compile_process = subprocess.run(['g++', cpp_path, '-o', exe_path], capture_output=True, text=True)
        if compile_process.returncode != 0:
            return Response(f'Compilation failed: {compile_process.stderr}', status=400, mimetype='text/plain')

        run_process = subprocess.run([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if run_process.returncode != 0:
            return Response(f'Execution failed: {run_process.stderr}', status=400, mimetype='text/plain')

        output = run_process.stdout
        # with open(input_path, 'r') as f:
        #     input_content = f.read()

        #     response_obj = {
        #         "out": output,
        #         "in":  input_content
        #     }

        response_obj = {
            "out": output
        }
    return Response(json.dumps(response_obj), mimetype='application/json')

    # return f'<h2>Grading...</h2><br/><p></p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6589, debug=True)