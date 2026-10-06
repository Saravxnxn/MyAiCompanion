from desktop.environment import DesktopEnvironment


environment = DesktopEnvironment()

surfaces = environment.get_surfaces()

for surface in surfaces:

    print(
        "Surface:",
        surface.left,
        surface.top,
        surface.right
    )