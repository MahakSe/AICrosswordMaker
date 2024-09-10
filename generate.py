import sys
from collections import deque

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for var in self.crossword.variables:
            # Create a list of words to remove (those that don't match the variable's length)
            invalid_words = [word for word in self.domains[var] if len(word) != var.length]

            for word in invalid_words:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        # If there is no overlap, no revision is necessary
        if overlap is None:
            return False

        to_remove = []
        i, j = overlap

        for x_word in self.domains[x]:
            # Check if there is any value in y's domain that satisfies the overlap constraint
            if not any(x_word[i] == y_word[j] for y_word in self.domains[y]):
                to_remove.append(x_word)

        for word in to_remove:
            self.domains[x].remove(word)
            revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs is None, start with an initial queue of all the arcs in the problem
        if arcs is None:
            queue = deque([(X, Y) for X in self.crossword.variables for Y in self.crossword.neighbors(X)])

        # begin with an initial queue of only the arcs that are in the list arcs
        else:
            queue = deque(arcs)

        while queue:

            # Dequeue an arc (X, Y)
            X, Y = queue.popleft()

            # Revise X's domain based on Y
            if self.revise(X, Y):
                # If X's domain is empty, no solution is possible
                if len(self.domains[X]) == 0:
                    return False

                # Add all arcs (Z, X) to the queue where Z is a neighbor of X and Z is not Y
                for Z in self.crossword.neighbors(X) - {Y}:
                    queue.append((Z, X))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if all values are distinct
        values = list(assignment.values())
        if len(values) != len(set(values)):
            return False

        # Check if every assigned value is the correct length
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # check if there are no conflicts between neighboring variables
        for var1 in assignment:
            for var2 in self.crossword.neighbors(var1):
                if var2 in assignment:
                    overlap = self.crossword.overlaps[var1, var2]
                    if overlap:
                        i, j = overlap
                        if assignment[var1][i] != assignment[var2][j]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        (least-constraining values heuristic)
        """

        def count_conflicts(word):
            """
            Count how many values this word would rule out for neighbors.
            """
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap:
                    i, j = overlap
                    for neighbor_word in self.domains[neighbor]:
                        if word[i] != neighbor_word[j]:
                            count += 1
            return count

        # Order by the number of conflicts the word causes
        return sorted(self.domains[var], key=count_conflicts)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain(minimum remaining value heuristic). If there is a tie, choose the variable with the highest
        degree (degree heuristic). If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = [
            var for var in self.crossword.variables if var not in assignment
        ]

        # Sort by (Primary Sort Criterion:) Minimum Remaining Values and (Secondary Sort Criterion) Degree heuristic
        return min(
            unassigned_vars,
            key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var)))
        )

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete, return it
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            self.ac3()

            if self.consistent(assignment):
                res = self.backtrack(assignment)
                if res is not None:
                    return res
            # If not successful, remove the variable from assignment and backtrack
            assignment.pop(var)

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
