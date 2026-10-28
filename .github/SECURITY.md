# Security policy

platformdirs is a Python library that returns the platform's conventional directories for user and site data, config,
cache, state, logs and runtime files. This policy says how to report a security problem and how we decide whether a
report is one.

## Reporting a vulnerability

**Do not open a public issue for a security problem.** Use
[GitHub's private vulnerability reporting](https://github.com/tox-dev/platformdirs/security/advisories/new). If you do
not have a GitHub account, or you are a Tidelift subscriber, report through the
[Tidelift security contact](https://tidelift.com/security) instead; Tidelift coordinates the fix and the disclosure with
us. If neither works for you, email [gaborjbernat@gmail.com](mailto:gaborjbernat@gmail.com).

Include what the attacker controls and what they gain, the steps or a proof of concept, and the versions and platform
you tested. Write the report yourself; unreviewed tool or model output takes longer to triage.

## What to expect

Volunteers maintain platformdirs, with no on-call rotation. We aim to acknowledge a report within **5 working days** and
assess it within **15 working days**. Fixes are developed in a private fork attached to the draft advisory, ship in a
new release, and the advisory, with a CVE requested through GitHub, goes out with that release. The default embargo is
**90 days** from the report; we agree any change with the reporter. We credit reporters in the advisory under the name
they choose, or not at all. There is no bug bounty.

## Supported versions

Only the latest release receives fixes. Confirm the problem reproduces on it before reporting.

## Vulnerability or bug

A report is a vulnerability when an attacker who controls only an input that the [threat model](THREAT_MODEL.md) lists
as untrusted breaks a guarantee platformdirs makes. A report that first needs control of something the threat model
trusts, such as the process environment, the user's home directory or a base directory the application supplies, is a
bug: we fix it in the open and publish no advisory. Classify by who supplies the dangerous input, not by how bad the
outcome sounds.

**In scope**

- An `appname`, `appauthor`, `version` or `place_*_file`/`find_*_file` name that escapes its base directory, for example
  through an absolute path, a drive, a UNC form or `..`.
- A symlink or race in a shared parent making `ensure_exists` or `place_*_file` create or return a path somewhere else,
  with the caller's privileges.
- A user data, config, cache, state, log or runtime directory on Unix, macOS, Android or iOS, created under
  `ensure_exists` or by `place_*_file`, with a mode wider than `0o700`, or `find_*_file` returning another user's file
  against its documented search order.
- `user_runtime_dir` using an `$XDG_RUNTIME_DIR` or the default runtime directory (`/run/user/<uid>` on Linux) that is a
  symlink, not a directory, owned by another user or not mode `0o700`, or a temporary fallback that is a symlink, not a
  directory or owned by another user.
- A path built from an XDG variable that the XDG specification says to ignore, such as a relative one.
- A crafted value causing a crash, hang or malformed path, rated Low.

**Out of scope**

- Values in the process environment (`HOME`, `XDG_*`, `APPDATA`, `WIN_PD_OVERRIDE_*`, `ANDROID_DATA`) pointing somewhere
  unexpected; whoever sets the environment already controls the process.
- Permissions of directories that already exist, and of site directories, which keep the default mode so other users can
  read them.
- A platform result that follows the documented operating-system convention.
- What an application does with a correct path, and who else can read what it stores there.
- Root running with `use_site_for_root`, which documents that it creates readable site directories.

If you cannot tell which side a finding falls on, report it privately and we will decide.
