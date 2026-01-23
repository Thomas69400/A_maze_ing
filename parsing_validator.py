from __future__ import annotations
"""
parsing_validator.py

Pydantic model used to validate maze parsing results.

This module defines ParsingValidator which ensures the maze dimensions,
entry and exit coordinates, and perfection flag meet expected constraints.
All validators include English docstrings and precise type annotations.
"""

from typing import Tuple, Optional
from pydantic import (BaseModel, field_validator,
                      ValidationInfo)


class ParsingValidator(BaseModel):
    """Validate parsed maze data.

    Attributes:
        width: Maze width in cells (positive integer).
        height: Maze height in cells (positive integer).
        entry_point: Coordinates (x, y) of the maze entry.
        exit_point: Coordinates (x, y) of the maze exit.
        perfect: Whether the maze is perfect (no loops).
    """

    width: int
    height: int
    entry_point: Tuple[int, int]
    exit_point: Tuple[int, int]
    perfect: bool
    output_file: str

    @field_validator("width", "height")
    def check_positive(cls: type[ParsingValidator], v: int) -> int:
        """Ensure width and height are positive integers.

        Raises:
            ValueError: If the value is not a positive integer.
        """

        if v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("entry_point", "exit_point")
    def check_non_negative_coordinates(
        cls: type[ParsingValidator],
        v: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Ensure coordinates are non-negative.

        Raises:
            ValueError: If any coordinate is negative.
        """

        if v[0] < 0 or v[1] < 0:
            raise ValueError("coordinates must be non-negative")
        return v

    @field_validator("exit_point")
    def check_different_points(
        cls: type[ParsingValidator],
        v: Tuple[int, int],
        values: ValidationInfo,
    ) -> Tuple[int, int]:
        """Ensure entry and exit points are different.

        Uses ValidationInfo to access other field values.

        Raises:
            ValueError: If entry_point equals exit_point.
        """

        entry_point: Optional[Tuple[int, int]] = values.data.get("entry_point")
        if entry_point and v == entry_point:
            raise ValueError("ENTRY and EXIT points must be different")
        return v

    @field_validator("entry_point", "exit_point")
    def check_within_bounds(
        cls: type[ParsingValidator],
        v: Tuple[int, int],
        values: ValidationInfo,
    ) -> Tuple[int, int]:
        """Ensure coordinates are within maze bounds.

        Raises:
            ValueError: If any coordinate lies outside [0, width) or
            [0, height).
        """

        width: Optional[int] = values.data.get("width")
        height: Optional[int] = values.data.get("height")
        if width is None or height is None:
            return v
        if v[0] >= width or v[1] >= height:
            raise ValueError("coordinates must be within maze bounds")
        return v

    @field_validator("output_file")
    def check_output_file(
        cls: type[ParsingValidator],
        v: str,
    ) -> str:
        """Ensure output file path is not empty.

        Raises:
            ValueError: If output_file is an empty string.
        """

        if not v:
            raise ValueError("output_file must not be empty")
        return v
