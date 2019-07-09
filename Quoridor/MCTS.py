#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import RuleEngine as RE
import numpy as np
from LookupRoad import Point
from RuleEngine import ChessBoard


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
        self.Children = []
        self.Father = FatherSet
        self._N = 1
        self._Q = 0
        self._P = Prior_P

    def CalNodeValue(self, SonNode):
        """
        计算一个子节点的UCT或Q+u(P)值，用于Select
        :param SonNode:子节点
        :return:节点的值
        """
        # 普通UCT
        # ExploitationComponent = SonNode._Q / SonNode._N
        # ExplorationComponent = self._C * np.sqrt((np.log10(self._N) / SonNode._N))
        # UCTBuff = ExploitationComponent + ExplorationComponent
        # 带P的
        UCTBuff = self._C * SonNode._P * np.sqrt(self._N / (1 + SonNode._N))

        return UCTBuff

    def Select(self):
        """
        Select操作
        :return:选择要去拓展的子节点
        """
        MTNode = MonteCartoTreeNode(self, 0)
        MaxQUCT = -100
        for NodeBuff in self.Children:
            NodeBuff._UCT = self.CalNodeValue(NodeBuff)
            if MaxQUCT < NodeBuff._UCT + NodeBuff._Q:
                MaxQUCT = NodeBuff._UCT + NodeBuff._Q
                MTNode = NodeBuff

        return MTNode

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

    def Expand(self, ThisChessBoard):
        """
        根据当前局面拓展一个未拓展节点
        :param ThisChessBoard:当前局面棋盘
        :return:无
        """
        if self.IsLeafNode():
            #  拓展该节点
            QABuff = []
            QABuff = RE.QuoridorRuleEngine.CreateActionList(ThisChessBoard
                                                            , MonteCartoTreeNode.ReversePlayer(self.NodePlayer))
            for QA in QABuff:
                MTSonNode = MonteCartoTreeNode(self, 0)
                MTSonNode.NodeAction = QA.Action
                MTSonNode.ActionLocation = QA.ActionLocation
                MTSonNode.NodePlayer = MonteCartoTreeNode.ReversePlayer(self.NodePlayer)
                self.Children.append(MTSonNode)

    def IsLeafNode(self):
        """
        判断是否是叶节点，即为拓展的节点
        :return: 是否
        """
        return self.Children == []

    @staticmethod
    def ReversePlayer(Player):
        """
        反转玩家
        :return: 无返回
        """
        if Player == 0:
            return 1
        else:
            return 0

    def SimluationOnce(self, InitChessBoard, JudgePlayer):

        # region 暂存挡板数量
        Board1Save = InitChessBoard.NumPlayer1Board
        Board2Save = InitChessBoard.NumPlayer2Board
        # endregion

        if self.Children == []:
            self.Expand(InitChessBoard)

        SimluationChessBoard = RE.ChessBoard.SaveChessBoard(InitChessBoard)

        NextExpandNode = self

        while True:
            # 选择
            NextExpandNode = NextExpandNode.Select()

            # region 模拟落子
            HintStr = RE.QuoridorRuleEngine.Action(SimluationChessBoard
                                                   , NextExpandNode.ActionLocation.X, NextExpandNode.ActionLocation.Y
                                                   , NextExpandNode.NodeAction)

            if HintStr != "OK":
                print("错误提示：")
                RE.ChessBoard.DrawNowChessBoard(SimluationChessBoard)
                ErrorStr = NextExpandNode.NodeAction * 100 + NextExpandNode.ActionLocation.X * 10\
                          + NextExpandNode.ActionLocation.Y
                raise Exception(ErrorStr)

            if NextExpandNode.NodeAction == 0 or NextExpandNode.NodeAction == 1:
                if NextExpandNode.NodePlayer == 0:
                    SimluationChessBoard.NumPlayer1Board -= 2
                else:
                    SimluationChessBoard.NumPlayer2Board -= 2

            # endregion
            # region 检测是否胜利
            SuccessHint = RE.QuoridorRuleEngine.CheckGameResult(SimluationChessBoard)
            if SuccessHint != "No Success":
                leaf_value = -1
                if JudgePlayer == 0 and SuccessHint == "P1 Success":
                    leaf_value = 1
                if JudgePlayer == 1 and SuccessHint == "P2 Success":
                    leaf_value = 1
                NextExpandNode.BackPropagation(leaf_value)
                break
            # endregion

            # 拓展
            NextExpandNode.Expand(SimluationChessBoard)

        # region 恢复挡板数量
        InitChessBoard.NumPlayer1Board = Board1Save
        InitChessBoard.NumPlayer2Board = Board2Save
        # endregion

    def GetMCTSPolicy(self, InitChessBoard, JudgePlayer, SimulationNum=10):
        for i in range(0, SimulationNum):
            self.SimluationOnce(InitChessBoard, JudgePlayer)

        BestMoveNode = MonteCartoTreeNode(self, 0)
        MaxVisitNum = -100

        for NodeBuff in self.Children:
            if NodeBuff._N > MaxVisitNum:
                MaxVisitNum = NodeBuff._N
                BestMoveNode = NodeBuff

        return BestMoveNode


