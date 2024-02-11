import pygame

from transitions import Machine, State


class MonsterState:
    def __init__(self, monster, player):
        self.monster = monster
        self.player = player


class MonsterIdleState(MonsterState):
    def on_enter(self):
        print(f"{self.monster.name} #{self.monster.id} has entered idle state")

    def on_exit(self):
        print(f"{self.monster.name} #{self.monster.id} is exiting idle state")

    def handle_input(self, event):
        pass


class MonsterAttackingState(MonsterState):
    def on_enter(self):
        print(f"{self.monster.name} #{self.monster.id} has entered attacking state")
        self.player.state_machine.attack()

    def on_exit(self):
        print(f"{self.monster.name} #{self.monster.id} is exiting attacking state")

    def handle_input(self, keys):
        pass


class MonsterChasingState(MonsterState):
    def on_enter(self):
        print(f"{self.monster.name} #{self.monster.id} has entered chasing state")

    def on_exit(self):
        print(f"{self.monster.name} #{self.monster.id} is exiting chasing state")

    def handle_input(self, event):
        pass


class MonsterDamagedState(MonsterState):
    def on_enter(self):
        print(f"{self.monster.name} #{self.monster.id} has entered damaged state")

    def on_exit(self):
        print(f"{self.monster.name} #{self.monster.id} is exiting damaged state")

    def handle_input(self, keys):
        pass


class MonsterDeadState(MonsterState):
    def on_enter(self):
        print(f"{self.monster.name} #{self.monster.id} has entered dead state")

    def handle_input(self, event):
        pass


class MonsterStateMachine:
    def __init__(self, monster, player):
        self.state_classes = {
            "idle": MonsterIdleState(monster, player),
            "attacking": MonsterAttackingState(monster, player),
            "chasing": MonsterChasingState(monster, player),
            "damaged": MonsterDamagedState(monster, player),
            "dead": MonsterDeadState(monster, player),
        }

        states = [
            State(
                name="idle",
                on_enter=self.state_classes["idle"].on_enter,
                on_exit=self.state_classes["idle"].on_exit,
            ),
            State(
                name="attacking",
                on_enter=self.state_classes["attacking"].on_enter,
                on_exit=self.state_classes["attacking"].on_exit,
            ),
            State(
                name="chasing",
                on_enter=self.state_classes["chasing"].on_enter,
                on_exit=self.state_classes["chasing"].on_exit,
            ),
            State(
                name="damaged",
                on_enter=self.state_classes["damaged"].on_enter,
                on_exit=self.state_classes["damaged"].on_exit,
            ),
            State(
                name="dead",
                on_enter=self.state_classes["dead"].on_enter,
            ),
        ]

        transitions = [
            ["idle", "*", "idle"],
            ["attack", "*", "attacking"],
            ["chase", "*", "chasing"],
            ["take_damage", "*", "damaged"],
            ["die", "*", "dead"],
        ]

        self.machine = Machine(
            model=self, states=states, transitions=transitions, initial="idle"
        )

    def update(self, dt):
        state_instance = self.state_classes[self.state]
        state_instance.update(dt)
