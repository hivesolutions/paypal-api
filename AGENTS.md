# AGENTS.md file

## Python Virtual Environment (venv)

The Python virtual environment for this repository is typically located in `.venv`.

## Project Structure

- `src/paypal` is the `paypal` package, the only package in `setup.py`, published to PyPI as `paypal-api`.
- Each PayPal resource has its own module with a mixin class (e.g. `PaymentAPI` in `payment.py`) whose methods build the URL from `self.base_url` and call `self.get` or `self.post`, returning the contents.
- `API` in `base.py` extends `appier.OAuth2API` and all the mixins, `oauth_token` gets an access token from `oauth2/token` with the client id and secret (client credentials grant) and appier sends that token with every other request, the token request itself passes `auth=False` and `token=False`.
- A new resource module must be mixed into `API` in `base.py` and exported in `__init__.py`.
- The credentials are read with `appier.conf("PAYPAL_ID")` and `appier.conf("PAYPAL_SECRET")` and can be overridden with the `client_id` and `client_secret` constructor arguments.
- `PAYPAL_SANDBOX` (true by default) selects `https://api.sandbox.paypal.com/v1/` instead of `https://api.paypal.com/v1/`, and `base_url` overrides both.
- `src/examples` holds an Appier web app (`PaypalApp`) that exposes the API calls as routes, it uses `PAYPAL_ID` and `PAYPAL_SECRET` and is not packaged.

## Formatting

Always format the code before committing, making sure that the Python code is properly formatted using:

```bash
pip install black
black .
```

The CI workflow checks the formatting with `black . --check`.

## Testing

To run the custom suite of unit test for PayPal API use the following sequence of commands that will install dependencies and run the appropriate test suite (last command).

Try to run the unit tests whenever making changes to the codebase, before committing new code.

```bash
pip install -r requirements.txt
pip install pytest
pytest
```

- Tests live in `src/paypal/test` (the `testpaths` of `pytest.ini`, where every `.py` file is collected) and are `unittest.TestCase` classes.
- The CI workflow runs `pytest` on CPython 2.7 and 3.5 up to the latest release and on PyPy 2.7, 3.6, 3.9 and 3.10, so tests must not rely on Python 3 only features such as `unittest.mock`.
- Tests must never reach the real PayPal API nor use real credentials, replace the HTTP methods of the `API` instance with fakes instead, which must also answer the `oauth2/token` request.
- Run the tests without `PAYPAL_SANDBOX`, `PAYPAL_ID` and `PAYPAL_SECRET` in the environment, as `API` reads them, an empty `PAYPAL_SANDBOX` turns the sandbox off.
- `python setup.py test` (`test_suite` is `paypal.test`) runs the same tests, the CI workflow still runs it on Python 3.8 and older and the deploy workflow on Python 2.7, recent setuptools no longer have it so use `pytest`.

## Style Guide

- Always update `CHANGELOG.md` according to semantic versioning, mentioning your changes in the unreleased section.
- Write commit messages using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Never bump the internal package version in `setup.py`. This is handled by the release process.
- Python files use CRLF as the line ending.
- The implementation should be done in Python 2.7+ and compatible with Python 3.13.
- No type annotations should exist in the `.py` files and if they exist they should be isolated in the `.pyi` files.
- The style should respect the black formatting.
- The implementation should be done in a way that is compatible with the existing codebase.
- Prefer `not item in list` over `item not in list`.
- Prefer `item == None` over `item is None`.
- The commenting style of the project is unique, try to keep commenting style consistent.

## Commit Messages

This project follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) with the following structure:

```text
<type>: <description>

<body>
```

### Commit Types

| Type       | Description                                             |
| ---------- | ------------------------------------------------------- |
| `feat`     | A new feature or functionality                          |
| `fix`      | A bug fix                                               |
| `docs`     | Documentation only changes                              |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore`    | Maintenance tasks, dependency updates, build changes    |
| `test`     | Adding or updating tests                                |
| `version`  | Version bump commits (reserved for releases)            |

### Guidelines

- Use lowercase for the type prefix.
- Use imperative mood in the description (e.g., "Add feature" not "Added feature").
- Keep the first line under 50 characters.
- Reference issue/PR numbers when applicable using `(#123)` at the end.
- For version releases, use the format `version: X.Y.Z`.
- Add an extra newline between subject and body.
- Make the body a series of bullet points about the commit.
- Be descriptive always making use of the body of the message.

### Examples

```text
feat: Add user authentication with OAuth 2.0 support (#138)
fix: Resolve race condition in database connection pool
docs: Add API endpoint documentation for v2 routes
refactor: Extract validation logic into reusable utility module
chore: Update dependencies to latest stable versions
test: Add integration tests for payment processing flow
version: 1.8.0
```

## Pre-Commit Checklist

Before committing, ensure that the following operations items check:

- [ ] Code is formatted with `black .`
- [ ] Tests pass: `pytest`
- [ ] CHANGELOG.md is updated in [Unreleased] section
- [ ] No debugging print statements or commented-out code
- [ ] CRLF line endings are preserved
- [ ] No type annotations in .py files (use .pyi if needed)

## New Release

To create a new release follow the following steps:

- Make sure that both the tests pass and the code formatting are valid.
- Increment (look at `CHANGELOG.md` for semver changes) the `version` value in `setup.py`.
- Move all the `CHANGELOG.md` Unreleased items that have at least one non empty item into a new section with the new version number and date, and then create new empty sub-sections (Added, Changed and Fixed) for the Unreleased section with a single empty item.
- Create a commit with the following message `version: $VERSION_NUMBER`.
- Push the commit.
- Create a new tag with the value of the new version number `$VERSION_NUMBER` (no `v` prefix) and push it, which runs the Deploy Workflow (`.github/workflows/deploy.yml`) that builds the source and wheel distributions and uploads them to PyPI as `paypal-api`.
- Create a new release on the GitHub repo using the Markdown from the corresponding version entry in `CHANGELOG.md` as the description of the release and the version number as the title. Do not include the title of the release (version and date) in the description.

## License

PayPal API is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).
