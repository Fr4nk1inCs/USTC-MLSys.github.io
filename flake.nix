{
  description = "USTC MLSys lab site — Astro.js dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.nodejs_22
            pkgs.pnpm
          ];

          shellHook = ''
            echo "Node $(node --version) | pnpm $(pnpm --version)"
          '';
        };
      }
    );
}
