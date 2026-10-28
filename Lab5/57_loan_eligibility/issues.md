# Lab 5 - Issue table (`loan_calculator.py`)

Before: Pylint 5.17/10, Bandit 8 issues (2 High, 1 Medium, 5 Low), Flake8 21 issues.
After: Pylint 10.00/10, Bandit 0 issues, Flake8 0 issues.

Reports: `reports/before/` and `reports/after/`.

## Security (Bandit) - commit 1

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| FTP used (B402, B321) | Security (High) | 3, 68 | Plain FTP sends the login and the report unencrypted. | Replaced `ftplib` with SFTP via `paramiko`; host keys are checked, unknown hosts are rejected. |
| `marshal.loads` (B302) | Security (Medium) | 64 | Deserialising a file with `marshal` is unsafe and the format is Python-version specific. | Store the loan book as JSON (`json.dump` / `json.load`). |
| Hardcoded password (B107) | Security (Low) | 67 | `password="Bureau#2024"` is committed to the repo. | Read `LOAN_BUREAU_USER` / `LOAN_BUREAU_PASSWORD` from environment variables. |
| `random` for IDs (B311) | Security (Low) | 51 | `random` is predictable, so application IDs could be guessed. | Use `secrets.randbelow`. |
| `subprocess` calling `mail` (B404, B603, B607) | Security (Low) | 6, 74 | Runs an external program found through PATH with user-supplied input. | Send the email with `smtplib` / `EmailMessage`; no subprocess at all. |

## Code quality (Pylint) - commit 2

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Mutable default arg `history=[]` (W0102) | Bug | 20 | One list is shared by every call, so history leaks between calls. | Default to `None` and create the list inside; made keyword-only. |
| `max_loan_amount` ignores the rate (W0613 unused `annual_rate`) | Bug | 33-38 | It adds `available` for every month, so interest is ignored and the loan is overstated (900,000 instead of about 722,600). | Invert the EMI formula to get the principal an EMI can support. |
| Unknown loan type approved (logic) | Bug | 24-29 | A "crypto" loan returned True because the score/income shortcut ran before the loan-type check. | Check the loan type first and reject anything not in `VALID_LOAN_TYPES`. |
| Wrong rate in the demo (found by running) | Bug | 94 | `calculateEMI(500000, 9, 5)` used 9 instead of 0.09 and printed an EMI of 375,000. | Pass `0.09`. |
| Division by zero | Bug | 14-18, 26 | `calculate_emi` fails at 0% interest and `check_eligibility` fails when income is 0. | Handle rate 0 as `principal / months`; reject income <= 0. |
| Redefined built-in `sum`, unused `month`, unused import `math` (W0622, W0612, W0611) | Warning | 2, 34-36 | Shadows a built-in and leaves dead code. | Removed them; the loop became a closed-form formula. |
| `global` statement (W0603) | Warning | 62 | Rebinding a module global is hard to follow. | Update the dict in place with `clear()` / `update()`. |
| Files opened without `with` (R1732) | Refactor | 56, 63, 70 | A file is left open if an exception is raised. | Use `with open(...)`; SFTP `put` replaces the manual open. |
| camelCase names (C0103) | Convention | 14-81 (every function) | Does not follow PEP 8 snake_case. | Renamed all functions. |
| Missing docstrings (C0114, C0116) | Convention | all | No module or function documentation. | Added docstrings. |
| Redundant `else`/`elif`, `or` chain, parens, f-string (R1705, R1714, R1703, C0325, W1309) | Refactor | 28, 79, 82-91, 104 | Needlessly verbose code. | Simplified to direct returns, `in`, plain strings. |
| Too many arguments (R0913) | Refactor | 20 | `check_eligibility` has 6 parameters. | Kept as is to avoid changing the public API; silenced with a commented `disable-next`. |
| Demo ran on import (design) | Design | 93, 106 | `main()` ran whenever the module was imported. | Added `if __name__ == "__main__":`. |

## Style (Flake8) - commit 3

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| E302 / E305 blank lines | Style | 14-106 | Needs two blank lines around top-level functions. | Added them. |
| E501 line too long | Style | 20, 55, 70, 78, 95, 96, 100 | Lines over 79 characters. | Wrapped long calls, dicts and strings. |
| F401 / F541 | Style | 2, 104 | Unused import and an f-string with no placeholders. | Removed (also fixed in commit 2). |
