from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode
from panda3d.core import BitMask32, Vec3,Vec2, Plane, Point3
from panda3d.core import CollisionSphere, CollisionNode
import math, random
from panda3d.core import CollisionRay, CollisionHandlerQueue, CollisionSegment
friction = 150.0

class GameObject():
    def __init__(self, pos, modelname, modelani, maxhp, maxsp, collidername):
        
        self.Actor = Actor(modelname,modelani)
        self.actor.reparentTo(self.render)
        self.actor.setPos(pos)

        self.maxHP = maxhp
        self.health = maxhp

        self.maxSP = maxsp

        self.velocity = Vec3(0, 0, 0)
        self.acc = 300

        self.walking = False

        colliderNode = CollisionNode(collidername)
        colliderNode.addSolid(CollisionSphere(0, 0, 0, 0.3))
        self.collider = self.actor.attachNewNode(colliderNode)
        self.collider.setPythonTag("owner",self)

        self.tempTrap = TrapEnemy(Vec3(-2, 7, 0))

    def update(self,dt):

        speed = self.velocity.length()

        #checking max speed
        if speed > self.maxSP : 
            self.velocity.normalize()
            self.velocity *= self.maxSP
            speed = self.maxSP

        #friction if walking
        if not self.walking:
            frictionval = friction*dt
            if frictionval > speed:
                self.velocity.set(0, 0, 0)
            else:
                frictionvec = -self.velocity
                frictionvec.normalize()
                frictionvec *= frictionval
                self.velocity += frictionvec

        self.actor.setPos(self.actor.getPos() + self.velocity*dt)
        
        self.tempTrap.update(self.player, dt)

    def alterhp(self,dhealth):

        self.health += dhealth
        if self.health > self.maxHP:
            self.health = self.maxHP
    
    def cleanup(self):
        if self.collider is not None and not self.collider.isEmpty():
            self.collider.clearPythonTag("owner")
            base.coltrav.removeCollider(self.collider)
            base.pusher.removeCollider(self.collider)

        if self.actor is not None:
            self.actor.cleanup()
            self.actor.removeNode()
            self.actor = None

        self.collider = None

