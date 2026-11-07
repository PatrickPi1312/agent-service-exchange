# Build the next integration

We welcome small, tested client examples for AI assistants that help people
request real-world services. Useful first contributions:

- A TypeScript client matching the Python demo's review-only write boundary.
- A consent step that previews recipient and exact enquiry before submission.
- An integration recipe for a property-management or office assistant.
- Clear error handling when there is no participating provider in a region.

Open an issue with the proposed use case before a large contribution. Include
the client/version, minimal reproduction and expected behaviour for bugs.
Use synthetic data only. Never post customer details, keys or private enquiries.

Run `uv run examples/demo.py` to use the isolated review service. It only accepts
its exact fixtures and cannot send email. Public-service rate limits apply;
do not run network demos on every CI build. `--live-read-only` only searches.

After installing `examples/requirements.txt`, run the offline boundary checks:
`python -m unittest discover -s examples -p 'test_*.py' -v`.
These checks use no network and create no enquiries.

The MIT licence applies to files in this public repository. The hosted backend
is a separate commercial service governed by its published terms; this licence
does not grant access to private backend code, customer data or third-party brands.

The maintainers may decline promotional or unrelated submissions. Community
contributions do not activate provider participation or establish service capacity.
