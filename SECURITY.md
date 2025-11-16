# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please do **NOT** create a public issue.

### Reporting Process

1. **Email**: Send details to security@promptvc.dev
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. **Response**: We'll respond within 48 hours
4. **Disclosure**: We'll work with you on coordinated disclosure

### Security Scope

**In scope:**
- Audit log tampering
- Unauthorized access to repository data
- Code injection through prompt content
- Path traversal vulnerabilities
- Command injection in CLI

**Out of scope:**
- Denial of service attacks
- Social engineering
- Physical security

## Security Best Practices

### For Users

1. **Restrict access** to `.prompt-vc/` directory
2. **Encrypt audit logs** before storing externally
3. **Use access controls** for repository files
4. **Regular backups** with secure storage
5. **Validate prompts** before committing

### For Developers

1. **Input validation** on all user inputs
2. **Path sanitization** for file operations
3. **No eval()** or exec() on user data
4. **Secure file permissions** on creation
5. **Audit log integrity** checks

## Known Security Considerations

### Audit Log Integrity

- Audit logs use JSON Lines format (append-only)
- Content-addressable storage prevents tampering
- Consider external backup for tamper-evidence

### File System Security

- Repository stored in `.prompt-vc/` directory
- Permissions should be restricted (e.g., `chmod 700`)
- Sensitive prompts should use file encryption

### Python Execution

- TypeScript bindings execute Python CLI via child_process
- Ensure Python package is from trusted source (PyPI)
- Validate CLI output to prevent injection

## Security Updates

Security updates will be released as patch versions and announced via:
- GitHub Security Advisories
- Release notes
- Email to registered users (if applicable)

## Bug Bounty

We currently do not have a bug bounty program, but we appreciate responsible disclosure and will acknowledge contributors.

## Contact

- **Security Email**: security@promptvc.dev
- **GPG Key**: [Coming soon]

---

Thank you for helping keep Prompt Versioning CLI secure!
