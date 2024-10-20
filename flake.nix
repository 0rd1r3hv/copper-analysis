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
              qt6.wrapQtAppsHook
            ];
            shellHook = '''';
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
