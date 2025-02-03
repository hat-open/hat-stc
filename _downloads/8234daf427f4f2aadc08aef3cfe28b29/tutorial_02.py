import hat.stc

def main():

    def act_print_state(door, evt):
        print('current state:', door.state)

    states = hat.stc.parse_scxml("door_01.scxml")
    actions = {'printState': act_print_state}
    door = hat.stc.Statechart(states, actions)

    print('registering close event')
    event = hat.stc.Event('close')
    door.step(event)

    print('registering open event')
    event = hat.stc.Event('open')
    door.step(event)

if __name__ == '__main__':
    main()