class Player(GameObject):
    def __init__(self):
        GameObject.__init__(self, Vec3(0, 0, 0), "Models/PandaChan/act_p3d_chan",{"stand" : "Models/PandaChan/a_p3d_chan_idle", "walk" : "Models/PandaChan/a_p3d_chan_run"},5,10,"player")

        self.actor.getChild(0).setH(180)

        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.actor.loop("stand")

        self.ray = CollisionRay(0, 0, 0, 0, 1, 0)

        rayNode = CollisionNode("playerRay")
        rayNode.addSolid(self.ray)

        self.rayNodePath = render.attachNewNode(rayNode)
        self.rayQueue = CollisionHandlerQueue()

        base.cTrav.addCollider(self.rayNodePath, self.rayQueue)

        self.damagePerSecond = -5.0

        mask = BitMask32()
        mask.setBit(1)

        self.collider.node().setIntoCollideMask(mask)

        mask = BitMask32()
        mask.setBit(1)

        self.collider.node().setFromCollideMask(mask)

        mask = BitMask32()
        mask.setBit(2)
        rayNode.setFromCollideMask(mask)

        mask = BitMask32()
        rayNode.setIntoCollideMask(mask)

        self.beamModel = loader.loadModel("Models/Misc/bambooLaser")
        self.beamModel.reparentTo(self.actor)
        self.beamModel.setZ(1.5)
        self.beamModel.setLightOff()
        self.beamModel.hide()

        self.lastMousePos = Vec2(0, 0)

        self.groundPlane = Plane(Vec3(0, 0, 1), Vec3(0, 0, 0))

        self.yVector = Vec2(0, 1)



    def update(self, keys, dt):
        GameObject.update(self, dt)

        self.walking = False

        if keys["up"]:
            self.walking = True
            self.velocity.addY(self.acceleration*dt)
        if keys["down"]:
            self.walking = True
            self.velocity.addY(-self.acceleration*dt)
        if keys["left"]:
            self.walking = True
            self.velocity.addX(-self.acceleration*dt)
        if keys["right"]:
            self.walking = True
            self.velocity.addX(self.acceleration*dt)

        if self.walking:
            standControl = self.actor.getAnimControl("stand")
            if standControl.isPlaying():
                standControl.stop()

            walkControl = self.actor.getAnimControl("walk")
            if not walkControl.isPlaying():
                self.actor.loop("walk")
        else:
            standControl = self.actor.getAnimControl("stand")
            if not standControl.isPlaying():
                self.actor.stop("walk")
                self.actor.loop("stand")

        
        if keys["shoot"]:

            if self.rayQueue.getNumEntries() > 0:
                self.rayQueue.sortEntries()
                rayHit = self.rayQueue.getEntry(0)
                hitPos = rayHit.getSurfacePoint(self.render)
                hitNodePath = rayHit.getIntoNodePath()
                
                if hitNodePath.hasPythonTag("owner"):
                    hitObject = hitNodePath.getPythonTag("owner")
                    
                    if not isinstance(hitObject, TrapEnemy):
                        hitObject.alterHealth(self.damagePerSecond*dt)
                
                beamLength = (hitPos - self.actor.getPos()).length()
                self.beamModel.setSy(beamLength)

                self.beamModel.show()
        else:
            self.beamModel.hide()

        mouseWatcher = base.mouseWatcherNode
        if mouseWatcher.hasMouse():
            mousePos = mouseWatcher.getMouse()
        else:
            mousePos = self.lastMousePos
        
        mousePos3D = Point3()
        nearPoint = Point3()
        farPoint = Point3()

        base.camLens.extrude(mousePos, nearPoint, farPoint)
        self.groundPlane.intersectsLine(mousePos3D, render.getRelativePoint(base.camera, nearPoint), render.getRelativePoint(base.camera, farPoint))


        firingVector = Vec3(mousePos3D - self.actor.getPos())
        firingVector2D = firingVector.getXy()
        firingVector2D.normalize()
        firingVector.normalize()

        heading = self.yVector.signedAngleDeg(firingVector2D)

        self.actor.setH(heading)

        if firingVector.length() > 0.001:
            self.ray.setOrigin(self.actor.getPos())
            self.ray.setDirection(firingVector)

        self.lastMousePos = mousePos

    def cleanup(self):

        base.cTrav.removeCollider(self.rayNodePath)
        GameObject.cleanup(self)

class Enemy(GameObject):
    def __init__(self, pos, modelname, modelani, maxhp, maxsp, collidername):
        
        GameObject.__init__(self, pos, modelname, modelani, maxhp, maxsp, collidername)

        self.scoreValue = 1

    def update(self, player, dt):

        GameObject.update(self, dt)

        self.runLogic(player, dt)

        #animation control
        if self.walking:
            walkingControl = self.actor.getAnimControl("walk")
            if not walkingControl.isPlaying():
                self.actor.loop("walk")
        else:
            spawnControl = self.actor.getAnimControl("spawn")
            if spawnControl is None or not spawnControl.isPlaying():
                attackControl = self.actor.getAnimControl("attack")
                if attackControl is None or not attackControl.isPlaying():
                    standControl = self.actor.getAnimControl("stand")
                    if not standControl.isPlaying():
                        self.actor.loop("stand")


    def runLogic(self, player, dt):
        pass

class WalkingEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos,"Models/Misc/simpleEnemy",{"stand" : "Models/Misc/simpleEnemy-stand","walk" : "Models/Misc/simpleEnemy-walk","attack" : "Models/Misc/simpleEnemy-attack","die" : "Models/Misc/simpleEnemy-die","spawn" : "Models/Misc/simpleEnemy-spawn"}, 3.0,7.0,"walkingEnemy")

        self.attackDistance = 0.75

        self.acceleration = 100.0

        self.yVector = Vec2(0, 1)
        mask = BitMask32()
        mask.setBit(2)

        self.collider.node().setIntoCollideMask(mask)

        self.attackSegment = CollisionSegment(0, 0, 0, 1, 0, 0)

        segmentNode = CollisionNode("enemyAttackSegment")
        segmentNode.addSolid(self.attackSegment)

        mask = BitMask32()
        mask.setBit(1)

        segmentNode.setFromCollideMask(mask)

        mask = BitMask32()

        segmentNode.setIntoCollideMask(mask)

        self.attackSegmentNodePath = render.attachNewNode(segmentNode)
        self.segmentQueue = CollisionHandlerQueue()

        base.cTrav.addCollider(self.attackSegmentNodePath, self.segmentQueue)

        self.attackDamage = -1

        self.attackDelay = 0.3
        self.attackDelayTimer = 0
        self.attackWaitTimer = 0

    def runLogic(self, player, dt):

        vectorToPlayer = player.actor.getPos() - self.actor.getPos()
        vectorToPlayer2D = vectorToPlayer.getXy()
        distanceToPlayer = vectorToPlayer2D.length()
        vectorToPlayer2D.normalize()

        heading = self.yVector.signedAngleDeg(vectorToPlayer2D)

        if distanceToPlayer > self.attackDistance*0.9:
            attackControl = self.actor.getAnimControl("attack")
            if not attackControl.isPlaying():
                self.walking = True
                vectorToPlayer.setZ(0)
                vectorToPlayer.normalize()
                self.velocity += vectorToPlayer*self.acceleration*dt
                self.attackWaitTimer = 0.2
                self.attackDelayTimer = 0
        else:
            self.walking = False
            self.velocity.set(0, 0, 0)

            if self.attackDelayTimer > 0:
                self.attackDelayTimer -= dt

                if self.attackDelayTimer <= 0:

                    if self.segmentQueue.getNumEntries() > 0:
                        self.segmentQueue.sortEntries()
                        segmentHit = self.segmentQueue.getEntry(0)
                        hitNodePath = segmentHit.getIntoNodePath()
                        
                        if hitNodePath.hasPythonTag("owner"):
                            hitObject = hitNodePath.getPythonTag("owner")
                            hitObject.alterHealth(self.attackDamage)
                            self.attackWaitTimer = 1.0

            elif self.attackWaitTimer > 0:
                self.attackWaitTimer -= dt

                if self.attackWaitTimer <= 0:
                    self.attackWaitTimer = random.uniform(0.5, 0.7)
                    self.attackDelayTimer = self.attackDelay
                    self.actor.play("attack")

        self.actor.setH(heading)
        self.attackSegment.setPointA(self.actor.getPos())
        self.attackSegment.setPointB(self.actor.getPos() + self.actor.getQuat().getForward()*self.attackDistance)
    
    def cleanup(self):

        base.cTrav.removeCollider(self.attackSegmentNodePath)
        self.attackSegmentNodePath.removeNode()

        GameObject.cleanup(self)

class TrapEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos,"Models/Misc/trap",{"stand" : "Models/Misc/trap-stand","walk" : "Models/Misc/trap-walk",},100.0,10.0,"trapEnemy")

        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.moveInX = False
        self.moveDirection = 0
        self.ignorePlayer = False

        mask = BitMask32()
        mask.setBit(2)
        mask.setBit(1)

        self.collider.node().setIntoCollideMask(mask)

        mask = BitMask32()
        mask.setBit(2)
        mask.setBit(1)

        self.collider.node().setFromCollideMask(mask)

    def runLogic(self, player, dt):
        if self.moveDirection != 0:
            self.walking = True
            if self.moveInX:
                self.velocity.addX(self.moveDirection*self.acceleration*dt)
            else:
                self.velocity.addY(self.moveDirection*self.acceleration*dt)
        else:
            self.walking = False
            diff = player.actor.getPos() - self.actor.getPos()
            if self.moveInX:
                detector = diff.y
                movement = diff.x
            else:
                detector = diff.x
                movement = diff.y

            if abs(detector) < 0.5:
                self.moveDirection = math.copysign(1, movement)

    def alterHealth(self, dHealth):
        pass

game=GameObject()
game.run()
