from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)


def python_to_java(input_code):
    # Reemplazar definiciones de funciones
    java_code = re.sub(r'def ([\w\d_]+)\(([^)]*)\):', r'public static void \1(\2) {', input_code)

    # Reemplazar print() con System.out.println()
    java_code = re.sub(r'print\(([^)]*)\)', r'System.out.println(\1)', java_code)

    # Reemplazar input() con Scanner
    java_code = re.sub(r'(\w+) = int\(input\(([^)]*)\)\)', r'Scanner scanner = new Scanner(System.in);\nint \1 = scanner.nextInt()', java_code)
    java_code = re.sub(r'(\w+) = float\(input\(([^)]*)\)\)', r'Scanner scanner = new Scanner(System.in);\nfloat \1 = scanner.nextFloat()', java_code)
    java_code = re.sub(r'(\w+) = str\(input\(([^)]*)\)\)', r'Scanner scanner = new Scanner(System.in);\nString \1 = scanner.nextLine()', java_code)

    # Convertir comentarios
    java_code = java_code.replace('#', '//')

    # Convertir elif a else if
    java_code = java_code.replace('elif', 'else if')

    # Reemplazar listas de Python por arrays de Java
    list_pattern = re.compile(r'(\w+)\s*=\s*\[([^\]]*)\]')
    matches = list_pattern.findall(input_code)
    for match in matches:
        list_name = match[0]
        list_items = match[1].split(',')
        list_items = [item.strip() for item in list_items]
        java_array_declaration = f'int[] {list_name} = new int[]{{{", ".join(list_items)}}};'
        # Reemplazar la línea anterior con la nueva declaración del array
        java_code = re.sub(rf'{list_name} = \[([^\]]*)\]', java_array_declaration, java_code)

    # Reemplazar variables y tipos
    variable_pattern = re.compile(r'(\w+)\s*=\s*(.+)')
    variables = variable_pattern.findall(input_code)
    for var_name, value in variables:
        if re.match(r'^\d+$', value):
            java_code = re.sub(rf'{var_name}\s*=\s*{value}', f'int {var_name} = {value}', java_code)
        elif re.match(r'^\d+\.\d+$', value):
            java_code = re.sub(rf'{var_name}\s*=\s*{value}', f'float {var_name} = {value}', java_code)
        elif re.match(r'^(True|False)$', value):
            java_code = re.sub(rf'{var_name}\s*=\s*{value}', f'boolean {var_name} = {value.lower()}', java_code)
        elif re.match(r'^"."$', value) or re.match(r"^'.'$", value):
            java_code = re.sub(rf'{var_name}\s*=\s*{value}', f'String {var_name} = {value}', java_code)
        elif re.match(r'^\[.*\]$', value):
            # Listas ya manejadas previamente
            continue
        else:
            # Asumir que es un String por defecto
            java_code = re.sub(rf'{var_name}\s*=\s*{value}', f'String {var_name} = {value}', java_code)

    # Reemplazar la indentación y ajustar bloques de control
    lines = java_code.split('\n')
    java_code = ''
    indent = 0
    indent_stack = []

    for line in lines:
        stripped_line = line.strip()
        current_indent = (len(line) - len(stripped_line)) // 4

        if stripped_line.startswith('while ') or stripped_line.startswith('if '):
            line = line.replace('while ', 'while (').replace('if ', 'if (').replace(' or ', ' || ').replace(' and ', ' && ').replace(' not ', ' ! ').rstrip() + ') {'
            indent_stack.append(indent)
            indent += 1

        elif stripped_line.startswith('for '):
            range_match = re.search(r'for (\w+) in range\(([^,]+), ([^,]+)\):', stripped_line)
            if range_match:
                var_name, start, end = range_match.groups()
                line = f'for (int {var_name} = {start}; {var_name} < {end}; {var_name}++) {{'
            else:
                range_match = re.search(r'for (\w+) in range\(([^,]+), ([^,]+), ([^,]+)\):', stripped_line)
                if range_match:
                    var_name, start, end, step = range_match.groups()
                    line = f'for (int {var_name} = {start}; {var_name} < {end}; {var_name} += {step}) {{'
                else:
                    range_match = re.search(r'for (\w+) in range\(([^,]+)\):', stripped_line)
                    if range_match:
                        var_name, end = range_match.groups()
                        line = f'for (int {var_name} = 0; {var_name} < {end}; {var_name}++) {{'
                    else:
                        # Manejar casos especiales como el rango de raíz cuadrada
                        range_match = re.search(r'for (\w+) in range\(2, int\(([^)]+)\*0\.5\) \+ 1\):', stripped_line)
                        if range_match:
                            var_name, expr = range_match.groups()
                            line = f'for (int {var_name} = 2; {var_name} <= Math.sqrt({expr}); {var_name}++) {{'
                        else:
                            # Manejar casos de listas
                            list_match = re.search(r'for (\w+) in (\w+):', stripped_line)
                            if list_match:
                                var_name, list_name = list_match.groups()
                                line = f'for (int {var_name} : {list_name}) {{'
            indent_stack.append(indent)
            indent += 1

        elif stripped_line.startswith('else'):
            line = '} else {'

        elif stripped_line == '':
            continue

        if ' += 1' in stripped_line:
            line = line.replace(' += 1', '++')
        if ' -= 1' in stripped_line:
            line = line.replace(' -= 1', '--')

        if stripped_line and not stripped_line.endswith(':') and not stripped_line.endswith('{') and not stripped_line.endswith('}') and not stripped_line.startswith('//'):
            line = line.rstrip() + ';'

        java_code += '    ' * indent + line + '\n'

        while indent_stack and current_indent < indent_stack[-1]:
            indent = indent_stack.pop()
            java_code += '    ' * indent + '}\n'

    while indent_stack:
        indent = indent_stack.pop()
        java_code += '    ' * indent + '}\n'

    return java_code


