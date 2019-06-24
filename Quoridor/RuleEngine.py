#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import numpy as np
import copy


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
        self.ChessBoardAll = np.empty([7, 7], dtype=Grid)
        for x in np.nditer(self.ChessBoardAll, order='C'):
            x = Grid(self)
        self.ChessBoardAll[0, 3].GridStatus = 1
        self.ChessBoardAll[6, 3].GridStatus = 1
        self.Player1Location = Point(self, -1, -1)
        self.Player2Location = Point(self, -1, -1)
        self.NumPlayer1Board = 16
        self.NumPlayer2Board = 16
        return

    @staticmethod
    def DrawNowChessBoard(ChessBoardNow):
        """
        绘制棋盘
        :return:
        """

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

