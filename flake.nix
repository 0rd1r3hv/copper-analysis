{
  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-root.url = "github:srid/flake-root";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };
  outputs =
    inputs@{
      flake-parts,
      nixpkgs,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.flake-root.flakeModule
        inputs.treefmt-nix.flakeModule
      ];
      perSystem =
        {
          config,
          self',
          inputs',
          pkgs,
          self,
          system,
          ...
        }:
        {
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              qt6.qtbase
              qt6.full
              (sage.override {
                extraPythonPackages =
                  ps: with ps; [
                    loguru
                    pyside6
                    qt-material
                  ];
                requireSageTests = false;
              })
            ];
            inputsFrom = [
              config.flake-root.devShell
              config.treefmt.build.devShell
            ];
            nativeBuildInputs = with pkgs; [
              flatter
              qt6.wrapQtAppsHook
            ];
            shellHook = ''
              if [ -z ${"\${DIRENVED+x}"} ]; then
                export SHELL=nu
                echo "Entering sage subshell"
                export DIRENVED=1
                if which sage >/dev/null 2>&1; then
                  sage -sh
                else
                  echo "sage not found!"
                fi
              else
                echo "sage subshell found."
              fi
            '';
          };
          treefmt.config = {
            inherit (config.flake-root) projectRootFile;
            programs = {
              nixfmt.enable = true;
              ruff.enable = true;
            };
          };
        };
      systems = import inputs.systems;
    };
}
