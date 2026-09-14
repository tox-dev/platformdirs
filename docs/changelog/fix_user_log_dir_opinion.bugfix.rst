Fix: ``Unix.user_log_dir`` now respects ``opinion=False`` when ``use_site_for_root=True``.
Previously, when running as root and ``opinion=False``, ``user_log_dir`` incorrectly
returned ``site_log_dir`` instead of ``site_state_dir``, breaking the contract that
``user_log_dir == user_state_dir`` when ``opinion=False``.
