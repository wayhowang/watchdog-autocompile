# watchdog-autocompile
notify when any files are changed/moved/created/deleted


## Install
```
pip install git+https://github.com/wayhowang/watchdog-autocompile.git@main
```



## Usage

```
watchmedo tricks tricks.yaml
```

Example `tricks.yaml`
```
tricks:
- watchdog_autocompile.AutoCompileTrick:
    patterns: ["*"]
    ignore_patterns: []
    source_directory: "src"
    build_directory: "build"
    patterns_and_commands: 
    - pattern: ["*.c"]
      command: "gcc ${source} -o ${output}.o"
    - pattern: ["*.cpp"]
      command: "g++ ${source} -o ${output}.o"
```
* `output` is the expected output path. e.g. `output` is `build/abc.cpp` if `source` is `src/abc.cpp`  
* sync files that matches `patterns`
* execute commands according to `patterns_and_commands`

It is a made example since there are a lot of much better tools for C/C++...