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
import time
import multiprocessing as mp


def DataCollectShow(Data_Collect):
    StateList = list(Data_Collect)[:]
    for i in range(len(StateList)):
        StateBuff = list(StateList[i])
        StateBuff = list(StateBuff[0])
        StateBuff = np.array(StateBuff)
        RE.ChessBoard.DrawChessBoardState(StateBuff)
        time.sleep(0.5)


def PrintInfo(index):
    print("第"+str(index)+"个进程开始！")
    for i in range(200000):
        sum += 1
    print("第" + str(index) + "个进程结束！")


if __name__ == '__main__':
    PVN = TictactoePolicyValueNet(7)
    # PVN = QuoridorPolicyValueNet(7)
    T1 = Train(PVN)

    # MCT = MCTSearch(PVN.policy_value_fn, Num_Simulation=1)
    # Root = Quoridor.MCTS.MonteCartoTreeNode(-1, np.zeros((4, 7*7)))
    # InitChessBoard = RE.ChessBoard()
    # Winner, Data_Collect = MCT.SelfPlay(0, True, temp=0.1)
    # DataCollectShow(Data_Collect)

    # MCT.OnceSimulation(Root, InitChessBoard, 1)

    T1.run()

    print("训练完成!")
    a = input()
