# Controls and Rules

## Classic Control Mode

Classic control mode comes from Winmine. It is the most compatible and authoritative control mode. In short, there are three rules: left click is triggered on release, right click is triggered on press, and chording is triggered on release. The implementation is shown below:

```automaton
stateDiagram-v2
    Idle --> LeftButtonDown: left button down
    Idle --> TriggerFlag: right button down

    LeftButtonDown --> TriggerLeft: left button up
    TriggerLeft --> Idle

    LeftButtonDown --> ChordDown: right button down

    TriggerFlag --> Idle: right button up
    TriggerFlag --> ChordDown: left button down

    ChordDown --> TriggerChordRight: left button up
    ChordDown --> TriggerChordLeft: right button up

    TriggerChordRight --> Idle: right button up
    TriggerChordLeft --> Idle: left button up

    TriggerChordRight --> ChordDown: left button down
    TriggerChordLeft --> ChordDown: right button down
```

### 1.5-click

1.5-click is a technique that uses the difference between right-click and chord trigger timing to speed up flag-and-chord operations. Flagging and chording are often performed together: flagging needs one click, and chording needs one click. If both clicks require one press and one release, the whole sequence needs four press/release actions. In classic control mode, you can press the right button to flag, keep the right button held, press the left button, and then release both buttons to chord. This completes flagging and chording with three press/release actions. Since both pressing and releasing take time because of mouse hardware limits, three press/release actions are roughly equivalent to completing two clicks in 1.5 clicks of time, hence the name.

In practice, the benefit mainly depends on the time between pressing the right button and releasing the chord. During that interval, the mouse needs to move from the flagging position to the chording position, so the time cost differs greatly between players. In the extreme case, the left button is pressed immediately after the right button, and then both buttons are released, costing only one click's worth of time.

## Other Control Modes

### Left-button double click

Many newer Minesweeper programs and platforms use left-button double click. This mode has only two trigger points: left-button release and right-button press. The difference from classic mode is that releasing the left button on an unopened cell triggers a left click, while releasing it on an opened cell triggers a chord. The left and right buttons are independent, making the operation easier. Different platforms handle simultaneous left-right presses differently, so no specific implementation diagram is shown here.

### Touch controls

Touch controls are equivalent to having only a left button, so the question is how to implement right click. Some software provides a button to switch between left and right click. Some software distinguishes left and right click by long press.

### Swipe clicking

Swipe clicking is the most aggressive control mode. As the name suggests, after a button is pressed, every cell the cursor passes over is triggered until the button is released. Because it fundamentally changes the feel of Minesweeper controls, few programs support it.

### Assisted chording

Assisted chording means the software performs chording for the user. The software identifies numbers that have enough flags around them and automatically triggers a chord, or even recursively triggers chords. This feature also changes the feel of Minesweeper controls. It lets users focus more on logic than operation, so it is more popular than swipe clicking. Representative software with recursive chording includes Minesweeper Go, Chocolate Sweeper, and Meowsweeper.
