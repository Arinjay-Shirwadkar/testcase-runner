import sys
import subprocess
from pathlib import Path

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
    command = build_command(solution)
    test_cases = find_test_cases(tests)

    if not test_cases:
        print(f"No test cases found in '{tests}'.")
        sys.exit(1)

    numpassed =0

    for inp_file, out_file in test_cases:
        inp_text = inp_file.read_text()
        expected = out_file.read_text()

        try:
            actual = run_solution(command, inp_text)
        except subprocess.TimeoutExpired:
            print(f"{inp_file.name}: FAIL due to time out")
            continue

        if actual== expected:
            print(f"{inp_file.name}: PASS")
            passed+=1
        else:
            print(f"{inp_file.name}: FAIL")
            print(f"expected: {expected!r}")
            print(f"got:      {actual!r}")

    print(f"\n{numpassed}/{len(test_cases)} test cases passed.")

if __name__ == "__main__":
    main()