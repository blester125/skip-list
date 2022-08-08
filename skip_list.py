"""A toy skiplist implementation.

The most important part of this implementation is the

```python
x = self.head
for i in range(self.level, -1, -1):
  while True:
    if x.next.get(i) is None or k < x.next[i].pair.key:
      break
```

We begin by looping through the levels of the skip list, starting at the
top-most level as it is the sparsist. We when hit the end of that list (or a
key that is larger than our key value), we know that our key is not at this
level but is one level down. So we break out of the while loop (which is what is
iterating through the list at some level) and the for loop drops us down one
level. Critically, the current node `x` is not reset, this means we are still
looking at the same node, just at a deeper level. This means that we get to
skip looking at all the nodes that come before `x` at this level. It is ok to
skip these nodes as we know that our key is greater than `x` and because the
list is ordered, everything before `x` is smaller than `x` and therefore smaller
than our key and can be ignored.
"""

import dataclasses
import random
from typing import Any, Optional, Protocol, TypeVar, Dict

class _Orderable(Protocol):
  def __lt__(self, other) -> bool: ...
Orderable = TypeVar("Orderable", bound=_Orderable)

K = Orderable
V = Any


@dataclasses.dataclass
class Pair:
  """Key value pair to store in the SkipList"""
  key: K
  value: V


@dataclasses.dataclass
class SkipNode:
  """A node in the skiplist."""
  pair: Pair
  next: Dict[int, 'SkipNpde']  # The max key value is the node's level.

  @property
  def level(self) -> int:
    return max(self.next.keys())


