from flask import Flask, jsonify, request
from executor import CommandExecutor

app = Flask(__name__)
executor = CommandExecutor()

@app.route('/commands', methods=['GET'])
def list_commands():
    return jsonify(list(executor.commands.keys()))

@app.route('/execute', methods=['POST'])
def execute_command():
    command_name = request.json.get('command')
    try:
        executor.execute_now(command_name)
        return jsonify({"result": f"Command '{command_name}' executed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/schedule', methods=['GET'])
def get_schedule():
    return jsonify(executor.schedule)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    executor.stop()
    return jsonify({"result": "Executor stopped"})

if __name__ == '__main__':
    app.run(debug=True)
