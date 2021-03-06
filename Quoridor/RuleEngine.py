#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import numpy as np
import copy
from LookupRoad import LookupRoadAlgorithm as LR

class Point:
    def __init__(self, X_Set=0, Y_Set=0):
        self.X = X_Set
        self.Y = Y_Set


class Grid:
    """
    棋格类
    """
    GridStatus = 0  # 0 代表棋格位位空，1代表有白子，2代表有黑子
    IfUpBoard = False  # 棋格上方是否有横挡板
    IfLeftBoard = False  # 棋格左方是否有竖挡板

    def __init__(self, GridStatus_Set=0, IfUpBoard_Set=False, IfLeftBoard_Set=False):
        """
        构造函数
        :param GridStatus_Set:格子状态
        :param IfUpBoard_Set:是否有上挡板
        :param IfLeftBoard_Set:是否有左挡板
        """
        self.GridStatus = GridStatus_Set
        self.IfUpBoard = IfUpBoard_Set
        self.IfLeftBoard = IfLeftBoard_Set
        return


class ChessBoard:
    """
    棋盘类
    """
    def __init__(self):
        """
        初始化棋盘状态
        """
        self.ChessBoardAll = np.zeros([7, 7], dtype=Grid)
        for i in range(0, self.ChessBoardAll.shape[0]):
            for j in range(0, self.ChessBoardAll.shape[1]):
                self.ChessBoardAll[i, j] = Grid()
        self.ChessBoardAll[0, 3].GridStatus = 1
        self.ChessBoardAll[6, 3].GridStatus = 2
        self.Player1Location = Point(0, 3)
        self.Player2Location = Point(6, 3)
        self.NumPlayer1Board = 16
        self.NumPlayer2Board = 16
        return

    @staticmethod
    def DrawNowChessBoard(ChessBoardNow):
        """
        绘制棋盘
        :return:
        """
        for i in range(0, ChessBoardNow.ChessBoardAll.shape[0] * 2):
            rowindex = i // 2
            for j in range(0, ChessBoardNow.ChessBoardAll.shape[1] * 2):
                colindex = j // 2
                if i % 2 == 0:  # 横档板显示行
                    if ChessBoardNow.ChessBoardAll[rowindex, colindex].IfUpBoard:
                        print("\033[31m─\033[0m", end='')
                    else:
                        print("─", end='')  # ─
                else:
                    if j % 2 == 0:  # 竖挡板显示列
                        if ChessBoardNow.ChessBoardAll[rowindex, colindex].IfLeftBoard:
                            print("\033[31m|\033[0m", end='')
                        else:
                            print("|", end='')
                    else:
                        if ChessBoardNow.ChessBoardAll[rowindex, colindex].GridStatus == 1:  # 白子
                            print("⚪", end='')
                        elif ChessBoardNow.ChessBoardAll[rowindex, colindex].GridStatus == 2:  # 黑子
                            print("●", end='')
                        else:
                            print(" ", end='')
            print()
        print()

    @staticmethod
    def SaveChessBoard(ChessBoardNow):
        """
        保存棋盘至返回值
        :param ChessBoardNow: 待保存的棋盘
        :return: 保存后的棋盘
        """
        ChessBoardSave = copy.deepcopy(ChessBoardNow)
        return ChessBoardSave

    @staticmethod
    def ResumeChessBoard(ChessBoardSave):
        """
        恢复棋盘至返回值
        :param ChessBoardSave: 保存的棋盘
        :return: 待恢复的棋盘
        """
        ChessBoard_Resumed = copy.deepcopy(ChessBoardSave)
        return ChessBoard_Resumed