class MCTS:
    def __init__(self,policy_value_fn, c_puct=5, Num_Simulation=300):
        self.NowChessBoard = ChessBoard()
        self.NowPlayer = 0  # 玩家1
        self.n_Simulation = Num_Simulation  # 模拟总次数
        self.PolicyNet = policy_value_fn  # 价值策略网络
        self.C_Puct = c_puct  # 探索率C

    def OnceSimulation(self, RootNode, InitChessBoard, JudgePlayer):

        # region 暂存挡板数量
        Board1Save = InitChessBoard.NumPlayer1Board
        Board2Save = InitChessBoard.NumPlayer2Board
        # endregion
        state = []
        StateBuff = np.zeros((4, 7*7))
        StateBuff[2, 0, 3] = 1
        StateBuff[3, 6, 3] = 1

        if RootNode.Children == []:
            RootNode.Expand(InitChessBoard)

        SimluationChessBoard = RE.ChessBoard.SaveChessBoard(InitChessBoard)

        NextExpandNode = RootNode

        while True:
            # 选择
            NextExpandNode = NextExpandNode.Select()

            # region 模拟落子
            HintStr = RE.QuoridorRuleEngine.Action(SimluationChessBoard
                                                   , NextExpandNode.ActionLocation.X, NextExpandNode.ActionLocation.Y
                                                   , NextExpandNode.NodeAction
                                                   , StateBuff)

            if HintStr != "OK":
                print("错误提示：")
                RE.ChessBoard.DrawNowChessBoard(SimluationChessBoard)
                ErrorStr = NextExpandNode.NodeAction * 100 + NextExpandNode.ActionLocation.X * 10\
                          + NextExpandNode.ActionLocation.Y
                raise Exception(ErrorStr)

            if NextExpandNode.NodeAction == 0 or NextExpandNode.NodeAction == 1:
                if NextExpandNode.NodePlayer == 0:
                    SimluationChessBoard.NumPlayer1Board -= 2
                else:
                    SimluationChessBoard.NumPlayer2Board -= 2

            # endregion
            # region 获得P、V数组
            state.append(StateBuff)
            action_probs, leaf_value = self._policy(state)
            # endregion
            # region 检测是否胜利
            SuccessHint = RE.QuoridorRuleEngine.CheckGameResult(SimluationChessBoard)
            if SuccessHint != "No Success":
                leaf_value = -1
                if JudgePlayer == 0 and SuccessHint == "P1 Success":
                    leaf_value = 1
                if JudgePlayer == 1 and SuccessHint == "P2 Success":
                    leaf_value = 1
                NextExpandNode.BackPropagation(leaf_value)
                break
            # endregion

            # 拓展
            NextExpandNode.Expand(SimluationChessBoard)

        # region 恢复挡板数量
        InitChessBoard.NumPlayer1Board = Board1Save
        InitChessBoard.NumPlayer2Board = Board2Save
        # endregion

    def GetActionProbs(self, state, temp=1e-3):
        pass

    def GetActionList(self, ChessBoard, temp=1e-3, return_prob=False):
        move_probs = np.zeros(4, 7 * 7)



    def SelfPlay(self):
        self.NowChessBoard = ChessBoard()
        self.NowPlayer = 0
        states, mcts_probs, current_players = [], [], []
        while True:
            a = 0









