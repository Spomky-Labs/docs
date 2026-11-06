# The release process

Releases are versioned as `<major>.<minor>.<patch>`, following
[Semantic Versioning](https://semver.org/). A version may carry a suffix such as `-rc1` for an early
access build; those are pre-releases.

| What changed | What comes out |
|---|---|
| A backwards-compatible bug fix | A patch version |
| Functionality added, backwards-compatibly | A minor version |
| An incompatible API change | A major version |

## Backwards compatibility

You can upgrade from one minor version to the next with confidence. When a feature, an enhancement or a
fix cannot keep backwards compatibility, it waits for the next major version.

Two exceptions:

* **Experimental features and code marked `@internal`** are outside this policy. `OTPHP\InternalClock` is
  one of them.
* **A backwards compatibility break is tolerated when a security issue requires it.** The 19-byte minimum
  on digests, which landed in v11.5, is such a case.

## Maintained versions

Release branches are maintained for the three most recent minor releases; fixes, security fixes included,
may be backported to them depending on severity and feasibility. The current list is in
[RELEASES.md](https://github.com/Spomky-Labs/otphp/blob/HEAD/RELEASES.md), and the security policy in
[SECURITY.md](https://github.com/Spomky-Labs/otphp/blob/HEAD/SECURITY.md).

Older versions are not maintained. A pull request against one may be considered, without any guarantee.
