#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from LookupRoad import Point


class MonteCartoTreeNode:
    _N = 1
    _Q = 0
    _P = 0
    _UCT = 0
    _C = 0
    Children = []
    Father = -1
    NodePlayer = 0  # 0 代表玩家1 1 代表玩家2
    NodeAction = 4
    ActionLocation = Point(-1, -1)

    def __init__(self, FatherSet, Prior_P):
        self.Father = FatherSet
        self._N = 0
        self._Q = 0
        self._P = Prior_P

    def UpdateInfo(self, Leaf_Value):
        """
        更新当前节点的信息
        :param Leaf_Value: 叶节点胜负评分
        :return: 无
        """
        self._N += 1
        self._Q = (Leaf_Value - self._Q) / self._N

    def BackPropagation(self, Leaf_Value):
        """
        反向传播更新所有节点的信息
        :param Leaf_Value:
        :return:
        """
        if isinstance(self.Father, type(1)):
            self.BackPropagation(-Leaf_Value)
        self.UpdateInfo(Leaf_Value)

    def Expand(self):
        if self.IsLeafNode():
            #  拓展该节点
            pass

    def IsLeafNode(self):
        """
        判断是否是叶节点，即为拓展的节点
        :return: 是否
        """
        return self.Children == []


