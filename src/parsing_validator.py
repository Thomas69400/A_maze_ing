"""Parsing validator for maze configuration.

This module defines ParsingValidator which ensures the maze dimensions,
entry and exit coordinates, and perfection flag meet expected constraints.
All validators include English docstrings and precise type annotations.
"""

from __future__ import annotations
from typing import Tuple, Optional, Type
from pydantic import BaseModel, field_validator, ValidationInfo


class ParsingValidator(BaseModel):
    """Validate parsed maze configuration data.

    This Pydantic model validates maze configuration by ensuring that
    all required fields meet their respective constraints. It performs
    cross-field validation to guarantee consistency between dimensions
    and entry/exit points.

    Attributes:
        width: Maze width in cells (must be positive).
        height: Maze height in cells (must be positive).
        entry_point: Coordinates (row, col) of the maze entry point.
        exit_point: Coordinates (row, col) of the maze exit point.
        perfect: Whether the maze is perfect (no loops).
        output_file: Path to the output file for maze data.
    """

    width: int
    height: int
    entry_point: Tuple[int, int]
    exit_point: Tuple[int, int]
    perfect: bool
    output_file: str

    @field_validator("perfect")
    @classmethod
    def check_perfect(cls: Type[ParsingValidator], v: bool) -> bool:
        """Validate that the perfect field is a boolean.

        Ensures the 'perfect' field is explicitly a boolean value,
        preventing invalid types that could cause logic errors in maze
        generation.

        Args:
            v: The value to validate for the perfect field.

        Returns:
            The validated boolean value.

        Raises:
            ValueError: If the value is not a boolean.
        """
        if v != "true" and v != "false" and not isinstance(v, bool):
            raise ValueError("perfect must be a boolean")
        return v

    @field_validator("width", "height")
    @classmethod
    def check_positive(cls: Type[ParsingValidator], v: int) -> int:
        """Validate that width and height are positive integers.

        Ensures maze dimensions are strictly positive values greater
        than zero.

        Args:
            v: The value to validate (width or height).

        Returns:
            The validated positive integer.

        Raises:
            ValueError: If the value is not strictly positive.
        """

        if v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("entry_point", "exit_point")
    @classmethod
    def check_non_negative_coordinates(
        cls: Type[ParsingValidator],
        v: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Validate that coordinates are non-negative integers.

        Ensures both row and column coordinates are not negative,
        allowing (0, 0) as the minimum valid coordinate.

        Args:
            v: Coordinate tuple (row, col) to validate.

        Returns:
            The validated coordinate tuple.

        Raises:
            ValueError: If any coordinate is negative.
        """

        if v[0] < 0 or v[1] < 0:
            raise ValueError("coordinates must be non-negative")
        return v

    @field_validator("exit_point")
    @classmethod
    def check_different_points(
        cls: Type[ParsingValidator],
        v: Tuple[int, int],
        values: ValidationInfo,
    ) -> Tuple[int, int]:
        """Validate that entry and exit points are different.

        Ensures the exit point differs from the entry point to create
        a valid maze with distinct start and end locations.
        Uses ValidationInfo to access previously validated fields.

        Args:
            v: The exit_point coordinate tuple to validate.
            values: ValidationInfo object containing other field values.

        Returns:
            The validated exit_point coordinate tuple.

        Raises:
            ValueError: If exit_point equals entry_point.
        """

        entry_point: Optional[Tuple[int, int]] = (
            values.data.get("entry_point"))
        if entry_point and v == entry_point:
            raise ValueError(
                "ENTRY and EXIT points must be different")
        return v

    @field_validator("entry_point", "exit_point")
    @classmethod
    def check_within_bounds(
        cls: Type[ParsingValidator],
        v: Tuple[int, int],
        values: ValidationInfo,
    ) -> Tuple[int, int]:
        """Validate that coordinates are within maze bounds.

        Ensures both entry and exit points have coordinates that fall
        within the valid range [0, width) and [0, height) respectively.

        Args:
            v: Coordinate tuple (row, col) to validate.
            values: ValidationInfo object containing width and height.

        Returns:
            The validated coordinate tuple.

        Raises:
            ValueError: If any coordinate lies outside valid bounds.
        """

        width: Optional[int] = values.data.get("width")
        height: Optional[int] = values.data.get("height")
        if width is None or height is None:
            return v
        if v[1] >= width or v[0] >= height:
            raise ValueError(
                "coordinates must be within maze bounds")
        return v

    @field_validator("output_file")
    @classmethod
    def check_output_file(
        cls: Type[ParsingValidator],
        v: str,
    ) -> str:
        """Validate that output file path is a non-empty string.

        Ensures the output file path is provided and not empty to
        prevent errors during file writing operations.

        Args:
            v: The output file path string to validate.

        Returns:
            The validated non-empty output file path.

        Raises:
            ValueError: If output_file is an empty string.
        """

        if not v:
            raise ValueError("output_file must not be empty")
        return v

    @field_validator("height", "width")
    @classmethod
    def check_dimensions(cls: Type[ParsingValidator], v: int) -> int:
        """Validate that dimensions are within reasonable limits.

        Ensures maze dimensions do not exceed a maximum threshold to
        prevent excessive memory usage or performance issues.

        Args:
            v: The dimension value (width or height) to validate.
        Returns:
            The validated dimension value.
        Raises:
            ValueError: If the dimension exceeds the maximum allowed size.
        """

        MAX_DIMENSION: int = 120
        if v > MAX_DIMENSION:
            raise ValueError(
                f"dimensions must not exceed {MAX_DIMENSION}")
        return v
