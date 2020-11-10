from anti_alignment.distance_metrics.distance_interface import DistanceMetricInterface

"""
This is a straightforward implementation of a well-known algorithm, and thus
probably shouldn't be covered by copyright to begin with. But in case it is,
the author (Magnus Lie Hetland) has, to the extent possible under law,
dedicated all copyright and related and neighboring rights to this software
to the public domain worldwide, by distributing it under the CC0 license,
version 1.0. This software is distributed without any warranty. For more
information, see <http://creativecommons.org/publicdomain/zero/1.0>

During our research, we obtained this file in the stackoverflow post:
https://stackoverflow.com/questions/6709693/calculating-the-similarity-of-two-lists
We just deleted the main method

"""

class Levenshtein_Distance(DistanceMetricInterface):
    def get_distance(self, a, b):
        """
        counts how many replacements, deletions and insertions of symbols between two strings.

        Levenshtein’s distance (or edit distance) which In our case its needed to obtain γ projected to labeled
        transitions starting from σ. calculating (replace/add/delete) at the same cost of 1.
        for instance the word 'ababababab' and 'bababababa' are at distance 2 from each other.
        on the other hand if it was hamming distance it would be at distance 10 for the same example.
        further use the output, will be divided by the length of the greatest(len(γ), len(σ))

        :param str a: trace or anti-alignment you want to compare as a list of strings
        :param str  b: trace or anti-alignment you want to compare a to, also as a list of strings
        :return: returns distance between the provided lists, cost 1 for each operation (replace/add/delete)
        :rtype: int
        """
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n

        current = range(n + 1)
        for i in range(1, m + 1):
            previous, current = current, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete = previous[j] + 1, current[j - 1] + 1
                change = previous[j - 1]
                if a[j - 1] != b[i - 1]:
                    change = change + 1
                current[j] = min(add, delete, change)

        return current[n]
