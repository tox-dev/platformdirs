###########
 Changelog
###########

.. towncrier-draft-entries:: Unreleased

.. towncrier release notes start

*********************
 4.11.0 (2026-07-21)
*********************

- Declare support for Python 3.15 and run the test suite against it, currently in beta. :pr:`512`

*********************
 4.10.1 (2026-07-18)
*********************

- Stop leaking memory on repeated Windows folder lookups. ``get_win_folder_via_ctypes`` defined a fresh ``ctypes``
  structure on every call, and each one registered a pointer type that was never released; the resolver is now built
  once and reused. :pr:`507`

*********************
 4.10.0 (2026-05-28)
*********************

- Add :func:`~platformdirs.user_publicshare_dir`, :func:`~platformdirs.user_templates_dir`,
  :func:`~platformdirs.user_fonts_dir`, and :func:`~platformdirs.user_preference_dir` :pr:`491`
- Add :func:`~platformdirs.user_projects_dir` backed by ``$XDG_PROJECTS_DIR`` :pr:`490`
- Return only the first path from :func:`~platformdirs.site_config_path` on macOS when ``multipath`` is set :pr:`488` -
  by :user:`lphuc2250gma`

********************
 4.9.6 (2026-04-09)
********************

- Fix macOS XDG variables leaking across :func:`~platformdirs.user_config_dir`, :func:`~platformdirs.user_data_dir`, and
  :func:`~platformdirs.user_state_dir` when only some are set :pr:`473` - by :user:`Goddesen`
- Avoid duplicate site directories in Unix :meth:`~platformdirs.PlatformDirs.iter_config_dirs` and
  :meth:`~platformdirs.PlatformDirs.iter_data_dirs` when ``use_site_for_root`` is active :pr:`469` - by :user:`viccie30`

********************
 4.9.4 (2026-03-05)
********************

- Respect ``XDG_CONFIG_HOME`` when reading the user-dirs configuration :pr:`453` - by :user:`bysiber`
- Create the directory in Android :func:`~platformdirs.user_log_dir` and :func:`~platformdirs.user_runtime_dir` when
  ``ensure_exists`` is set :pr:`452` - by :user:`bysiber`

********************
 4.9.2 (2026-02-16)
********************

- No user-facing changes

********************
 4.9.1 (2026-02-14)
********************

- No user-facing changes

********************
 4.9.0 (2026-02-14)
********************

- Add :func:`~platformdirs.site_bin_dir` :pr:`443`
- Add :func:`~platformdirs.site_applications_dir` :pr:`442`
- Use the correct runtime directory path on OpenBSD :pr:`440`

********************
 4.8.0 (2026-02-14)
********************

- Add ``use_site_for_root`` to redirect ``user_*_dir`` to ``site_*_dir`` for root on Unix :pr:`426`
- Add :func:`~platformdirs.site_state_dir` for system-wide state :pr:`425`
- Add :func:`~platformdirs.site_log_dir` :pr:`424`
- Add :func:`~platformdirs.user_applications_dir` :pr:`432`
- Add :func:`~platformdirs.user_bin_dir` :pr:`430`
- Add ``PLATFORMDIRS_*`` environment variable overrides for Windows folder resolution :pr:`427`
- Add ``WIN_PD_OVERRIDE_*`` environment variable overrides for Windows folder resolution :pr:`428`
- Yield individual site directories from :meth:`~platformdirs.PlatformDirs.iter_data_dirs` and
  :meth:`~platformdirs.PlatformDirs.iter_config_dirs` on macOS :pr:`429`

********************
 4.7.1 (2026-02-13)
********************

- Avoid :exc:`FileNotFoundError` on Windows in sandboxed environments :pr:`422`

********************
 4.7.0 (2026-02-12)
********************

- Fall back to a temp directory when the Unix runtime dir is not writable :pr:`369` - by :user:`lengau`
- Use ``SHGetKnownFolderPath`` instead of the deprecated ``SHGetFolderPathW`` on Windows :pr:`380` - by :user:`moi15moi`

********************
 4.6.0 (2026-02-12)
********************

- Honor XDG environment variables on macOS :pr:`375` - by :user:`Czaki`
- Fix :func:`~platformdirs.site_cache_dir` documentation :pr:`402` - by :user:`brianhelba`
- Fix an outdated link and correct a function docstring :pr:`398` - by :user:`joclement`

