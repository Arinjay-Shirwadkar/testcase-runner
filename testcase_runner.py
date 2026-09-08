import sys
import subprocess
from pathlib import Path

def run_solution(command, inp_text):
    result= subprocess.run(command,
        input=inp_text,
        capture_output=True,
        text=True,
        timeout=5,
        )
    return result.stdout.strip()

def find_test_cases(tests: Path):
    in_files= sorted(tests.glob("*.in"))
    pairs= []
    for in_file in in_files:
        out_file = in_file.with_suffix(".out")
        if out_file.exists():
            pairs.append((in_file, out_file))
        else:
            print(f"No matching .out file for {in_file.name}, so am skipping.")
    return pairs

def build_command(solution_path: str) -> list:
    #check for cpp too, if you get time
    if solution_path.endswith('.py'):
        return ["python",solution_path]
    else:
        raise ValueError("Please ensure the solution path is a python file")

def main():
    l = len(sys.argv)
    if l<2:
        #no foldeer mentioned
        print("Please use as : python testcase_runner.py <pathtosolution> [tests folder]")
        sys.exit(1)

    #the standard cl input will be python testcase_runner.py <pathtosolution> [tests folder]
    solution = sys.argv[1]
    if l>2:
        tests = Path(sys.argv[2])
    else:
        tests=Path("tests")
        #still, we can fallback on the folder "tests" if nothing be mentioned

    if not tests.exists():
       print(f"The test folder '{tests}' was not found.")
       sys.exit(1)

    #now we will use these functions
    try:
        command = build_command(solution)
    except ValueError as ve:
        print(ve)
        sys.exit(1)
    test_cases = find_test_cases(tests)

    if not test_cases:
        print(f"No test cases found in '{tests}'.")
        sys.exit(1)

    numpassed =0

    for inp_file, out_file in test_cases:
        inp_text = inp_file.read_text()
        expected = out_file.read_text().strip()

        try:
            actual = run_solution(command, inp_text)
        except subprocess.TimeoutExpired:
            print(f"{inp_file.name}: FAIL due to time out")
            continue

        if actual== expected:
            print(f"{inp_file.name}: PASS")
            numpassed+=1
        else:
            print(f"{inp_file.name}: FAIL")
            print(f"expected: {expected!r}")
            print(f"got:      {actual!r}")

    print(f"\n{numpassed}/{len(test_cases)} test cases passed.")

if __name__ == "__main__":
    main()