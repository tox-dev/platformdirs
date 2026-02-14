Changelog
=========
4.9.1 (2026-02-14)
------------------
- 📝 docs: enhance README, fix issues, and reorganize platforms.rst :pr:`445`

4.9.0 (2026-02-14)
------------------
- 📚 docs: split usage guide into tutorial, how-to, and reference :pr:`441`
- ✨ feat(api): add site_bin_dir property :pr:`443`
- ✨ feat(api): add site_applications_dir property :pr:`442`
- 🐛 fix(unix): use correct runtime dir path for OpenBSD :pr:`440`
- 📝 docs(usage): document use_site_for_root parameter :pr:`439`

4.8.0 (2026-02-14)
------------------
- 📝 docs(usage): note that home dir is in stdlib :pr:`431`
- ✨ feat(api): add user_applications_dir property :pr:`432`
- ✨ feat(api): add user_bin_dir property :pr:`430`
- 🐛 fix(macos): yield individual site dirs in iter_*_dirs :pr:`429`
- ✨ feat(windows): add WIN_PD_OVERRIDE_* env var overrides :pr:`428`
- ✨ feat(windows): add PLATFORMDIRS_* env var overrides :pr:`427`
- ✨ feat(api): add use_site_for_root parameter :pr:`426`
- ✨ feat(api): add site_state_dir for system-wide state :pr:`425`
- ✨ feat(api): add site_log_dir and document Store Python sandbox :pr:`424`
- 📝 docs(windows): document Store Python sandbox path behavior :pr:`423`

4.7.1 (2026-02-13)
------------------
- 🐛 fix(windows): avoid FileNotFoundError in sandboxed environments :pr:`422`

4.7.0 (2026-02-12)
------------------
- 🔧 build(release): adopt filelock-style automated workflow :pr:`420`
- 🐛 fix(unix): fall back to tempdir when runtime dir is not writable :pr:`369` - by :user:`lengau`
- Replace SHGetFolderPathW with SHGetKnownFolderPath :pr:`380` - by :user:`moi15moi`
- 📝 docs: restructure and fix cross-references :pr:`419`

4.6.0 (2026-02-12)
-------------------
- feat(macos): add XDG env var support via shared mixin :pr:`375` - by :user:`Czaki`
- build: migrate from hatch to tox with ty :pr:`415`
- Fix docs for ``site_cache_dir`` :pr:`402` - by :user:`brianhelba`
- Update outdated link and correct function doc :pr:`398` - by :user:`joclement`

4.5.1 (2025-12-05)
-------------------
- Fix no-ctypes fallback on windows :pr:`403` - by :user:`youknowone`

4.5.0 (2025-10-08)
-------------------
- Drop 3.9 support :pr:`389`
- Update Windows file paths in README :pr:`385` - by :user:`ParadaCarleton`
- Add support for Python 3.14 :pr:`382` - by :user:`hugovk`

4.4.0 (2025-08-26)
-------------------
- feat: improve homebrew path detection :pr:`370` - by :user:`daeho-ro`

4.3.8 (2025-05-07)
-------------------
- Add missing examples and fix order of examples in README :pr:`355` - by :user:`gene1wood`

4.3.7 (2025-03-19)
-------------------
- Drop support for EOL Python 3.8 :pr:`330` - by :user:`hugovk`
- Chunk dependabot updates into a single PR :pr:`311` - by :user:`ofek`

4.3.6 (2024-09-17)
-------------------
- Fix readme download target :pr:`307`

4.3.5 (2024-09-17)
-------------------
- Split build and publish for release :pr:`306`

4.3.4 (2024-09-17)
-------------------
- Use upstream setup-uv with uv python :pr:`305`

4.3.3 (2024-09-13)
-------------------
- Don't include outdated changelog in docs :pr:`301` - by :user:`cbm755`
- Update check.yml :pr:`302`

4.3.2 (2024-09-08)
-------------------
- Fix multi-path returned from ``_path`` methods on MacOS :pr:`299` - by :user:`matthewhughes934`
- Use uv as installer :pr:`300`

4.3.1 (2024-09-07)
-------------------
- Update README

4.3.0 (2024-09-07)
-------------------
- Ensure PlatformDirs is valid superclass type for mypy AND not an abstract class for other checkers :pr:`295` - by :user:`Avasam`
- Use ``include-hidden-files: true`` to upload coverage artifacts :pr:`298` - by :user:`edgarrmondragon`
- Test with latest PyPy :pr:`290` - by :user:`edgarrmondragon`
- Test with Python 3.13 :pr:`289` - by :user:`edgarrmondragon`
- Speed up Hatch installation :pr:`282` - by :user:`ofek`

4.2.2 (2024-05-15)
-------------------
- Fix android detection when python4android is present :pr:`277` - by :user:`tmolitor-stud-tu`

4.2.1 (2024-04-23)
-------------------
- Allow working without ctypes :pr:`275` - by :user:`youknowone`
- Update dead Microsoft's known folders documentation link :pr:`267` - by :user:`deronnax`
- Various minor fixes :pr:`263` - by :user:`deronnax`
- Use hatch over tox :pr:`262`
- Switch to ruff for formatting and use codespell and docformatter :pr:`261`