********************
 4.5.1 (2025-12-05)
********************

- Fix no-ctypes fallback on Windows :pr:`403` - by :user:`youknowone`

********************
 4.5.0 (2025-10-08)
********************

- Add support for Python 3.14 :pr:`382` - by :user:`hugovk`
- Drop support for Python 3.9 :pr:`389`
- Update Windows file paths in README :pr:`385` - by :user:`ParadaCarleton`

********************
 4.4.0 (2025-08-26)
********************

- Improve Homebrew path detection :pr:`370` - by :user:`daeho-ro`

********************
 4.3.8 (2025-05-07)
********************

- Add missing examples and fix example order in README :pr:`355` - by :user:`gene1wood`

********************
 4.3.7 (2025-03-19)
********************

- Drop support for EOL Python 3.8 :pr:`330` - by :user:`hugovk`

********************
 4.3.6 (2024-09-17)
********************

- No user-facing changes

********************
 4.3.5 (2024-09-17)
********************

- No user-facing changes

********************
 4.3.4 (2024-09-17)
********************

- No user-facing changes

********************
 4.3.3 (2024-09-13)
********************

- No user-facing changes

********************
 4.3.2 (2024-09-08)
********************

- Fix multi-path returned from ``_path`` methods on macOS :pr:`299` - by :user:`matthewhughes934`

********************
 4.3.1 (2024-09-07)
********************

- No user-facing changes

********************
 4.3.0 (2024-09-07)
********************

- Make :class:`~platformdirs.PlatformDirs` usable as a mypy superclass without breaking other type checkers :pr:`295` -
  by :user:`Avasam`
- Add support for Python 3.13 :pr:`289` - by :user:`edgarrmondragon`

********************
 4.2.2 (2024-05-15)
********************

- Fix Android detection when ``python-for-android`` is present :pr:`277` - by :user:`tmolitor-stud-tu`

********************
 4.2.1 (2024-04-23)
********************

- Allow working without ctypes :pr:`275` - by :user:`youknowone`

********************
 4.2.0 (2024-01-31)
********************

- Add convenience methods to iterate over both user and site dirs and paths :pr:`258` - by :user:`SpaceshipOperations`
- Fix two typos referencing ``XDG_DATA_DIR`` :pr:`256` - by :user:`Freed-Wu`

********************
 4.1.0 (2023-12-04)
********************

- Drop support for EOL Python 3.7 :pr:`246` - by :user:`hugovk`
- Fix Linux :func:`~platformdirs.user_log_dir` example in README :pr:`245` - by :user:`dbohdan`

********************
 4.0.0 (2023-11-10)
********************

- Revert :func:`~platformdirs.site_cache_dir` on UNIX to ``/var/cache`` instead of ``/var/tmp`` :pr:`239` - by
  :user:`andersk`

*********************
 3.11.0 (2023-10-02)
*********************

- Detect Homebrew-installed software on macOS :pr:`232` - by :user:`singingwolfboy`

*********************
 3.10.0 (2023-07-29)
*********************

- Add :func:`~platformdirs.site_runtime_dir` :pr:`212` - by :user:`kemzeb`

********************
 3.9.1 (2023-07-15)
********************

- Optionally create the opinionated ``log`` subdirectory in :func:`~platformdirs.user_log_dir` on Unix :pr:`208` - by
  :user:`kemzeb`

********************
 3.9.0 (2023-07-15)
********************

- Add :func:`~platformdirs.user_desktop_dir` and :func:`~platformdirs.user_desktop_path` :pr:`200` - by
  :user:`lukacat10`

********************
 3.8.1 (2023-07-06)
********************

- Provide a fallback for :func:`~platformdirs.user_runtime_dir` on BSD :pr:`201` - by :user:`RayyanAnsari`

********************
 3.8.0 (2023-06-22)
********************

- No user-facing changes

********************
 3.7.0 (2023-06-20)
********************

- Return ``/var/run/user/$uid`` from :func:`~platformdirs.user_runtime_dir` on \*BSD :pr:`194` - by :user:`kemzeb`

********************
 3.6.0 (2023-06-18)
********************

- Add :func:`~platformdirs.user_downloads_dir` :pr:`192` - by :user:`cofiem`

********************
 3.5.3 (2023-06-09)
********************

- Add support for Python 3.12

********************
 3.5.2 (2023-06-09)
********************

- No user-facing changes

