#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from Quoridor.VPNetModel import TictactoePolicyValueNet
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
    act_visits = [[2, 3], [4, 5], [6, 7]]
    acts, visits = zip(*act_visits)
    PVN = TictactoePolicyValueNet(7)
    # PVN = QuoridorPolicyValueNet(7)
    T1 = Train(PVN)

    MCT = MCTSearch(PVN.policy_value_fn, Num_Simulation=2)
    Root = Quoridor.MCTS.MonteCartoTreeNode(-1, np.zeros((4, 7*7)))
    InitChessBoard = RE.ChessBoard()
    Winner, Data_Collect = MCT.SelfPlay(0, True)

    # MCT.OnceSimulation(Root, InitChessBoard, 1)


    T1.run()

    print("训练完成!")
    a = input()


main()
