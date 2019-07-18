# pyfsm - A simple Finite State Machine

![Python Version](https://img.shields.io/static/v1?label=python&message=3%2e7%2b&color=blue&style=flat-square)
![Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-blue?style=flat-square)

---

**Table of Contents**

- [Installation](#installation)
- [Classes](#classes)
- [License](#license)

## Installation

```console
pip install pyfsm
```

## Classes

### **StateType**

This class defines the supported types for a State:

- FSM_BEGIN_STATE: use to define a start point for the FSM
- FSM_NORMAL_STATE: use to define a normal state for the FSM
- FSM_END_STATE: use to define a end point for the FSM

### **State**

This class defines a FSM State. Properties associated with a State are:

- name: a unique identifier for this state
- type: the type of this state as defined by the **StateType** class
- enter_action: a string sent to the client when entering this state
- exit_action: a string sent to the client when exiting this state

### **Event**

This class defines a FSM Event. Property associated with an Event is:

- name: a unique identifier for this event

### **Transition**

A transition describes the next state depending on the current state and the event.The properties associated with a Transition are:

- event: the Event triggering the transition
- begin_state: the initial State for the transition
- end_state: the end State for the transition

### **FSM**

This class defines the FSM.The following properties are available:

- has_ended: True if the FSM is in END state
- current: The current state for the FSM

To properly communicates with the client, the FSM needs:

- a user callback method that takes an argument
- a user queue where the callback methods will be pushed

Everytime a change of states occured, the FSM will:

- push the callback in the queue with the exit_action from the previous state
- push the callback in the queue with the enter_action from the new state

#### Methods available to the client

*setup(user_callback, user_queue)*

This function is used to initiate the user callback and queue.
The user_queue should be an instance of *queue.Queue()*
The user_callback must take an argument:

```python
def user_callback(fsm_action):
    # do something with fsm_action
    #...
```

**FSMError** will be raise if the user_callback is not callable or if the user_queue is not an instance of *queue.Queue()*.

---

*add(transitions)*

Add a list of transitions to the FSM. Upon parsing this list, the FSM will construct its own repository of States and Events.

---

*state()*

Return the name of the current state or "" if not current state is defined.

---

*start()*

Set the FSM on the starting point.
*has_ended* will be set to **False**.

**FSMError** will be raised if no starting point can be found in the list of states.

---

*stop()*

Set the FSM on the ending point.
*has_ended* will be set to **True**.

**FSMError** will be raised if no ending point can be found in the list of states.

---

*update(event)*

Update the FSM with the event. If the event is defined for the current state and the move is valid, the transition will occur.

**FSMError** will be raised if:

- the event is not defined for the current state
- the end state is None

---

*can(state)*

Return **True** if the FSM can move to *state* from the current state.
Return **False** otherwise.

---

*cannot(state)*

Return **True** if the FSM cannot move to *state* from the current state.
Return **False** otherwise.

---

### **FSMBuilder**

This helper class is used for creating a FSM object from a **YAML** definition.
Example:

```python
builder = FSMBuilder("myFSMDefinition.yml")
fsm_composite = builder.parse()
```

Upon successful parsing of the YAML file, a **FSMBuilderComposite** object is created.

---

*FSMBuilder(filename)*
Constructor.

**FSMBuilderError** will be raised if the file cannot be found on the filesystem.

---

*parse(event_objects=True)*

Parse the file and build the FSMBuilderComposite object.
If *event_objects* is True, the parser will map each events to a specific string within the composite object.
The string will start with 'E' and follow by an index.

*Example*:Events are defined in the YAML file in this order 'PLAY', 'PAUSE', 'STOP'.The composite object will have the properties:

- E0 that will map to 'PLAY'
- E1 that will map to 'PAUSE'
- E2 that will map to 'STOP'

**FSMBuilderError** will be raised in the following cases:

- if the YAML file is not with the correct version
- if the specific markers cannot be found in the file (see YAML file definition below)

---

### **FSMBuilderComposite**

This composite object is created when parsing a YAML file.
The properties available after creation are:

- FSM: this is the FSM object
- events: this list contains all the events found in the YAML definition
- Exxx: mapping for the events in the list (optional)

## Exceptions

### **FSMError**

This is the generic Exception raised when a problem occured in the FSM.

### **FSMBuilderError**

This is the generic Exception raised when a problem occured while building FSM from YAML file.

## YAML file definition

A set of mandatory markers should be defined in the file.

### **Version**

This indicates the minimum version of the reader to decode this file.
For now, only version **0.1.0** is supported.

### **Events**

The list of events defined for this FSM

### **States**

The list of states defined for this FSM.
The properties defined for a state are:

- name (MANDATORY): a unique name for this state
- type (OPTIONAL): the type of this state (BEGIN, NORMAL, END) or NORMAL by default
- enter (OPTIONAL): the action string when entering this state
- exit (OPTIONAL): the action string when leaving this state

### **Transitions**

The list of transitions for this FSM.
Each transition should have:

- event (MANDATORY): the name of the event as defined in Events
- begin (MANDATORY): the name of the begining state
- end (MANDATORY): the name of the ending state

### **Example:**

```yaml
# define the version
Version: 1.0.0

# define some events
Events:
  - E.PLAY
  - E.PAUSE
  - E.STOP

# define some states
States:
  - name: S.PLAY
    type: BEGIN
    enter: "play"
    exit: ""
  - name: S.PAUSE
    type: NORMAL
    enter: "pause"
  - name: S.STOP
    type: END
    enter: "stop"

# define some transitions
Transitions:
  - event: E.PAUSE
    begin: S.PLAY
    end: S.PAUSE
  - event: E.PAUSE
    begin: S.PAUSE
    end: S.PAUSE

  - event: E.PLAY
    begin: S.PAUSE
    end: S.PLAY
  - event: E.PLAY
    begin: S.PLAY
    end: S.PLAY

  - event: E.STOP
    begin: S.PLAY
    end: S.STOP
  - event: E.STOP
    begin: S.PAUSE
    end: S.STOP
  - event: E.STOP
    begin: S.STOP
    end: S.STOP
```

## License

`pyfsm` is distributed under the terms of the [Apache 2.0](https://opensource.org/license/apache-2-0) license.
