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
trusts, such as the process environment or the user's home directory, is a bug: we fix it in the open and publish no
advisory. Classify by who supplies the dangerous input, not by how bad the outcome sounds.

**In scope**

- `place_config_file` and the other `place_*_file` helpers returning a path outside the user directory for a relative
  `name`.
- Directories created by `place_*_file` with a mode wider than `0o700`.
- A path built from an XDG variable that the XDG specification says to ignore, such as a relative one.

**Out of scope**

- Values in the process environment (`HOME`, `XDG_*`, `APPDATA`, `ANDROID_DATA`) pointing somewhere unexpected; whoever
  sets the environment already controls the process.
- Permissions of directories that already exist, and of directories created by `ensure_exists`, which use the default
  mode.
- What an application stores in the returned directories, and who else can read them.
- Root running with `use_site_for_root`, which documents that it creates readable site directories.

If you cannot tell which side a finding falls on, report it privately and we will decide.
