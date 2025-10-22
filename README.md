# GitHub Actions

This repo contains GitHub actions used by ZeroC repositories.

Current actions:

- _whitespace_ - Validate trailing whitespace and consecutive newlines

## Usage

```yml
steps:
  - name: Run whitespace validation
    uses: zeroc-ice/github-actions/@main
    with:
      whitespace_patterns: "'*'"
```
