# Proxy Validated Relationships Service

#### Secrets Scanning
Secrets scanning is enabled in the project Git Hooks and will prevent merges that obey regular expressions suspecting
secrets. Should the secrets scanner detect a suspected secret on commit the output of `[ERROR] Matched one or more prohibited patterns`
will show.

Should you wish to scan the entire code base you can use `./nhsd-git-secrets/git-secrets --scan` which will scan your entire
local codebase. To whitelist certain strings, files, phrases from being highlighted by the secrets scanner head to `.gitallowed`.

## Testing

The goal of our testing is to be able to demonstrate the Proxy Relationship Validation System dealing with scenarios we expect to have to deal with when the system goes live. The strategy for this is first to test API calls to our integration (INT) API gateway and demonstrate them working in Sprint Reviews.

Underpinning this is 'in the cloud' testing of the underlying components, e.g. lambdas and test functions. If we can repeatedly and automatically demonstrate these working then it should give us
confidence that the API they enable should work as well.

The tests for both of these approaches can be found in the [tests](tests) directory.