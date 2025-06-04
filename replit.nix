{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.pip
    pkgs.python39Packages.fastapi
    pkgs.python39Packages.uvicorn
    pkgs.python39Packages.passlib
    pkgs.python39Packages.sqlalchemy
    pkgs.python39Packages.aiohttp
    pkgs.python39Packages.python_jose
    pkgs.python39Packages.python_multipart
    pkgs.sqlite
  ];
}
