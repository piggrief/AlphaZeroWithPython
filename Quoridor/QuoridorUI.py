#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import RuleEngine as RE
import LookupRoad as LR
import MCTS as MT


class QuoridorGame:
    def __init__(self):
        self.NowPlayer = 0  # 白子
        self.NumBoard_P1 = 16  # 白子挡板数
        self.NumBoard_P2 = 16  # 白子挡板数
        self.NowCB = RE.ChessBoard()
        RE.ChessBoard.DrawNowChessBoard(self.NowCB)
        self.NowRuleEngine = RE.QuoridorRuleEngine()

    def ReversePlayer(self):
        """
        反转玩家
        :return: 无返回
        """
        if self.NowPlayer == 0:
            self.NowPlayer = 1
        else:
            self.NowPlayer = 0


def main():
    QG = QuoridorGame()
    Road = LR.LookupRoadAlgorithm()
    RootNode = MT.MonteCartoTreeNode(-1, 0)
    while True:
        if QG.NowPlayer == 0:  # 白子
            print("请白子输入行动指令：")
        else:
            print("请黑子输入行动指令：")

        if QG.NowPlayer == 0:  # 玩家落子
            NowQA = RE.QuoridorAction()
            ActionStr = input()
            try:
                CMDBuff = int(ActionStr)
                NowQA.Action = CMDBuff // 100
                NowQA.ActionLocation = RE.Point((CMDBuff // 10) % 10, CMDBuff % 10)
            except:
                print("输入错误！请重新输入：")
                continue
        else:  # 电脑落子
            MoveNode = RootNode.GetMCTSPolicy(QG.NowCB, QG.NowPlayer)
            NowQA.Action = MoveNode.NodeAction
            NowQA.ActionLocation = MoveNode.ActionLocation

        # region 检测挡板是否违规
        P1HintStr = RE.QuoridorRuleEngine.CheckBoard(QG.NowCB, NowQA.Action, 0
                                                     , NowQA.ActionLocation.X, NowQA.ActionLocation.Y)
        P2HintStr = RE.QuoridorRuleEngine.CheckBoard(QG.NowCB, NowQA.Action, 1
                                                     , NowQA.ActionLocation.X, NowQA.ActionLocation.Y)
        if P1HintStr == "Player1 No Board":
            if NowQA.Action == 0 or NowQA.Action == 1:
                print(P1HintStr)
            continue
        if (P1HintStr != "Player1 No Board" and P2HintStr != "Player2 No Board")\
                and (P1HintStr != "OK" or P2HintStr != "OK"):
            if P1HintStr != "OK" and P2HintStr == "OK":
                print(P1HintStr)
            elif P2HintStr != "OK" and P1HintStr == "OK":
                print(P2HintStr)
            elif P2HintStr != "OK" and P1HintStr != "OK":
                print("P1:" + P1HintStr + " P2:" + P2HintStr)
            continue

        # endregion
        HintStr = RE.QuoridorRuleEngine.Action(QG.NowCB, NowQA.ActionLocation.X
                                               , NowQA.ActionLocation.Y, NowQA.Action)

        ResultStr = RE.QuoridorRuleEngine.CheckGameResult(QG.NowCB)
        if ResultStr != "No Success":
            print(ResultStr)
            break
        if HintStr != "OK":
            print(HintStr)
            continue
        else:
            disbuff1 = Road.AstarRestart(QG.NowCB, 0, QG.NowCB.Player1Location.X, QG.NowCB.Player1Location.Y)
            disbuff2 = Road.AstarRestart(QG.NowCB, 1, QG.NowCB.Player2Location.X, QG.NowCB.Player2Location.Y)

            print("P1的最短路程：" + str(disbuff1))
            print("P2的最短路程：" + str(disbuff2))

            QG.ReversePlayer()
            RE.ChessBoard.DrawNowChessBoard(QG.NowCB)

    return 0


main()
