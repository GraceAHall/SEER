
from __future__ import annotations
from enum import Enum
from util_consts import NA_CHAR

#############
### ENUMS ###
#############

class Grade(Enum):
    NA          = 0
    G1          = 1
    G2          = 2
    G3          = 3
    G4          = 4
    T_CELL      = 5
    B_CELL      = 5
    NULL_CELL   = 5
    NK_CELL     = 5

    @classmethod
    def fromstr(cls, the_str: str) -> Grade:
        if the_str == NA_CHAR:
            return Grade.NA
        for e in Grade:
            if e.name == the_str:
                return e 
        raise ValueError

class Source(Enum):
    NA              = NA_CHAR
    CLINICAL        = 'C'
    PATHOLOGICAL    = 'P' 
    BOTH            = 'B'
    
    @classmethod
    def fromstr(cls, the_str: str) -> Source:
        for e in Source:
            if e.value == the_str:
                return e
        raise ValueError

class Behavior(Enum):
    BENIGN      = 0
    BORDERLINE  = 1
    MALIGNANT   = 2
    
    @classmethod
    def fromstr(cls, the_str: str) -> Behavior:
        for e in Behavior:
            if e.name == the_str:
                return e 
        raise ValueError

class RegionalNodes(Enum):
    NA                 = 0
    NEG                = 1
    POS_ASPIRATION     = 2
    POS_NODES          = 3
    
    @classmethod
    def fromstr(cls, the_str: str) -> RegionalNodes:
        if the_str == NA_CHAR:
            return RegionalNodes.NA
        for e in RegionalNodes:
            if e.name == the_str:
                return e 
        raise ValueError
