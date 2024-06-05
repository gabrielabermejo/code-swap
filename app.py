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

    # Reemplazar comentarios
    java_code = java_code.replace('#', '//')

    # Convertir condicionales
    java_code = java_code.replace('elif', 'else if')

    # Reemplazar la indentación
    lines = java_code.split('\n')
    java_code = ''
    indent = 0
    if_open = False
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            # Manejar la indentación
            if line.startswith('    '):
                line = line[4:]
                indent += 1
            elif indent > 0:
                indent -= 1
            
            # Convertir condicionales y ciclos
            if stripped_line.startswith('if ') or stripped_line.startswith('else if ') or stripped_line.startswith('else:'):
                if if_open:
                    java_code += '    ' * (indent - 1) + '}\n'
                    if_open = False
                if ':' in line:
                    condition = line.split(':')[0].strip()
                    if 'else' in condition:
                        line = line.replace(condition + ':', '{} {{'.format(condition))
                    else:
                        line = line.replace(condition + ':', '{} ({}) {{'.format(condition.split(' ')[0], condition.split(' ', 1)[1]))
                if_open = True
            elif stripped_line.startswith('for ') or stripped_line.startswith('while '):
                if ':' in line:
                    condition = line.split(':')[0].strip()
                    if stripped_line.startswith('for '):
                        # Convertir range() en bucle for en Java
                        parts = condition.split(' ')
                        var = parts[1]
                        range_values = condition.split('range(')[1].split(')')[0]
                        if ',' in range_values:
                            start, end = range_values.split(',')
                            line = 'for (int {} = {}; {} < {}; {}++) {{'.format(var, start.strip(), var, end.strip(), var)
                        else:
                            end = range_values
                            line = 'for (int {} = 0; {} < {}; {}++) {{'.format(var, var, end.strip(), var)
                    else:
                        line = line.replace(condition + ':', '({}) {{'.format(condition.split(' ', 1)[1]))
            
            java_code += '    ' * indent + line + '\n'
    
    # Agregar punto y coma al final de las líneas que lo necesiten
    lines = java_code.split('\n')
    java_code = ''
    for line in lines:
        stripped_line = line.strip()
        if stripped_line and not stripped_line.endswith('{') and not stripped_line.endswith('}') and not stripped_line.startswith('//'):
            line += ';'
        java_code += line + '\n'
    
    return java_code

def java_to_python(input_code):
    # Reemplaza las llaves en Java y puntos y comas
    python_code = input_code.replace(';', '').replace('{', '').replace('}', '')
    
    # Reemplaza los 'System.out.println' con 'print'
    python_code = python_code.replace('System.out.println', 'print')
    
    # Reemplaza las funciones public void con def en Python
    python_code = python_code.replace('public void', 'def')
    
    # Elimina la línea que contiene 'public void main(String[] args) {'
    lines = python_code.split('\n')
    formatted_lines = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('def main(String[] args)'):
            continue  # Salta esta línea
        if stripped_line.startswith('def'):
            line = line.replace('(', '():').replace(' {', ':')
        formatted_lines.append(line)
    
    # Combina las líneas nuevamente
    python_code = '\n'.join(formatted_lines)
    
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