@dataclasses.dataclass
class SkipList:
  """Skiplist.

  A probablistic data structure that essentially adds binary search to an
  ordered linked list. The skip list can be through of as stacked, ordered
  linked lists where we try to have each list be about half as sparse as the
  list below it. Each node is present in all lists below it.
  """

  head: SkipNode
  level: int
  size: int

  def __len__(self):
    """The length of the list is tracked with size."""
    return self.size

  def __getitem__(self, k: K) -> V:
    x = self.head

    # Search each level starting from the top
    for i in range(self.level, -1, -1):
      # Most important part of this loop is that when we break from the while
      # loop over the linked list, we will drop down a level (from the for loop)
      # but we don't reset `x` so we are looking at the same node, just at a
      # lower level. This means we get to skip looking at any node before `x`
      # at this new level.
      while True:
        # Iterate through the LL at this level, If we hit the end (or find a key
        # that is larger than ours) we know we aren't in this level.
        if x.next.get(i) is None or k < x.next[i].pair.key:
          break
        # If we find our key, return the value. x.next[i] is defined because
        # otherwise we would have broken above
        elif x.next[i].pair.key == k:
          return x.next[i].pair.value
        # Otherwise move to the next entry. We know this entry will have a next
        # list long enough to be indexed by this level `i` as we are only
        # looking at the next node at this level.
        else:
          x = x.next[i]
    # If we didn't find the key, raise an error.
    raise KeyError(k)

  # This isn't a staticmethod to make overriding this method easier.
  def get_level(self) -> int:
    """Select a random level to insert the new node at. P_L = 2^(-L + 1)."""
    level = 0
    # Make it less likely to get a higher level.
    while random.choice([True, False]):
      level += 1
    return level

  def insert(self, key: K, value: V) -> 'SkipList':
    # Get the level we add the new node at.
    new_level = self.get_level()

    # If our new level is more that we have seen before, add None pointers to
    # head node.
    if new_level > self.level:
      self.level = new_level

    # Create a new node to hold K and V, it will be inserted at the newly
    # choosen level,
    new_node = SkipNode(Pair(key, value), {})
    x = self.head

    # We need to insert the new node into the linked list at each level.
    for i in range(new_level, -1, -1):
      # Most important part of this loop is that when we break from the while
      # loop over the linked list, we will drop down a level (from the for loop)
      # but we don't reset `x` so we are looking at the same node, just at a
      # lower level. This means we get to skip looking at any node before `x`
      # at this new level.
      #
      # Iterate through the until we hit the end or find a key that is less than
      # what we are inserting.
      while x.next.get(i) is not None and x.next[i].pair.key < key:
        x = x.next[i]
      # If we hit the end, x.next.get(i) is None and we are the largest key at
      # this level. Set our next value to None (making us the end of the list)
      # and set the pervious last node to point to us. In the other case
      # x.next[i] is just a node and we do the same sort of setting.
      new_node.next[i] = x.next.get(i)
      x.next[i] = new_node

    self.size += 1
    return self

  def delete(self, key: K) -> 'SkipList':
    x = self.head
    # Track if we deleted the key so we know if we should decrease the size.
    deleted = False

    # Start searching from the top level
    for i in range(self.level, -1, -1):
      # Most important part of this loop is that when we break from the while
      # loop over the linked list, we will drop down a level (from the for loop)
      # but we don't reset `x` so we are looking at the same node, just at a
      # lower level. This means we get to skip looking at any node before `x`
      # at this new level.
      while True:
        # Iterate through until we find hit the end of the list or we find a key
        # larget than us, this means we need to go down a level.
        if x.next.get(i) is None or key < x.next[i].pair.key:
          break
        # If we find the next node is the key to delete, we delete it by moving
        # our next pointer to the one after that. Then in the next loop, the
        # next node will have a key that is larger than ours and we will break,
        # making us go to the next level down where we will find our key again.
        # x.next[i] is safe to access because if it was not there we would have
        # broken before.
        elif x.next[i].pair.key == key:
          deleted = True
          x.next[i] = x.next[i].next.get(i)
        # Move on if need be
        else:
          x = x.next[i]

    # We deleted a key, so make the size smaller.
    if deleted:
      self.size -= 1

    return self

  def __str__(self) -> str:
    """Print the skip list on a grid to show the skips better."""
    # Track which column a key will appear in the grid
    location = {}
    rows = []
    # Track the longest string representation of a key to make the grid even.
    max_len = 0
    # We know there will be self.level rows in the grid
    # Start at the bottom as it will have every key and sets locations for
    # higher levels.
    for i in range(self.level + 1):
      # We know there will be self.size columns in the grid.
      row = [None for _ in range(self.size)]
      x = self.head.next[i]
      # Track the current column.
      j = 0
      # Iterate until we hit the end of the list
      while x is not None:
        # Get the saved location if possible, otherwise get the current count
        j = location.get(x.pair.key, j)
        # Save the column number of this key.
        location[x.pair.key] = j
        # Place the key in the grid, according to the column, this places higher
        # level keys in the right columns,
        row[location[x.pair.key]] = x.pair.key
        # If this has the longest string representation, update it
        if (l := len(str(x.pair.key))) > max_len:
          max_len = l
        # Move to the next node (or None at the end) and update the column.
        x = x.next.get(i)
        j += 1
      rows.append(row)

    def _format_key(key: Optional[K], max_len: int) -> str:
      if key is not None:
        return f"-> {key:>{max_len}}"
      return "   " + " " * max_len

    # format the grid
    lines = []
    # Iterate through the levels backwards (so zero is last).
    for i, row in reversed(list(enumerate(rows))):
      rs = " ".join(_format_key(r, max_len) for r in row)
      lines.append(f"{i}: {rs}")
    return "\n".join(lines)


# Simple demo.
if __name__ == "__main__":
  from skip_list_test import make_example_list

  skiplist = make_example_list()

  print(skiplist)
  print(f"Size: {len(skiplist)}")
  print("=" * 80)

  print(f"Found {skiplist[7]} with key 7")
  print(f"Found {skiplist[15]} with key 15")
  print(f"Found {skiplist[5]} with key 5")

  skiplist = skiplist.delete(15)
  print(skiplist)
  print(f"Size: {len(skiplist)}")
  print("=" * 80)

  skiplist = skiplist.insert(14, 14)
  print(skiplist)
  print(f"Size: {len(skiplist)}")
  print("=" * 80)

  skiplist = skiplist.delete(7)
  print(skiplist)
  print(f"Size: {len(skiplist)}")
  print("=" * 80)

  skiplist = skiplist.delete(24)
  print(skiplist)
  print(f"Size: {len(skiplist)}")
