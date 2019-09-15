from pathlib import WindowsPath

from yakuza.yk_shader_file import import_yakuza_shader_file

f = import_yakuza_shader_file(WindowsPath("./custom_data/sd_c1dzt[hair][vcol][ao].fxo"))
print(f)

f2 = import_yakuza_shader_file(WindowsPath("./custom_data/ps_lighting_from_depth_ssss.pso"))
print(f2)