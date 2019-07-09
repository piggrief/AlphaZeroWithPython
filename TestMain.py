#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from Quoridor.VPNetModel import GobangPolicyValueNet2
from Quoridor.VPNetModel import QuoridorPolicyValueNet
from Quoridor.ModelTrain import Train
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 屏蔽警告
import tensorflow as tf
import Quoridor.MCTS
from Quoridor.MCTS import MCTSearch
import numpy as np
import Quoridor.RuleEngine as RE


def main():
    PVN2 = QuoridorPolicyValueNet(7)
    T1 = Train(PVN2)

    MCT = MCTSearch(PVN2.policy_value_fn, Num_Simulation=2)
    Root = Quoridor.MCTS.MonteCartoTreeNode(-1, np.zeros((4, 7*7)))
    InitChessBoard = RE.ChessBoard()
    MCT.OnceSimulation(Root, InitChessBoard, 1)


    T1.run()

    print("训练完成!")
    a = input()


main()
