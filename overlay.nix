final: prev: {
  arm-description = final.callPackage ././arm_description/package.nix { };
  arm-moveit-config = final.callPackage ././arm_moveit_config/package.nix { };
  core-description = final.callPackage ././core_description/package.nix { };
  #core-gazebo = final.callPackage ././core_gazebo/package.nix {};
}