def java_to_python(input_code):
    # Basic replacements
    replacements = {
        'System.out.println': 'print',
        ' public static void main(String[] args)':' ',
        ' Scanner scanner = new Scanner(System.in)':' ',
        'public static': 'def',
        'System.out.print': 'print',
        'public void': 'def',
        'public class': 'class',
        'main(String[] args)': 'main',
        '//': '#',
        'int[]':' ',
        'double[]':' ',
        'float[]':' ',
        'string[]':' '
        
    }
    
    for java_syntax, python_syntax in replacements.items():
        input_code = input_code.replace(java_syntax, python_syntax)
    
    # Remove extra spaces and handle indentation
    lines = input_code.splitlines()
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped_line = line.strip()
        # Remove braces
        stripped_line = stripped_line.replace('{', '').replace('}', '')
        if stripped_line.endswith(';'):
            stripped_line = stripped_line[:-1].strip()
        if stripped_line:
            formatted_lines.append(' ' * (indent_level * 4) + stripped_line)
        if stripped_line.endswith(':'):
            indent_level += 1
    
    python_code = '\n'.join(formatted_lines)
    
    # Convert traditional for loops
    for_pattern = re.compile(r'for\s*\((int\s+)?(\w+)\s*=\s*(\d+);(\s*\2\s*[<=>!]+\s*\d+);(\s*\2\s*\+\+|--|[\+\-\*/]=\s*\d+)\)')
    
    def convert_for(match):
        init_var = match.group(2).strip()
        init_value = match.group(3).strip()
        condition = match.group(4).strip()
        increment = match.group(5).strip()

        cond_var, cond_operator, cond_value = re.split(r'([<=>!]+)', condition)
        cond_var = cond_var.strip()
        cond_operator = cond_operator.strip()
        cond_value = cond_value.strip()

        if '++' in increment or '+= 1' in increment:
            increment_value = '1'
        elif '--' in increment or '-= 1' in increment:
            increment_value = '-1'
        else:
            increment_value = re.split(r'[\+\-\*/]=', increment)[1].strip()

        if cond_operator == '<':
            range_end = cond_value
        elif cond_operator == '<=':
            range_end = str(int(cond_value) + 1)
        elif cond_operator == '>':
            range_start, range_end = cond_value, str(int(init_value) - 1)
        elif cond_operator == '>=':
            range_start, range_end = cond_value, init_value

        return f'for {init_var} in range({init_value}, {range_end}):'
    
    python_code = for_pattern.sub(convert_for, python_code)
    
    # Convert enhanced for loops
    enhanced_for_pattern = re.compile(r'for\s*\(\s*(int|float|double|String|boolean)?\s*(\w+)\s*:\s*(\w+)\s*\)')
    
    def convert_enhanced_for(match):
        var_type = match.group(1)
        var_name = match.group(2).strip()
        collection = match.group(3).strip()
        return f'for {var_name} in {collection}:'
    
    python_code = enhanced_for_pattern.sub(convert_enhanced_for, python_code)
    
    # Convert while loops
    python_code = re.sub(r'while\s*\(([^)]+)\)', r'while \1:', python_code)
    
    # Convert do-while loops
    def convert_do_while(match):
        body, condition = match.groups()
        body_lines = body.strip().split('\n')
        formatted_body = '\n    '.join(line.strip() for line in body_lines)
        return f'while True:\n    {formatted_body}\n    if not ({condition}):\n        break'
    
    python_code = re.sub(r'do \{([^}]*)\} while \(([^)]+)\);', convert_do_while, python_code, flags=re.DOTALL)

    # Convert if statements
    python_code = re.sub(r'if\s*\(([^)]+)\)', r'if \1:', python_code)
    python_code = re.sub(r'else if\s*\(([^)]+)\)', r'elif \1:', python_code)
    python_code = python_code.replace('else', 'else:')
    
    # Remove variable types
    python_code = re.sub(r'\b(int|float|double|String|boolean)\b ', '', python_code)
    
    # Convert increments and decrements
    python_code = re.sub(r'(\w+)\+\+', r'\1 += 1', python_code)
    python_code = re.sub(r'(\w+)\-\-', r'\1 -= 1', python_code)
    
    # Convert logical operators
    python_code = python_code.replace('&&', 'and')
    python_code = python_code.replace('||', 'or')
    python_code = python_code.replace('!', 'not ')
    
    # Convert input statements
    formatted_lines = python_code.split('\n')
    for i, line in enumerate(formatted_lines):
        if 'scanner.nextInt' in line:
            parts = line.split('=')
            var_name = parts[0].split()[-1]
            formatted_lines[i] = f'{var_name.strip()} = int(input())'
        elif 'scanner.nextDouble' in line:
            parts = line.split('=')
            var_name = parts[0].split()[-1]
            formatted_lines[i] = f'{var_name.strip()} = float(input())'
        elif 'scanner.nextLine' in line:
            parts = line.split('=')
            var_name = parts[0].split()[-1]
            formatted_lines[i] = f'{var_name.strip()} = input()'
        elif 'scanner.nextBoolean' in line:
            parts = line.split('=')
            var_name = parts[0].split()[-1]
            prompt = parts[-1].split('(')[-1].split(')')[0].strip('"')
            formatted_lines[i] = f'{var_name.strip()} = bool(input("{prompt}: "))'
    
    python_code = '\n'.join(formatted_lines)
    
    # Convert array declarations
    array_pattern = re.compile(r'\bint\[\]\s+(\w+)\s*=\s*\{([^\}]+)\};')
    
    def convert_array(match):
        var_name = match.group(1).strip()
        elements = match.group(2).strip()
        return f'{var_name} = [ {elements} ] '
    
    python_code = array_pattern.sub(convert_array, python_code)
    
    # Ensure function declarations end with a colon
    python_code = re.sub(r'(def\s+\w+\(.*?\))', r'\1:', python_code)
    
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
