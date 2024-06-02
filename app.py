from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def python_to_java(input_code):
    # Reemplazar la definición de funciones
    java_code = input_code.replace('def ', 'public static void ').replace('():', '() {')
    # Reemplazar print() por System.out.println()
    java_code = java_code.replace('print(', 'System.out.println(')
    # Reemplazar input() por Scanner
    java_code = java_code.replace('int(input())', 'new Scanner(System.in).nextInt()')
    java_code = java_code.replace('float(input())', 'new Scanner(System.in).nextFloat()')
    java_code = java_code.replace('str(input())', 'new Scanner(System.in).nextLine()')
    java_code = java_code.replace('#', '//')
    java_code = java_code.replace('for key, value in my_dict.items():', 'for (Map.Entry<String, Object> entry : myDict.entrySet()) { String key = entry.getKey(); Object value = entry.getValue();')

    # Reemplazar la indentación
    lines = java_code.split('\n')
    java_code = ''
    indent = 0
    for line in lines:
        if line.strip():
            if line.startswith('    '):
                indent += 1
                line = line[4:]
            elif indent > 0:
                indent -= 1
            java_code += '    ' * indent + line + '\n'
    # Agregar punto y coma al final de las líneas
    java_code = java_code.replace('\n', ';\n')
    return java_code




def java_to_python(input_code):
    # Reemplaza las llaves en Java por indentación en Python
    python_code = input_code.replace('{', '').replace(';', '\n').replace('public void', 'def').replace('(', '():').replace(' {', ':')
    return python_code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    input_code = data['code']
    direction = data['direction']
    
    if direction == 'py-to-java':
        converted_code = python_to_java(input_code)
    elif direction == 'java-to-py':
        converted_code = java_to_python(input_code)
    else:
        return jsonify({'error': 'Invalid conversion direction'})
    
    return jsonify({'converted_code': converted_code})

if __name__ == '__main__':
    app.run(debug=True)
