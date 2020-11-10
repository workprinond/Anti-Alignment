#Standard implementation of longest common subsequence usinf dynamic programming
from ipython_genutils.py3compat import xrange
from distance_metrics.distance_interface import DistanceMetricInterface


class LongestCommonSubsequence(DistanceMetricInterface):
    def longestcommonsubsequence(A, B):

        x = len(A)
        y = len(B)

        P = [[None] * (y + 1) for i in xrange(x + 1)]

        for i in range(x + 1):
            for j in range(y + 1):
                if i == 0 or j == 0:
                    P[i][j] = 0
                elif A[i - 1] == B[j - 1]:
                    P[i][j] = P[i - 1][j - 1] + 1
                else:
                    P[i][j] = max(P[i - 1][j], P[i][j - 1])

        return P[x][y]