********************
 3.5.1 (2023-05-11)
********************

- Define ``getuid`` on all non-Windows platforms so :func:`~platformdirs.user_runtime_dir` works beyond Linux :pr:`183`

********************
 3.5.0 (2023-04-27)
********************

- Add :func:`~platformdirs.user_music_dir` :pr:`173` - by :user:`kemzeb`

********************
 3.4.0 (2023-04-26)
********************

- Add :func:`~platformdirs.user_videos_dir` :pr:`169` - by :user:`kemzeb`

********************
 3.3.0 (2023-04-25)
********************

- Add :func:`~platformdirs.user_pictures_dir` :pr:`167` - by :user:`kemzeb`

********************
 3.2.0 (2023-03-25)
********************

- Add the ``ensure_exists`` option to create directories when they are missing :pr:`155` - by :user:`smsearcy`

********************
 3.1.1 (2023-03-10)
********************

- Point :func:`~platformdirs.site_cache_dir` at ``/var/tmp`` instead of write-protected ``/var/cache`` on Unix :pr:`148`
  - by :user:`efiop`

********************
 3.1.0 (2023-03-03)
********************

- Add :func:`~platformdirs.site_cache_dir` :pr:`145` - by :user:`efiop`

********************
 3.0.0 (2023-02-06)
********************

- **BREAKING** Point macOS :func:`~platformdirs.user_config_dir` and :func:`~platformdirs.site_config_dir` at
  ``*/Library/Application Support`` to mirror the data dirs, and drop the trailing slash from
  :func:`~platformdirs.user_config_dir` and :func:`~platformdirs.user_data_dir` :pr:`137` - by :user:`ThomasWaldmann`

********************
 2.6.2 (2022-12-28)
********************

- Add ``typing-extensions`` as a dependency on Python < 3.8 :pr:`123` - by :user:`amacf`

********************
 2.6.1 (2022-12-29)
********************

- Detect Termux via ``$PREFIX`` when ``$SHELL`` is unset :pr:`115` - by :user:`Freed-Wu`

********************
 2.6.0 (2022-12-06)
********************

- Point :func:`~platformdirs.user_log_dir` at :func:`~platformdirs.user_state_dir` on Linux per the XDG spec :pr:`108` -
  by :user:`lordwelch`

********************
 2.5.4 (2022-11-12)
********************

- No user-facing changes

********************
 2.5.3 (2022-11-06)
********************

- Declare support for Python 3.11 :pr:`103` - by :user:`hugovk`

********************
 2.5.2 (2022-04-18)
********************

- Treat Android shells as Unix :pr:`72`

********************
 2.5.1 (2022-02-19)
********************

- Work out of the box under Nuitka standalone builds :pr:`68`

********************
 2.5.0 (2022-02-09)
********************

- Support the Termux subsystem :pr:`63` - by :user:`YariKartoshe4ka`

********************
 2.4.1 (2021-12-26)
********************

- **BREAKING** Drop Python 3.6 support :pr:`52`

********************
 2.4.0 (2021-09-25)
********************

- Add :func:`~platformdirs.user_documents_dir` :pr:`39` - by :user:`JuneStepp`

********************
 2.3.0 (2021-08-30)
********************

- Add :func:`~platformdirs.user_runtime_dir` for ``$XDG_RUNTIME_DIR`` :pr:`37` - by :user:`whonore`

********************
 2.2.0 (2021-07-29)
********************

- Unix: fall back to the default when the ``$XDG_*`` environment variable is empty :pr:`30` - by :user:`papr`

********************
 2.1.0 (2021-07-25)
********************

- Add ``pathlib.Path``-returning ``*_path`` API alongside the string variants :pr:`27` - by :user:`papr`
- Add Android support :pr:`18`
- Add type annotations :pr:`20` - by :user:`domdfcoding`
- **BREAKING** Drop Python 2.7 and 3.5 support :pr:`14` - by :user:`domdfcoding`

********************
 2.0.2 (2021-07-13)
********************

- No user-facing changes

********************
 2.0.0 (2021-07-12)
********************

- **BREAKING** Rename ``appdirs`` to ``platformdirs`` as part of the friendly fork
- **BREAKING** Remove support for end-of-life Pythons 2.6, 3.2, and 3.3
- **BREAKING** Correct the config directory on macOS
- Add support for Python 3.7, 3.8, and 3.9
