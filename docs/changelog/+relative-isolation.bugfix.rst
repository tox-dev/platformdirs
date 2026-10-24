Pin a relative ``isolated_dirs`` root on context entry so changing the working directory keeps directory lookups and
creation under the original isolation root. The context now yields an absolute path.