class QuoridorRuleEngine:
    """
    Quoridor游戏规则引擎类
    关于玩家的规定：0为P1白子，1为P2黑子
    关于动作的规定：0为放置竖挡板，1为放置横挡板，2为移动玩家1，3为移动玩家2，4为等待
    """
    def __init__(self):
        return

    @staticmethod
    def CheckGameResult(ChessBoardToCheck):
        if ChessBoardToCheck.Player1Location.X == 6:
            return "P1 Success"
        elif ChessBoardToCheck.Player2Location.X == 0:
            return "P2 Success"
        else:
            return "No Success"

    @staticmethod
    def ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction):
        if NowAction == 2:
            ChessBoard_ToCheck.Player1Location = Point(row, col)
        else:
            ChessBoard_ToCheck.Player2Location = Point(row, col)

    @staticmethod
    def CheckBoard(ChessBoard_ToCheck, WhichBoard, Player, Location_row, Location_col):
        """
        检测该挡板是否能被放下
        :param ChessBoard_ToCheck:待检测棋盘
        :param WhichBoard:放置哪种挡板
        :param Player:检测哪个玩家会被堵死
        :param Location_row:玩家的位置行
        :param Location_col:玩家的位置列
        :return:错误提示符，能被放下就会返回“OK”
        """
        ThisChessBoard = ChessBoard_ToCheck
        if WhichBoard == 2 or WhichBoard == 3:
            return "OK"
        if Player == 0 and ChessBoard_ToCheck.NumPlayer1Board <= 0:
            return "Player1 No Board"
        elif Player == 1 and ChessBoard_ToCheck.NumPlayer2Board <= 0:
            return "Player2 No Board"

        ChessBoardBuff = ChessBoard.SaveChessBoard(ThisChessBoard)

        Hint = QuoridorRuleEngine.Action(ThisChessBoard, Location_row, Location_col, WhichBoard)

        if Hint == "OK":
            AstarE = LR()
            disbuff1 = AstarE.AstarRestart(ThisChessBoard, 0
                                           , ThisChessBoard.Player1Location.X, ThisChessBoard.Player1Location.Y)
            disbuff2 = AstarE.AstarRestart(ThisChessBoard, 1
                                           , ThisChessBoard.Player2Location.X, ThisChessBoard.Player2Location.Y)

            if disbuff1 >= 999 and disbuff2 < 999:
                Hint = "Player1 No Road!"
            elif disbuff1 < 999 and disbuff2 >= 999:
                Hint = "Player2 No Road!"
            elif disbuff1 >= 999 and disbuff2 >= 999:
                Hint = "Player1&Player2 No Road!"

        if Hint != "OK":
            ThisChessBoard = ChessBoard.ResumeChessBoard(ChessBoardBuff)
            return Hint

        ThisChessBoard = ChessBoard.ResumeChessBoard(ChessBoardBuff)
        return "OK"

    @staticmethod
    def CheckMove_Change(ChessBoard_ToCheck, row, col, NowAction):
        """
        检测能否执行移动，Change代表检测成功后会执行这次移动，改变棋盘ChessBoard_ToCheck
        :param ChessBoard_ToCheck:待检测的棋盘
        :param row:移动的行
        :param col:移动的列
        :param NowAction:移动类型
        :return:移动状态提示，“OK”表示移动执行完成且成功
        """
        if ChessBoard_ToCheck.ChessBoardAll[row, col].GridStatus != 0:
            return "This Not Empty"
        ActionPlayer = 0  # 1 为玩家1，2 为玩家2
        AnotherPlayer = 0
        if NowAction != 2 and NowAction != 3:
            return "Error"

        if NowAction == 2:  # 移动玩家1
            ActionPlayer = 1
            AnotherPlayer = 2
        else:
            ActionPlayer = 2
            AnotherPlayer = 1

        ChessBoardAll = ChessBoard_ToCheck.ChessBoardAll
        # region 检测是否可走
        # region 前扫一格
        if row >= 1 and (not ChessBoardAll[row, col].IfUpBoard):  # 上扫
            if ChessBoardAll[row - 1, col].GridStatus == ActionPlayer:
                ChessBoardAll[row - 1, col].GridStatus = 0
                ChessBoardAll[row, col].GridStatus = ActionPlayer
                if NowAction == 2:
                    ChessBoard_ToCheck.Player1Location = Point(row, col)
                else:
                    ChessBoard_ToCheck.Player2Location = Point(row, col)
                return "OK"
            elif ChessBoardAll[row - 1, col].GridStatus == AnotherPlayer:
                if col >= 1 and ChessBoardAll[row - 1, col - 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row - 1, col].IfLeftBoard):  # 左扫
                    ChessBoardAll[row - 1, col - 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    if NowAction == 2:
                        ChessBoard_ToCheck.Player1Location = Point(row, col)
                    else:
                        ChessBoard_ToCheck.Player2Location = Point(row, col)
                    return "OK"
                if col <= 5 and ChessBoardAll[row - 1, col + 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row - 1, col + 1].IfLeftBoard):  # 右扫
                    ChessBoardAll[row - 1, col + 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    if NowAction == 2:
                        ChessBoard_ToCheck.Player1Location = Point(row, col)
                    else:
                        ChessBoard_ToCheck.Player2Location = Point(row, col)
                    return "OK"
                if row >= 2 and ChessBoardAll[row - 2, col].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row - 1, col].IfUpBoard):  # 上扫
                    ChessBoardAll[row - 2, col].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    if NowAction == 2:
                        ChessBoard_ToCheck.Player1Location = Point(row, col)
                    else:
                        ChessBoard_ToCheck.Player2Location = Point(row, col)
                    return "OK"
        # endregion
        if row >= 1 and (not ChessBoardAll[row, col].IfUpBoard):  # 上扫
            if ChessBoardAll[row - 1, col].GridStatus == ActionPlayer:
                ChessBoardAll[row - 1, col].GridStatus = 0
                ChessBoardAll[row, col].GridStatus = ActionPlayer
                QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                return "OK"

            elif ChessBoardAll[row - 1, col].GridStatus == AnotherPlayer:
                if col >= 1 and ChessBoardAll[row - 1, col - 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row - 1, col].IfLeftBoard):  # 左扫
                    ChessBoardAll[row - 1, col - 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if col <= 5 and ChessBoardAll[row - 1, col + 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row - 1, col + 1].IfLeftBoard):  # 右扫
                    ChessBoardAll[row - 1, col + 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if row >= 2 and ChessBoardAll[row - 2, col].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row - 1, col].IfUpBoard):  # 上扫
                    ChessBoardAll[row - 2, col].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

        if row <= 5 and (not ChessBoardAll[row + 1, col].IfUpBoard):  # 下扫
            if ChessBoardAll[row + 1, col].GridStatus == ActionPlayer:
                ChessBoardAll[row + 1, col].GridStatus = 0
                ChessBoardAll[row, col].GridStatus = ActionPlayer
                QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                return "OK"

            elif ChessBoardAll[row + 1, col].GridStatus == AnotherPlayer:
                if col >= 1 and ChessBoardAll[row + 1, col - 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row + 1, col].IfLeftBoard):  # 左扫
                    ChessBoardAll[row + 1, col - 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if col <= 5 and ChessBoardAll[row + 1, col + 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row + 1, col + 1].IfLeftBoard):  # 右扫
                    ChessBoardAll[row + 1, col + 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if row <= 4 and ChessBoardAll[row + 2, col].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row + 2, col].IfUpBoard):  # 下扫
                    ChessBoardAll[row + 2, col].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

        if col >= 1 and (not ChessBoardAll[row, col].IfLeftBoard):  # 左扫
            if ChessBoardAll[row, col - 1].GridStatus == ActionPlayer:
                ChessBoardAll[row, col - 1].GridStatus = 0
                ChessBoardAll[row, col].GridStatus = ActionPlayer
                QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                return "OK"
            elif ChessBoardAll[row, col - 1].GridStatus == AnotherPlayer:
                if col >= 2 and ChessBoardAll[row, col - 2].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row, col - 1].IfLeftBoard):  # 左扫
                    ChessBoardAll[row, col - 2].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if row <= 5 and ChessBoardAll[row + 1, col - 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row + 1, col - 1].IfUpBoard):  # 下扫
                    ChessBoardAll[row + 1, col - 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if row >= 1 and ChessBoardAll[row - 1, col - 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row, col - 1].IfUpBoard):  # 上扫
                    ChessBoardAll[row - 1, col - 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

        if col <= 5 and (not ChessBoardAll[row, col + 1].IfLeftBoard):  # 右扫
            if ChessBoardAll[row, col + 1].GridStatus == ActionPlayer:
                ChessBoardAll[row, col + 1].GridStatus = 0
                ChessBoardAll[row, col].GridStatus = ActionPlayer
                QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                return "OK"

            elif ChessBoardAll[row, col + 1].GridStatus == AnotherPlayer:
                if col <= 4 and ChessBoardAll[row, col + 2].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row, col + 2].IfLeftBoard):  # 右扫
                    ChessBoardAll[row, col + 2].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if row <= 5 and ChessBoardAll[row + 1, col + 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row + 1, col + 1].IfUpBoard):  # 下扫
                    ChessBoardAll[row + 1, col + 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"

                if row >= 1 and ChessBoardAll[row - 1, col + 1].GridStatus == ActionPlayer and \
                        (not ChessBoardAll[row, col + 1].IfUpBoard):  # 上扫
                    ChessBoardAll[row - 1, col + 1].GridStatus = 0
                    ChessBoardAll[row, col].GridStatus = ActionPlayer
                    QuoridorRuleEngine.ChangeP1P2Location(ChessBoard_ToCheck, row, col, NowAction)
                    return "OK"
        # endregion
        return "MoveError"

    @staticmethod
    def Action(ChessBoard, row, col, NowAction):
        """
        行动操作，主要是用来改变棋盘状态数组
        :param ChessBoard:待行动的棋盘状态
        :param row:行动的行
        :param col:行动的列
        :param NowAction:行动操作
        :return:行动结果，可不可行,"OK"代表行动成功
        """
        ChessBoard_ToAction = ChessBoard.ChessBoardAll
        if NowAction == 0:  # 放置竖挡板
            if col <= 0 or col >= 7 or row >= 6:
                return "VerticalBoardPlaceError!"
            if ChessBoard_ToAction[row, col].IfLeftBoard or ChessBoard_ToAction[row + 1, col].IfLeftBoard:
                return "This has a VerticalBoard!"
            if ChessBoard_ToAction[row + 1, col].IfUpBoard and ChessBoard_ToAction[row + 1, col - 1].IfUpBoard:
                return "十字交叉违规！"
            ChessBoard_ToAction[row, col].IfLeftBoard = True
            ChessBoard_ToAction[row + 1, col].IfLeftBoard = True
            return "OK"
        elif NowAction == 1:  # 放置横挡板
            if row <= 0 or row >= 7 or col >= 6:
                return "HorizontalBoardPlaceError!"
            if ChessBoard_ToAction[row, col].IfUpBoard or ChessBoard_ToAction[row, col + 1].IfUpBoard:
                return "This has a HorizontalBoard!"
            if ChessBoard_ToAction[row, col + 1].IfLeftBoard and ChessBoard_ToAction[row - 1, col + 1].IfLeftBoard:
                return "十字交叉违规！"
            ChessBoard_ToAction[row, col].IfUpBoard = True
            ChessBoard_ToAction[row, col + 1].IfUpBoard = True
            return "OK"
        elif NowAction == 2:  # 移动玩家1
            return QuoridorRuleEngine.CheckMove_Change(ChessBoard, row, col, 2)
        elif NowAction == 3:  # 移动玩家2
            return QuoridorRuleEngine.CheckMove_Change(ChessBoard, row, col, 3)
        else:
            return "Error"

