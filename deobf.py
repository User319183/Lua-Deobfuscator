import re
import base64
import urllib.parse
import binascii
import codecs
from colorama import Fore, Style


def prettify_lua(code):
    # Add a newline before each "do", "end", "if", "else", "for", and "while"
    code = re.sub(r'(\s)(do|end|if|else|for|while)(\s)', r'\1\n\2\3', code)

    # Add a newline after each "end"
    code = re.sub(r'(end)(\s)', r'\1\n\2', code)

    # Indent each line inside a "do ... end" or "if ... end" block
    lines = code.split('\n')
    indent_level = 0
    for i in range(len(lines)):
        if 'end' in lines[i]:
            indent_level -= 1
        lines[i] = '    ' * indent_level + lines[i].strip()
        if 'do' in lines[i] or 'if' in lines[i]:
            indent_level += 1

    return '\n'.join(lines)


def reverse_obfuscation(input_string):
    # Base64 encoding
    try:
        encoded_string = base64.b64encode(input_string.encode('utf-8')).decode('utf-8')
        return encoded_string
    except:
        pass

    # URL encoding
    try:
        encoded_string = urllib.parse.quote(input_string)
        return encoded_string
    except:
        pass

    # Hex encoding
    try:
        encoded_string = binascii.hexlify(input_string.encode('utf-8')).decode('utf-8')
        return encoded_string
    except:
        pass

    # character escaping encoding
    try:
        encoded_string = ''.join([f'\\x{char.encode("utf-8").hex()}' for char in input_string])
        return encoded_string
    except:
        pass

    # binary string encoding
    try:
        encoded_string = ''.join([f'{ord(char):02x}' for char in input_string])
        return encoded_string
    except:
        pass

    try:
        encoded_string = codecs.encode(input_string, 'rot_13')
        return encoded_string
    except:
        pass

    # If all else fails, return the original string
    return input_string


def deobfuscate_custom(code):
    # Search for M.b, M.f, and M.t function calls
    function_calls = re.findall(r'M\.[bft]\((.*?)\)', code)
    for string in function_calls:
        deobfuscated_string = reverse_obfuscation(string)
        code = code.replace(string, deobfuscated_string)
    return code

def remove_dead_code(code):
    # Remove unused variables
    used_vars = set(re.findall(r'\bvar\d+\b', code))
    assignments = re.findall(r'\bvar\d+\b = .+', code)
    for assignment in assignments:
        var = assignment.split(' = ')[0]
        if var not in used_vars:
            code = code.replace(assignment, '')

    # Remove useless loops
    loops = re.findall(r'for .+ do\n\t.+\nend', code)
    for loop in loops:
        code = code.replace(loop, '')

    return code


def simplify_expressions(code):
    # Simplify constant calculations
    constant_calculations = re.findall(r'(\d+\.\d+) / (\d+\.\d+) \+ (\d+\.\d+)', code)
    for calculation in constant_calculations:
        num1, num2, num3 = map(float, calculation)
        simplified_value = num1 / num2 + num3
        code = code.replace(f'{num1} / {num2} + {num3}', str(simplified_value))

    # Simplify arithmetic operations
    arithmetic_operations = re.findall(r'(\bvar\d+\b) = (\bvar\d+\b) (.) (\bvar\d+\b)', code)
    for operation in arithmetic_operations:
        var, var1, operator, var2 = operation
        # Check if the operation always results in the same value
        if operator == '+' and var1 == var2:
            code = code.replace(f'{var} = {var1} {operator} {var2}', f'{var} = 2 * {var1}')
            print(Fore.GREEN + f"Simplified arithmetic operation: {var} = {var1} {operator} {var2} to {var} = 2 * {var1}" + Style.RESET_ALL)


    return code

