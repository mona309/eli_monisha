from setuptools import setup

setup(
    name = "Exploring panda3d with panda-chan",
    options = {
        "build_apps" : {

            "include_patterns" : [
                "health.png",
                "Models/PandaChan/a_p3d_chan_idle.egg.pz",
                "Models/PandaChan/a_p3d_chan_run.egg.pz",
                "Models/PandaChan/a_p3d_chan_step_l.egg.pz",
                "Models/PandaChan/a_p3d_chan_step_r.egg.pz",
                "Models/PandaChan/a_p3d_chan_walk.egg.pz",
                "Models/PandaChan/act_p3d_chan.egg.pz",
                "Models/Wbxkomik.ttf",
                "Models/Misc/bambooLaser.egg",
                "Models/Misc/bambooLaserHit.egg",
                "Models/Misc/environment.egg",
                "Models/Misc/playerHit.egg",
                "Models/Misc/simpleEnemy-attack.egg",
                "Models/Misc/simpleEnemy-die.egg",
                "Models/Misc/simpleEnemy-spawn.egg",
                "Models/Misc/simpleEnemy-stand.egg",
                "Models/Misc/simpleEnemy-walk.egg",
                "Models/Misc/simpleEnemy.egg",
                "Models/Misc/stoneFrame.png",
                "Models/Misc/trap-stand.egg",
                "Models/Misc/trap-walk.egg",
                "Models/Misc/trap.egg",
                "Models/Misc/UIButton.png",
                "Models/Misc/UIButtonDisabled.png",
                "Models/Misc/UIButtonHighlighted.png",
                "Models/Misc/UIButtonPressed.png",
                "Sounds/Defending-the-Princess-Haunted.ogg",
                "Sounds/enemyAttack.ogg",
                "Sounds/enemyDie.ogg",
                "Sounds/enemySpawn.ogg",
                "Sounds/FemaleDmgNoise.ogg",
                "Sounds/laserHit.ogg",
                "Sounds/laserNoHit.ogg",
                "Sounds/trapHitsSomething.ogg",
                "Sounds/trapSlide.ogg",
                "Sounds/trapStop.ogg",
                "Sounds/UIClick.ogg",

                  ],

            "gui_apps" : {"Exploring panda3d with panda-chan" : "Game.py" },

            "plugins" : [ "pandagl", "p3openal_audio" ],

            "platforms" : [ "manylinux1_x86_64", "macosx_10_6_x86_64", "win_amd64" ],

            "log_filename" : "$USER_APPDATA/PandaChan/output.log",

            "log_append" : False #refresh
        }
    }
)
