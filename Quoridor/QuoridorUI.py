#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import RuleEngine as RE
import LookupRoad as LR

class QuoridorGame:
    class QuoridorAction:
        def __init__(self, Action_Set = 4, Row_Set = -1, Col_set = -1):
            self.Action = Action_Set
            self.ActionLocation = RE.Point(Row_Set, Col_set)

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
    while True:
        if QG.NowPlayer == 0:  # 白子
            print("请白子输入行动指令：")
        else:
            print("请黑子输入行动指令：")

        NowQA = QuoridorGame.QuoridorAction()
        ActionStr = input()
        try:
            CMDBuff = int(ActionStr)
            NowQA.Action = CMDBuff // 100
            NowQA.ActionLocation = RE.Point((CMDBuff // 10) % 10, CMDBuff % 10)
        except:
            print("输入错误！请重新输入：")
            continue

        HintStr = RE.QuoridorRuleEngine.Action(QG.NowCB, NowQA.ActionLocation.X\
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
