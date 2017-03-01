
# Check if user config or default config is newer than compiled config
#   Load compiled conf = config.Config.load(fpath)
# Else
#   Check if user exists
#   Read default, [user] : conf = config.parse(default, user)
#   Save it: conf.save(fpath)
