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
# @brief	FSM Objects definition

# ----- imports
from __future__ import annotations
from typing import Any, Dict, List

from enum import Enum, auto


# ----- classes

class StateType(Enum):
    """ Supported types for all the FSM States """
    FSM_BEGIN_STATE = auto()
    FSM_NORMAL_STATE = auto()
    FSM_END_STATE = auto()

class State:
    """ Definition of a FSM State """
    def __init__(self, name: str, state_type: StateType, enter_action: str = "", exit_action: str = "") -> None:
        """ Constructor

        Args:
            name         : the name of this state
            state_type   : the type of this state
            enter_action : action to performed when entering this state
            exit_action  : action to performed when exiting this state
        """
        self.name = name
        self.state_type = state_type
        self.enter_action = enter_action
        self.exit_action = exit_action

class Event:
    """Definition of a FSM event"""
    def __init__(self, name: str) -> None:
        """Constructor

        Args:
            name : name of the event
        """
        self.name = name

class Transition:
    """Definition of a FSM transition"""
    def __init__(self, event: Event, begin_state: State, end_state: State) -> None:
        """Constructor

        Args:
            event       : the event that will trigger the transition
            begin_state : the initial state of the transition
            end_state   : the final state of the transition
        """
        self.event = event
        self.begin_state = begin_state
        self.end_state = end_state

