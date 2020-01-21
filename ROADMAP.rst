=======
ROADMAP
=======

================================  PypiUpload  ================================
WARNING: Uploading via this command is deprecated, use twine to upload instead (https://pypi.org/p/twine/)
=============================  PypiUploadWheel  ==============================
WARNING: Uploading via this command is deprecated, use twine to upload instead (https://pypi.org/p/twine/)


- Materialize the Step interface and validate all steps against it
- Use subcommands: "releaser go"
- Try to improve appearance of the default commands list (e. g. blank lines)
- Create subcommand that adds new git commits to the top of CHANGES.rst
- Optionally xdg-open the wheel for convenience
- Switch from path.py to pathlib
- Implement the missing steps (see release_new_version.py)
