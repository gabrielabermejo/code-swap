from flask import Flask, render_template, request, jsonify
import re

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
    """Converts basic Java code structure to equivalent Python.

    Args:
        input_code: The Java code string to be converted.

    Returns:
        The converted Python code string.
    """

    # Common replacements
    python_code = input_code.replace('System.out.println', 'print')
    python_code = python_code.replace('public void', 'def')
    python_code = python_code.replace('public class', 'class')
    python_code = python_code.replace('main(String[] args)', '__main__')

    # Formatting
    python_code = '\n'.join([line.strip() for line in python_code.splitlines()])  # Remove extra spaces
    lines = python_code.split('\n')
    formatted_lines = []
    indent_level = 0

    # Implementación para quitar todos los {}, } y ;
    for line in lines:
        stripped_line = line.strip()
        # Remover los '{', '}' y ';'
        if stripped_line.endswith('{'):
            stripped_line = stripped_line[:-1].strip()
        elif stripped_line.endswith('}'):
            stripped_line = stripped_line[:-1].strip()
            indent_level -= 1
        if stripped_line.endswith(';'):
            stripped_line = stripped_line[:-1].strip()
        if stripped_line:
            formatted_lines.append(' ' * (indent_level * 4) + stripped_line)
        if stripped_line.endswith(':'):
            indent_level += 1

    python_code = '\n'.join(formatted_lines)

    # Convert for loops
    def replace_for_loops(match):
        init_var, limit = match.groups()
        return f'for {init_var} in range({limit}):'

    python_code = re.sub(r'for \(int ([a-zA-Z_]\w*) = 0; \1 < (\d+); \1\+\+\)', replace_for_loops, python_code)

    for_pattern = re.compile(r'for \((.*); (.*); (.*)\)')

    def convert_for(match):
        initialization, condition, increment = match.groups()
        init_var, init_value = initialization.split('=')
        init_var = init_var.strip()
        init_value = init_value.strip()

        cond_var, cond_operator, cond_value = condition.strip().split()

        # Extract increment details
        if '++' in increment:
            increment_value = '1'
        elif '--' in increment:
            increment_value = '-1'
        else:
            increment_var, increment_value = increment.split('=')
            increment_value = increment_value.strip()

        # Attempt conversion to range-based for loop
        if (init_value == '0' and cond_operator == '<' and
                increment_value == '1' and init_var == cond_var):
            return f'for {init_var} in range({cond_value}):'
        else:
            # Construct range based on operators
            range_start = init_value
            range_end = cond_value
            if '<' in cond_operator:
                range_end = cond_value
            elif '<=' in cond_operator:
                range_end = str(int(cond_value) + 1)
            elif '>' in cond_operator:
                range_start, range_end = cond_value, str(int(init_value) - 1)
            elif '>=' in cond_operator:
                range_start, range_end = cond_value, init_value

            return f'for {init_var} in range({range_start}, {range_end}, {increment_value}):'

    python_code = for_pattern.sub(convert_for, python_code)

    # Convert while loop (basic replacement)
    python_code = python_code.replace('while (', 'while ')

    # Remove variable type declarations
    python_code = re.sub(r'\b(int|float|double|String)\b ', '', python_code)

    # Convert increments and decrements
    python_code = re.sub(r'(\w+)\+\+', r'\1 += 1', python_code)
    python_code = re.sub(r'(\w+)\-\-', r'\1 -= 1', python_code)

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