def deobfuscate(file_path, output_path):
    with open(file_path, 'r') as file:
        code = file.read()

    # Find all variable assignments and function definitions
    assignments = re.findall(r'\blocal (\w+)', code)
    functions = re.findall(r'function (\w+)', code)

    # Create a mapping of old variable names to new names
    var_mapping = {var: f'var{i}' for i, var in enumerate(set(assignments))}

    # Replace old variable names with new names
    for old_var, new_var in var_mapping.items():
        code = re.sub(r'\b' + re.escape(old_var) + r'\b', new_var, code)
        print(Fore.GREEN + f"Renamed variable: {old_var} to {new_var}" + Style.RESET_ALL)

    # Remove dead code (code after return statements)
    new_code = re.sub(r'return\s*$', 'return', code, flags=re.MULTILINE)
    if new_code != code:
        print(Fore.YELLOW + "Removed dead code" + Style.RESET_ALL)
        code = new_code
    else:
        print(Fore.RED + "No dead code found" + Style.RESET_ALL)
        
    # Remove unused variables
    used_vars = set(re.findall(r'\bvar\d+\b', code))
    for old_var, new_var in var_mapping.items():
        if new_var not in used_vars:
            code = re.sub(r'\b' + re.escape(new_var) + r'\b', '', code)
            print(Fore.GREEN + f"Removed unused variable: {new_var}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Variable {new_var} is used" + Style.RESET_ALL)
            
    # Handle redefined variables
    for old_var, new_var in var_mapping.items():
        redefined_vars = re.findall(r'\blocal ' + re.escape(old_var) + r'\b', code)
        if len(redefined_vars) > 1:
            for i in range(1, len(redefined_vars)):
                new_var_i = f'{new_var}_{i}'
                code = re.sub(r'\blocal ' + re.escape(old_var) + r'\b', 'local ' + new_var_i, code, count=1)
                print(Fore.GREEN + f"Renamed redefined variable: {old_var} to {new_var_i}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Variable {old_var} is not redefined" + Style.RESET_ALL)
                    
    # Custom string deobfuscation
    strings = re.findall(r'M\.b\((.*?)\)', code)
    for string in strings:
        deobfuscated_string = deobfuscate_custom(string)
        code = code.replace(string, deobfuscated_string)
        print(Fore.GREEN + f"Deobfuscated string using method {deobfuscate_custom.__name__}: {string} to {deobfuscated_string}" + Style.RESET_ALL)
        
    # arithmetic operations deobfuscation
    arithmetic_operations = re.findall(r'(\bvar\d+\b) = (\bvar\d+\b) (.) (\bvar\d+\b)', code)
    for operation in arithmetic_operations:
        var, var1, operator, var2 = operation
        if operator == '+':
            code = code.replace(f'{var} = {var1} {operator} {var2}', f'{var} = {var1} - {var2}')
            print(Fore.GREEN + f"Deobfuscated arithmetic operation: {var} = {var1} {operator} {var2} to {var} = {var1} - {var2}" + Style.RESET_ALL)
        elif operator == '-':
            code = code.replace(f'{var} = {var1} {operator} {var2}', f'{var} = {var1} + {var2}')
            print(Fore.GREEN + f"Deobfuscated arithmetic operation: {var} = {var1} {operator} {var2} to {var} = {var1} + {var2}" + Style.RESET_ALL)
        # work on other operators

    # Simplify constant calculations
    constant_calculations = re.findall(r'(\d+\.\d+) / (\d+\.\d+) \+ (\d+\.\d+)', code)
    for calculation in constant_calculations:
        num1, num2, num3 = map(float, calculation)
        simplified_value = num1 / num2 + num3
        code = code.replace(f'{num1} / {num2} + {num3}', str(simplified_value))
        print(Fore.GREEN + f"Simplified calculation: {num1} / {num2} + {num3} to {simplified_value}" + Style.RESET_ALL)
        
    # Remove useless calculations
    used_vars = set(re.findall(r'\bvar\d+\b', code))
    calculations = re.findall(r'(\bvar\d+\b) = .+', code)
    for calculation in calculations:
        var = calculation.split(' = ')[0]
        if var not in used_vars:
            code = code.replace(calculation, '')
            print(Fore.GREEN + f"Removed useless calculation: {calculation}" + Style.RESET_ALL)
            
    # Remove useless if statements
    if_statements = re.findall(r'if .+ then\n\t.+\nend', code)
    for statement in if_statements:
        # Check if the if statement always evaluates to the same value
        if re.search(r'if true then\n\tend', statement) or re.search(r'if false then\n\tend', statement):
            code = code.replace(statement, '')
            print(Fore.GREEN + f"Removed useless if statement: {statement}" + Style.RESET_ALL)
            
    # Remove useless loops
    loops = re.findall(r'for .+ do\n\t.+\nend', code)
    for loop in loops:
        # Check if the loop iterates a fixed number of times and doesn't modify any variables
        if re.search(r'for \(\d+, \d+\) do\n\tend', loop):
            code = code.replace(loop, '')
            print(Fore.GREEN + f"Removed useless loop: {loop}" + Style.RESET_ALL)
        
    # Remove useless function calls and definitions
    function_calls = re.findall(r'\bvar\d+\b\(.+\)', code)
    for call in function_calls:
        # Check if the function is defined and called but doesn't do anything
        if re.search(r'function ' + re.escape(call.split('(')[0]) + r'\(\)\n\tend', code):
            code = code.replace(call, '')
            print(Fore.GREEN + f"Removed useless function call: {call}" + Style.RESET_ALL)

            
    # Remove useless function definitions
    for function in functions:
        if function not in used_vars:
            code = re.sub(r'function ' + re.escape(function) + r'\(.+end', '', code)
            print(Fore.GREEN + f"Removed useless function: {function}" + Style.RESET_ALL)
            
    # Remove useless variable assignments
    assignments = re.findall(r'\bvar\d+\b = .+', code)
    for assignment in assignments:
        var = assignment.split(' = ')[0]
        if var not in used_vars:
            code = code.replace(assignment, '')
            print(Fore.GREEN + f"Removed useless assignment: {assignment}" + Style.RESET_ALL)
            
    
    # Remove unused dictionary keys
    dict_keys = re.findall(r'G\.\w+ = .+', code)
    for key in dict_keys:
        key_name = key.split(' = ')[0]
        if code.count(key_name) == 1:  # The key is not used elsewhere
            code = code.replace(key, '')
            print(Fore.GREEN + f"Removed unused dictionary key: {key}" + Style.RESET_ALL)


    # Attempt to prettify the code
    code = prettify_lua(code)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(code)

    print(Fore.BLUE + f"Deobfuscated and prettified code written to: {output_path}" + Style.RESET_ALL)

deobfuscate('script.lua', 'cleaned_script.lua')