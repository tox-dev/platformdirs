Check the parents of the temporary Unix runtime directory. Reject a group- or world-writable fallback, or tighten its permissions
under ``ensure_exists``. If no standard or configured temporary directory is usable, raise an error.