4.2.0 (2024-01-31)
-------------------
- Add convenience methods to ``PlatformDirsAPI`` that allow iterating over both user and site dirs/paths :pr:`258` - by :user:`SpaceshipOperations`
- Fix 2 typos about ``XDG_DATA_DIR`` :pr:`256` - by :user:`Freed-Wu`

4.1.0 (2023-12-04)
-------------------
- Drop support for EOL Python 3.7 :pr:`246` - by :user:`hugovk`
- Fix Linux ``user_log_dir`` example in README :pr:`245` - by :user:`dbohdan`
- Update changelog for 4.0.0 :pr:`242` - by :user:`rafalkrupinski`

4.0.0 (2023-11-10)
-------------------
- UNIX: revert ``site_cache_dir`` to use ``/var/cache`` instead of ``/var/tmp`` :pr:`239` - by :user:`andersk`

3.11.0 (2023-10-02)
--------------------
- BSD: provide a fallback for ``user_runtime_dir``

3.10.0 (2023-07-29)
--------------------
- Add missing user media directory docs

3.9.1 (2023-07-15)
-------------------
- Have ``user_runtime_dir`` return ``/var/run/user/uid`` for \*BSD

3.9.0 (2023-07-15)
-------------------
- Introduce ``user_downloads_dir``

3.8.1 (2023-07-06)
-------------------
- Use ruff

3.8.0 (2023-06-22)
-------------------
- Test with 3.12.0.b1

3.7.0 (2023-06-20)
-------------------
- Introduce ``user_music_dir``

3.6.0 (2023-06-18)
-------------------
- Introduce ``user_videos_dir``

3.5.3 (2023-06-09)
-------------------
- Introduce ``user_pictures_dir``

3.5.2 (2023-06-09)
-------------------
- Add 3.12 support
- Add ``tox.ini`` to sdist
- Removing Windows versions
- Better handling for UNIX support

3.5.1 (2023-05-11)
-------------------
- Add auto create directories optional

3.5.0 (2023-04-27)
-------------------
- ``site_cache_dir`` use ``/var/tmp`` instead of ``/var/cache`` on unix, as the later may be write protected

3.4.0 (2023-04-26)
-------------------
- Introduce ``site_cache_dir``

3.3.0 (2023-04-25)
-------------------
- Add ``appdirs`` keyword to package

3.2.0 (2023-03-25)
-------------------
- **BREAKING** Changed the config directory on macOS to point to ``*/Library/Application Support``
- macOS: remove erroneous trailing slash from ``user_config_dir`` and ``user_data_dir``

3.1.1 (2023-03-10)
-------------------
- Fix missing ``typing-extensions`` dependency

3.1.0 (2023-03-03)
-------------------
- Add detection of ``$PREFIX`` for android

3.0.1 (2023-03-02)
-------------------
- **BREAKING** Correct the log directory on Linux/Unix from ``XDG_CACHE_HOME`` to ``XDG_STATE_HOME`` per the XDG spec

3.0.0 (2023-02-06)
-------------------
- Fix licensing metadata
- Support 3.11
- Bump dependencies

2.6.2 (2022-12-28)
-------------------
- Fix missing ``typing-extensions`` dependency

2.6.1 (2022-12-29)
-------------------
- Add detection of ``$PREFIX`` for android

2.6.0 (2022-12-06)
-------------------
- **BREAKING** Correct the log directory on Linux/Unix from ``XDG_CACHE_HOME`` to ``XDG_STATE_HOME`` per the XDG spec

2.5.4 (2022-11-12)
-------------------
- Fix licensing metadata

2.5.3 (2022-11-06)
-------------------
- Support 3.11
- Bump dependencies

2.5.2 (2022-04-18)
-------------------
- Move packaging to hatchling from setuptools
- Treat android shells as unix

2.5.1 (2022-02-19)
-------------------
- Add native support for nuitka

2.5.0 (2022-02-09)
-------------------
- Add support for Termux subsystems

2.4.1 (2021-12-26)
-------------------
- Drop python 3.6 support

2.4.0 (2021-09-25)
-------------------
- Add ``user_documents_dir``

2.3.0 (2021-08-30)
-------------------
- Add ``user_runtime_dir`` and its path-returning equivalent

2.2.0 (2021-07-29)
-------------------
- Unix: Fallback to default if XDG environment variable is empty

2.1.0 (2021-07-25)
-------------------
- Add ``readthedocs.org`` documentation via Sphinx
- Modernize project layout
- Drop Python 2.7 and 3.5 support
- Android support
- Add type annotations
- Reorganize project layout to platform specific classes
- Add ``*_path`` API, returning :class:`~pathlib.Path` objects instead of :class:`str` - by :user:`papr`

2.0.2 (2021-07-13)
-------------------
- Fix ``__version__`` and ``__version_info__``

2.0.0 (2021-07-12)
-------------------
- **BREAKING** Name change as part of the friendly fork
- **BREAKING** Remove support for end-of-life Pythons 2.6, 3.2, and 3.3
- **BREAKING** Correct the config directory on OSX/macOS
- Add Python 3.7, 3.8, and 3.9 support
