# Lua Deobfuscator

This is a simple Python script to deobfuscate Lua code. It uses a variety of techniques to simplify and clean up obfuscated Lua code, making it easier to read and understand.

## Features

- Variable renaming: All variables are renamed to a standard format for consistency.
- Dead code removal: Unreachable code after return statements is removed.
- Unused variable removal: Variables that are declared but never used are removed.
- Redefined variable handling: Variables that are redefined are renamed to avoid confusion.
- String deobfuscation: Strings that are obfuscated using common techniques are deobfuscated.
- Arithmetic operation deobfuscation: Arithmetic operations that are obfuscated are deobfuscated.
- Constant calculation simplification: Constant calculations are simplified to their result.
- Useless calculation removal: Calculations that don't affect the program's output are removed.
- Useless if statement removal: If statements that always evaluate to the same value are removed.
- Useless loop removal: Loops that iterate a fixed number of times and don't modify any variables are removed.
- Useless function call and definition removal: Functions that are defined and called but don't do anything are removed.
- Unused dictionary key removal: Dictionary keys that are not used elsewhere are removed.
- Code prettification: The code is formatted for readability.

## Usage

To use this script, simply call the `deobfuscate` function with the path to the Lua script you want to deobfuscate and the path where you want to save the deobfuscated code:

```python
deobfuscate('script.lua', 'cleaned_script.lua')
```

This will deobfuscate the code in `script.lua` and save the result to `cleaned_script.lua`.

## Dependencies

This script uses the `re`, `base64`, `urllib.parse`, `binascii`, `codecs`, and `colorama` Python libraries. You can install these with pip:

```bash
pip install colorama
```

The other libraries are part of the Python standard library and should be available by default.

## Limitations

This script is intended for simple Lua obfuscation techniques. It may not work correctly with more complex obfuscation techniques or with code that is not valid Lua code.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.