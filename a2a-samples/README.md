# Agent2Agent (A2A) Samples

This repository contains code samples and demos which use the [Agent2Agent (A2A) Protocol](https://goo.gle/a2a).

## Related Repositories

- [A2A](https://github.com/a2aproject/A2A) - A2A Specification and documentation.
- [a2a-python](https://github.com/a2aproject/a2a-python) - A2A Python SDK.
- [a2a-inspector](https://github.com/a2aproject/a2a-inspector) - UI tool for inspecting A2A enabled agents.

## Contributing

Contributions welcome! See the [Contributing Guide](CONTRIBUTING.md).

## Getting help

Please use the [issues page](https://github.com/a2aproject/a2a-samples/issues) to provide suggestions, feedback or submit a bug report.

## Disclaimer

This repository itself is not an officially supported Google product. The code in this repository is for demonstrative purposes only.

Important: The sample code provided is for demonstration purposes and illustrates the mechanics of the Agent-to-Agent (A2A) protocol. When building production applications, it is critical to treat any agent operating outside of your direct control as a potentially untrusted entity.

All data received from an external agent—including but not limited to its AgentCard, messages, artifacts, and task statuses—should be handled as untrusted input. For example, a malicious agent could provide an AgentCard containing crafted data in its fields (e.g., description, name, skills.description). If this data is used without sanitization to construct prompts for a Large Language Model (LLM), it could expose your application to prompt injection attacks.  Failure to properly validate and sanitize this data before use can introduce security vulnerabilities into your application.

Developers are responsible for implementing appropriate security measures, such as input validation and secure handling of credentials to protect their systems and users.
