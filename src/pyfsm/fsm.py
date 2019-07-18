# -*- coding: utf-8 -*-
# vim: filetype=python
#
# This source file is subject to the Apache License 2.0
# that is bundled with this package in the file LICENSE.txt.
# It is also available through the Internet at this address:
# https://opensource.org/licenses/Apache-2.0
#
# @author	Sebastien LEGRAND
# @license	Apache License 2.0
#
# @brief	Main file

# ----- imports
from __future__ import annotations
from typing import Any, Dict, List, Callable, Optional

import queue

from enum import Enum, auto

from .fsm_objects import (
    StateType, State, Event, Transition
)


# ----- classes
class FSMError(Exception):
    """Generic exception for the FSM"""

class FSM:
    """Main Finite State Machine Class"""

    def __init__(self) -> None:
        """Constructor"""
        self.has_ended = True                               # True when the FSM has ended
        self.states: Dict[str, Dict[str, State]] = { }      # States in this FSM
        self.current: State = None                          # current running state

        self.user_callback = None       # the user callback method
        self.user_queue = None          # the user callback queue

    def setup(self, user_callback: Callable, user_queue: queue) -> None:
        """Setup the user callback / queue

        Args:
            user_callback : the user callback method
            user_queue    : the user callback queue
        """
        if callable(user_callback):
            self.user_callback = user_callback
        else:
            raise FSMError("user_callback must be a callable object.")

        if isinstance(user_queue, queue.Queue):
            self.user_queue = user_queue
        else:
            raise FSMError("user_queue must be an instance of queue.Queue.")

    def add(self, transitions: List[Transition] | Transition) -> None:
        """Add one or more transition to the FSM

        Args:
            transitions : a transition or a list of transitions
        """
        # transform the single transition into a list
        if not isinstance(transitions, list):
            transitions = [transitions]

        for transition in transitions:
            # record the begin state in the map
            if transition.begin_state.name not in self.states:
                self.states[transition.begin_state.name] = { }
                self.states[transition.begin_state.name]['__object'] = transition.begin_state

            # record the end state in the map
            if transition.end_state.name is not None:
                if transition.end_state.name not in self.states:
                    self.states[transition.end_state.name] = { }
                    self.states[transition.end_state.name]['__object'] = transition.end_state

            # associate both states with the event
            self.states[transition.begin_state.name][transition.event.name] = transition.end_state

    def state(self) -> str:
        """Get the current state name

        Returns:
            The name of the current state or the empty string
        """
        if self.current:
            return self.current.name
        else:
            return ""

    def start(self) -> None:
        """Set the FSM on the starting state"""
        for state_name in self.states:
            state: State = self.states[state_name]['__object']

            if state.state_type == StateType.FSM_BEGIN_STATE:
                self.current = state
                self.has_ended = False
                return

        raise FSMError("FSM has no begin state.")

    def stop(self) -> None:
        """Set the FSM on the ending state"""
        for state_name in self.states:
            state: State = self.states[state_name]['__object']

            if state.state_type == StateType.FSM_END_STATE:
                self.current = state
                self.has_ended = True
                return

        raise FSMError("FSM has no end state.")

    def update(self, event: Event) -> None:
        """Update the FSM with the new event

        Args:
            event : an event that will move the FSM
        """
        def _sendUserAction(action: str):
            if action == "":
                return

            if self.user_queue is None or self.user_callback is None:
                return

            self.user_queue.put(
                lambda: self.user_callback(action)
            )

        # do nothing if the FSM has ended
        if self.has_ended:
            return

        # ensure the event is defined for the current state
        if event.name not in self.states[self.current.name]:
            raise FSMError(f"Event {event.name} is not defined for the current state {self.current.name}.")

        # check for an invalid move
        if self.states[self.current.name][event.name] is None:
            raise FSMError(f"Invalid transition for state {self.current.name} and event {event.name}.")

        # move to the new state
        _sendUserAction(self.current.exit_action)
        self.current: State = self.states[self.current.name][event.name]
        _sendUserAction(self.current.enter_action)

        # check for completeness
        if self.current.state_type == StateType.FSM_END_STATE:
            self.has_ended = True

    def can(self, state: State) -> bool:
        """Check if the state is valid from the current state

        Args:
            state : the targeted state

        Returns:
            True if the state is a valid state from the current state
        """
        for event in self.states[self.current.name]:
            # bypass the 'special' object
            if event == '__object':
                continue
            if self.states[self.current.name][event] == state:
                return True

        return False

    def cannot(self, state: State) -> bool:
        """Check if the state is not valid from the current state

        Args:
            state : the targeted state

        Returns:
            True if the state is not a valid state from the current state
        """
        for event in self.states[self.current.name]:
            # bypass the 'special' object
            if event == '__object':
                continue
            if self.states[self.current.name][event] == state:
                return False

        return True


