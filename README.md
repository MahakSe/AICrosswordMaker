# Crossword Puzzle AI Generator

This project focuses on creating an AI that generates crossword puzzles using constraint satisfaction algorithms. Below is a guide to understanding, setting up, and running the project.

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Algorithms Used](#algorithms-used)
- [Usage](#usage)


## Overview
This project generates crossword puzzles by solving constraint satisfaction problems (CSP). Given a structure file and a word list, the AI fills the crossword grid with words that satisfy both unary and binary constraints. Unary constraints ensure word lengths match the slots in the grid, while binary constraints ensure overlapping words share the correct letters.

## Project Structure
- `crossword.py`: Contains the `Variable` and `Crossword` classes, used to model the crossword puzzle.
- `generate.py`: Contains the `CrosswordCreator` class, which implements the AI logic for solving the crossword puzzle.
- `data/`: Includes example structure files and word lists to test the AI.
- `output.png`: you can generate your crossword puzzle image.

## Algorithms Used

- **Constraint Satisfaction Problem (CSP)**: The core of the crossword generation uses CSP techniques to ensure that the word assignments are valid.

- **AC-3 Algorithm**: This algorithm is used to enforce arc consistency between variables, pruning invalid values from the variable domains and ensuring more efficient search.

- **Backtracking Search**: A recursive algorithm that attempts to find a solution by trying different variable assignments and backtracking when a conflict is found.

- **Heuristics**:
  - **Minimum Remaining Values (MRV)**: Chooses the next variable to assign by selecting the one with the fewest remaining legal values.
  - **Least Constraining Value (LCV)**: Orders variable assignments in a way that minimizes constraints on other variables.

## Usage
 To run the AI and generate a crossword, use the following command:

``` bash
 python generate.py data/structure1.txt data/words1.txt output.png
```
 This command will generate a crossword puzzle from the specified structure and word list, and output the result in an image file (output.png).
 If successful, the crossword will be printed in the terminal and an image will be saved.
