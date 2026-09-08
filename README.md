# Testcase Runner

A small command-line tool that runs a Python solution against a folder of
test cases and reports PASS/FAIL for each one, acting as a simplified version of what a CP judge does.

## Why I built this

I wished to explore the inner working of the CP engine, and built this project to learn more about this. I wanted skills pertinent to actually understanding how code is processed rather than only learning CP.

## How it works

- Point it at a solution file and a folder of test cases.
- Each test case is a pair of files: `N.in` (fed to the solution as input)
  and `N.out` (the expected output).
- The tool runs the solution once per test case, feeds it the `.in` file via
  stdin, captures what it prints, and compares that to the `.out` file.
- Each test times out after 5 seconds, so an infinite loop in a solution
  won't hang the system.

## Usage

```bash
python testcase_runner.py <path_to_solution.py> [tests_folder]
```

If `tests_folder` is omitted, it defaults to a folder named `tests` in the
current directory.

### Example

Given a solution `add_solution.py`:

```python
a = int(input())
b = int(input())
print(a + b)
```

And a test folder with matching pairs:

```
tests/
    1.in   ("3\n5")     1.out  ("8")
    2.in   ("10\n20")   2.out  ("30")
```

Run:

```bash
python testcase_runner.py add_solution.py tests
```

Output:

```
1.in: PASS
2.in: PASS

2/2 test cases passed.
```

If a test fails, the runner shows both the expected and actual output:

```
3.in: FAIL
expected: '3'
got:      '2'

2/3 test cases passed.
```

This repo also includes a working example under `add_tests/` with
`add_solution.py`, so you can try it immediately:

```bash
python testcase_runner.py add_solution.py add_tests
```

## Notes andlimitations

- Cuurrently Only Python solutions are supported (the solution path must end in `.py`).
- The runner only captures the solution's standard output. If a solution
  crashes, the test simply shows as FAIL with an empty "got" value rather
  than the underlying error so running the solution directly against the
  input file (e.g. `python add_solution.py < tests/1.in`) will show the
  real traceback if you need to debug why something failed.
- Comparison is exact string matching after trimming trailing whitespace and
  there's no support yet for floating-point tolerance or multiple valid
  answers.

## Requirements

- Python 3.7+
- Not using any third-party libraries. only the standard library
  (`subprocess`, `pathlib`, `sys`).
