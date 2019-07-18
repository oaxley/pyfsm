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
# @brief	FSM Builder from YAML file

# ----- imports
from __future__ import annotations
from typing import Any, Dict, List

import os
import yaml

from __about__ import __version__

from .fsm_objects import (
    StateType, State, Event, Transition
)

from .fsm import FSM


# ----- classes
class FSMBuilderError(Exception):
    """ Generic Exception class when building FSM from YAML file """

class FSMBuilderComposite(object):
    """ Composite object returned by the builder """

class FSMBuilder(object):
    """ Build a FSM from a YAML definition file """

    def __init__(self, filename: str) -> None:
        """Constructor

        Args:
            filename : the name of the YAML file
        """
        if not os.path.exists(filename):
            raise FSMBuilderError(f"Could not find the YAML file {filename}.")

        self.filename = filename
        self.events: Dict[str, Event] = {}
        self.states: Dict[str, State]= {}
        self.transitions: List[Transition] = []


    def _makeVersion(self, version: str) -> int:
        """ Create a number from a string version

        Args:
            version : a string representing a Semantic Versioning "x.y.z"

        Returns:
            An integer value that can be easily compared with another value
        """
        try:
            major, minor, patch = version.split('.')
            value = (int(major) * (2**16)) + (int(minor) * (2**8)) + int(patch)

        except ValueError:
            raise FSMBuilderError(f"Cannot parse the version (major.minor.patch) from the definition file.")

        return value


    def _buildEvents(self, events: List[str]) -> None:
        """ Build event objects from a list of name

        Args:
            events: a list containing names of the events
        """
        for event in events:
            if event in self.events:
                raise FSMBuilderError(f"Event {event} is already defined.")
            else:
                self.events[event] = Event(event)

    def _buildStates(self, states: List[Dict[str, str]]) -> None:
        """ Build state objects from a list of definition

        Args:
            states : a list containing all the states objects from the YAML definition
        """
        for state in states:
            if 'name' not in state:
                raise FSMBuilderError(f"Found a state with no name in the definition file.")

            if state['name'] in self.states:
                raise FSMBuilderError(f"Found duplicated state name {state['name']} in the defintion file.")

            if 'type' not in state:
                state_type = StateType.FSM_NORMAL_STATE
            else:
                if state['type'].lower() == 'begin':
                    state_type = StateType.FSM_BEGIN_STATE
                elif state['type'].lower() == 'end':
                    state_type = StateType.FSM_END_STATE
                else:
                    raise FSMBuilderError(f"Unknown state type <{state['type']}>")

            if 'enter' not in state:
                enter_action = ""
            else:
                enter_action = state['enter']

            if 'exit' not in state:
                exit_action = ""
            else:
                exit_action = state['exit']

            self.states[state['name']] = State(state['name'],state_type,enter_action,exit_action)

    def _buildTransitions(self, transitions: List[Dict[str, str]]) -> None:
        """Build transition objects for a list of definition

        Args:
            transitions: a list containing all the transitions object from the YAML definition
        """
        for transition in transitions:
            if 'event' not in transition:
                raise FSMBuilderError(f"Found a transition with no event associated.")
            else:
                if transition['event'] not in self.events:
                    raise FSMBuilderError(f"Cannot find event {transition['event']} in the list of defined events.")

            if 'begin' not in transition:
                raise FSMBuilderError(f"Found a transition with no begin state.")
            else:
                if transition['begin'] not in self.states:
                    raise FSMBuilderError(f"Cannot find state {transition['begin']} in the list of defined states.")

            if 'end' not in transition:
                raise FSMBuilderError(f"Found a transition with no end state.")
            else:
                if transition['end'] not in self.states:
                    raise FSMBuilderError(f"Cannot find state {transition['end']} in the list of defined states.")

            event = self.events[transition['event']]
            begin_state = self.states[transition['begin']]
            end_state = self.states[transition['end']]
            self.transitions.append(Transition(event,begin_state,end_state))

    def parse(self, event_objects=True) -> FSMBuilderComposite:
        """Parse the YAML file and return composite object with the FSM and the list of events

        Args:
            event_objects : create objects Exx corresponding to each event in the YAML definition

        Returns:
            A FSM Composite object that encapsulates the FSM and its events
        """
        with open(self.filename, 'r') as stream:
            data = yaml.load(stream, Loader=yaml.BaseLoader)

        # check the version
        if 'Version' not in data:
            raise FSMBuilderError(f"Cannot find the version in the file.")
        else:
            if self._makeVersion(__version__) < self._makeVersion(data['Version']):
                raise FSMBuilderError(f"Builder cannot parse file with version > {__version__}.")

        # build events
        if 'Events' not in data:
            raise FSMBuilderError(f"Cannot find the list of Events in {self.filename}.")
        else:
            self._buildEvents(data['Events'])

        # build states
        if 'States' not in data:
            raise FSMBuilderError(f"Cannot find the list of States in {self.filename}.")
        else:
            self._buildStates(data['States'])

        # build transitions
        if 'Transitions' not in data:
            raise FSMBuilderError(f"Cannot find the list of Transitions in {self.filename}.")
        else:
            self._buildTransitions(data['Transitions'])

        # create the FSM
        obj = FSMBuilderComposite()
        obj.FSM = FSM()
        obj.FSM.add(self.transitions)

        # set the events
        obj.events = data['Events']

        # create syntaxic sugar strings for events
        if event_objects:
            count = 0
            for event in data['Events']:
                setattr(obj, f"E{count}", event)
                count = count + 1

        return obj