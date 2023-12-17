{
  description = "jherland's solutions to Advent Of Code 2023";

  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-unstable;
  };

  outputs = { nixpkgs, ... }@inputs: {
    devShells.x86_64-linux.default =
      let
        pkgs = nixpkgs.legacyPackages.x86_64-linux;
      in pkgs.mkShell {
        name = "AoC23";
        buildInputs = with pkgs; [
          git
          python312
          python312Packages.venvShellHook

          # Allow installation of binary wheels by
          # (a) providing manylinux2014 support, and
          # (b) patching binaries installed into the virtualenv.
          pythonManylinuxPackages.manylinux2014
          autoPatchelfHook
        ];
        venvDir = "./.venv";
        postShellHook = ''
          unset SOURCE_DATE_EPOCH
          pip install --upgrade pip
          pip install -e .[dev]
          # Patch binaries in the virtualenv to link against Nix deps
          autoPatchelf "$venvDir"
        '';
      };
    };
}
