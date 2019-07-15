#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import Quoridor.RuleEngine as RE
import numpy as np
from Quoridor.LookupRoad import Point
from Quoridor.RuleEngine import ChessBoard
import time
import concurrent.futures
import copy


class MonteCartoTreeNode:
    _N = 1
    _Q = 0
    _P = 0
    _UCT = 0
    _C = 0.01
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

    def Select(self, NowChessBoard):
        """
        Select操作
        :return:选择要去拓展的子节点
        """
        while True:
            MTNode = MonteCartoTreeNode(self, 0)
            MaxQUCT = -100
            for NodeBuff in self.Children:
                NodeBuff._UCT = self.CalNodeValue(NodeBuff)
                if MaxQUCT < NodeBuff._UCT + NodeBuff._Q:
                    MaxQUCT = NodeBuff._UCT + NodeBuff._Q
                    MTNode = NodeBuff

            JudgePlayer = self.Children[0].NodePlayer

            if MTNode.NodeAction == 0 or MTNode.NodeAction == 1:
                CheckResult = RE.QuoridorRuleEngine.CheckBoard(NowChessBoard, MTNode.NodeAction, JudgePlayer
                                                               , MTNode.ActionLocation.X, MTNode.ActionLocation.Y)
                if CheckResult != "OK":
                    self.Children.remove(MTNode)
                    continue

            break

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

    def Expand(self, Action_Priors):
        """
        根据当前局面拓展一个未拓展节点
        :param Action_Priors:当前局面可行动作评分列表
        :return:无
        """
        if self.IsLeafNode():
            #  拓展该节点
            for Action, Prob in Action_Priors:
                MTSonNode = MonteCartoTreeNode(self, 0)
                MTSonNode.NodeAction = (Action // 100) % 10
                MTSonNode.ActionLocation = Point((Action // 10) % 10, Action % 10)
                MTSonNode.NodePlayer = MonteCartoTreeNode.ReversePlayer(self.NodePlayer)
                MTSonNode._P = Prob
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

    @staticmethod
    def update_with_move(RootNode, last_move):
        MCTNodeBuff = MonteCartoTreeNode(-1, [])
        for MCTNode in RootNode.Children:
            if MCTNode.NodeAction == ((last_move // 100) % 10) \
                    and MCTNode.ActionLocation.X == ((last_move // 10) % 10)\
                    and MCTNode.ActionLocation.Y == (last_move % 10):
                MCTNodeBuff = MCTNode
                break
        RootNode = MCTNodeBuff
        return RootNode



def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


class MCTSearch:
    def __init__(self, policy_value_fn
                 , InitChessBoard=ChessBoard()
                 , JudgePlayer=0
                 , c_puct=5
                 , Num_Simulation=300
                 , IsSelfPlay=True):
        self.InitChessBoard = InitChessBoard
        self.n_Simulation = Num_Simulation  # 模拟总次数
        self.PolicyNet = policy_value_fn  # 价值策略网络
        self.C_Puct = c_puct  # 探索率C
        self.RootNode = MonteCartoTreeNode(-1, [])
        self.CurrentPlayer = JudgePlayer
        self.IsSelfPlay = IsSelfPlay

    def OnceSimulation(self, NowChessBoard, IsShowCB=False):
        """
        模拟一次,所有信息都会被保存在RootNode根节点内
        :param NowChessBoard: 初始棋盘
        :param IsShowCB: 是否显示棋盘
        :return: 无
        """
        # region 暂存挡板数量
        Board1Save = NowChessBoard.NumPlayer1Board
        Board2Save = NowChessBoard.NumPlayer2Board
        # endregion
        state = []

        # if self.RootNode.Children == []:
        #     self.RootNode.Expand(NowChessBoard)

        SimluationChessBoard = RE.ChessBoard.SaveChessBoard(NowChessBoard)

        NextExpandNode = self.RootNode

        print("一次模拟开始！")

        while True:
            StartSimTime = time.time()
            if self.RootNode.Children != []:
                SelectStart = time.time()
                # 选择
                NextExpandNode = NextExpandNode.Select(SimluationChessBoard)
                #print("Select操作用时：", end='')
                #print(time.time() - SelectStart)
                ActionStart = time.time()
                # region 模拟落子
                HintStr = RE.QuoridorRuleEngine.Action(SimluationChessBoard
                                                       , NextExpandNode.ActionLocation.X, NextExpandNode.ActionLocation.Y
                                                       , NextExpandNode.NodeAction, NextExpandNode.NodePlayer)
                #print("Action操作用时：", end='')
                #print(time.time() - SelectStart)

                if HintStr != "OK":
                    print("错误提示：")
                    RE.ChessBoard.DrawNowChessBoard(SimluationChessBoard)
                    ErrorStr = NextExpandNode.NodeAction * 100 + NextExpandNode.ActionLocation.X * 10\
                              + NextExpandNode.ActionLocation.Y
                    raise Exception(ErrorStr)

                if IsShowCB:
                    ChessBoard.DrawNowChessBoard(SimluationChessBoard)
                    time.sleep(0.5)

            # endregion
            # region 获取legal列表
            if self.RootNode.Children == []:
                QABuff = []
                CreateStartTime = time.time()
                QABuff = RE.QuoridorRuleEngine.CreateActionList(SimluationChessBoard
                                                                , MonteCartoTreeNode.ReversePlayer(NextExpandNode.NodePlayer))

                LegalActionList = []
                for QA in QABuff:
                    LegalActionList.append(QA.Action * 100 + QA.ActionLocation.X * 10 + QA.ActionLocation.Y)
            # endregion
            # print("列表创建计算时间：", end='')
            # print(time.time() - CreateStartTime)
            # region 获得P、V数组
            state.append(SimluationChessBoard.ChessBoardState)
            PolicyNetStart = time.time()
            if self.RootNode.Children != []:
                action_probs, leaf_value = self.PolicyNet(np.array(state), [])
            else:
                action_probs, leaf_value = self.PolicyNet(np.array(state), LegalActionList, True)
            #print("策略价值网络计算时间：", end='')
            #print(time.time() - PolicyNetStart)
            # endregion

            # region 只选路径最短的action
            if self.RootNode.Children != []:
                QABuff = []
                QABuff = RE.QuoridorRuleEngine.CreateMoveActionList(SimluationChessBoard
                                                                    , MonteCartoTreeNode.ReversePlayer(NextExpandNode.NodePlayer))
                NewActionList = []
                NewProbs = []
                for Action, Prob in action_probs:
                    if (Action // 100) != 2 and (Action // 100) != 3:
                        Action_X = (Action // 10) % 10
                        Action_Y = Action % 10
                        if (Action // 100) == 0:
                            if Action_Y == 0:
                                continue
                        elif (Action // 100) == 1:
                            if Action_X == 0:
                                continue
                        NewActionList.append(Action)
                        NewProbs.append(Prob)
                    elif QABuff[0].ActionLocation.X == (Action // 10) % 10 \
                            and QABuff[0].ActionLocation.Y == Action % 10 \
                            and QABuff[0].Action == (Action // 100):
                        NewActionList.append(Action)
                        NewProbs.append(Prob)
                action_probs = zip(NewActionList, NewProbs)
            # endregion

            # region 检测是否胜利
            SuccessHint = RE.QuoridorRuleEngine.CheckGameResult(SimluationChessBoard)
            if SuccessHint != "No Success":
                leaf_value = -1
                if self.CurrentPlayer == 0 and SuccessHint == "P1 Success":
                    leaf_value = 1
                if self.CurrentPlayer == 1 and SuccessHint == "P2 Success":
                    leaf_value = 1
                NextExpandNode.BackPropagation(leaf_value)
                break
            # endregion

            ExpandTime = time.time()
            # 拓展
            NextExpandNode.Expand(action_probs)
            #print("Expand用时：", end='')
            #print(time.time() - ExpandTime)

            Endtime = time.time()
            #print("一次循环用时：", end='')
            #print(Endtime - StartSimTime)

        # region 恢复挡板数量
        NowChessBoard.NumPlayer1Board = Board1Save
        NowChessBoard.NumPlayer2Board = Board2Save
        # endregion

    def GetActionProbs(self, ChessBoard_Init, temp=1e-3):
        """
        通过n_Simulation次模拟获得最终的决策动作列表及其Prob值
        :param ChessBoard_Init:
        :param temp:
        :return:
        """
        # StartTime = time.time()
        # 模拟n_Simulation次
        for i in range(self.n_Simulation):
            Sim_ChessBoard = ChessBoard.SaveChessBoard(ChessBoard_Init)
            SimStartTime = time.time()
            if Sim_ChessBoard.NumPlayer1Board <= 0 or Sim_ChessBoard.NumPlayer2Board <= 0:
                BreakPoint = 0
            self.OnceSimulation(Sim_ChessBoard, IsShowCB=False)
            SimEndTime = time.time()
            print("一次模拟时间：", end='')
            print(SimEndTime - SimStartTime)

        # EndTime = time.time()
        # print("总模拟时间：", end='')
        # print(EndTime - StartTime)
        # 计算每个动作的概率pi值
        acts = []
        _NList = []
        for MCTNode in self.RootNode.Children:
            ActionBuff = MCTNode.NodeAction * 100 + MCTNode.ActionLocation.X * 10 + MCTNode.ActionLocation.Y
            acts.append(ActionBuff)
            _NList.append(MCTNode._N)

        act_probs = softmax(1.0/temp * np.log(np.array(_NList) + 1e-10))

        return acts, act_probs

    def GetPolicyAction(self, ChessBoard_Init, temp=1e-3, return_prob=False):
        """
        获得动作可供决策的动作及其prob值
        :param ChessBoard_Init:
        :param temp:
        :param return_prob: 是否返回Prob值
        :return:
        """
        move_probs = np.zeros((4, 7 * 7))
        # self.RootNode.NodePlayer = ActionPlayer
        acts, probs = self.GetActionProbs(ChessBoard_Init, temp)

        for i in range(len(acts)):
            ActionBuff = (acts[i] // 100) % 10
            LocationBuff = (acts[i] // 10) % 10 * 7 + acts[i] % 10
            move_probs[ActionBuff, LocationBuff] = probs[i]

        if self.IsSelfPlay:
            while True:
                move = np.random.choice(acts, p=0.75 * probs + 0.25 * np.random.dirichlet(
                    0.3 * np.ones(len(probs))))  # 增加一个Dirichlet Noise来探索

                CheckResult = RE.QuoridorRuleEngine.CheckBoard(ChessBoard_Init, move // 100
                                                               , self.RootNode.Children[0].NodePlayer
                                                               , (move // 10) % 10, move % 10)
                if CheckResult != "OK":
                    for i in range(len(probs)):
                        if acts[i] == move:
                            np.delete(acts, i)
                            np.delete(probs, i)
                else:
                    break
            self.RootNode = self.RootNode.update_with_move(self.RootNode, move)
        else:
            move = np.random.choice(acts, p=probs)  # 如果用默认值temp=1e-3，就相当于选择P值最高的动作
            self.RootNode.update_with_move(self.RootNode, -1)
        if return_prob:
            return move, move_probs
        else:
            return move

    def SelfPlay(self, JudgePlayer, is_shown=False, temp=1e-3):
        self.InitChessBoard = ChessBoard()
        self.CurrentPlayer = JudgePlayer
        states, mcts_probs, current_players = [], [], []
        CurrentPlayer = 0
        self.RootNode.NodePlayer = MonteCartoTreeNode.ReversePlayer(JudgePlayer)
        StartSelfPlayTime = time.time()
        while True:
            move, move_probs = self.GetPolicyAction(self.InitChessBoard
                                                    , temp=temp, return_prob=True)
            # region 保存当前局面数据
            ToSaveStates = copy.deepcopy(self.InitChessBoard.ChessBoardState)
            states.append(ToSaveStates)
            mcts_probs.append(move_probs)
            current_players.append(copy.deepcopy(CurrentPlayer))
            # endregion

            Hint = RE.QuoridorRuleEngine.Action(self.InitChessBoard
                                                , (move // 10) % 10, move % 10, (move // 100) % 10
                                                , CurrentPlayer)

            if Hint != "OK":
                raise Exception(Hint + str(move))
            if is_shown:
                ChessBoard.DrawNowChessBoard(self.InitChessBoard)
                print("NowPlayer：", end='')
                print(CurrentPlayer, end='')
                print("NowAction：", end='')
                print(move)
                print("P1Board:", end='')
                print(self.InitChessBoard.NumPlayer1Board, end='')
                print("P2Board:", end='')
                print(self.InitChessBoard.NumPlayer2Board)

            ResultStr = RE.QuoridorRuleEngine.CheckGameResult(self.InitChessBoard)

            if ResultStr != "No Success":
                winners_z = np.zeros(len(current_players))
                WinnerPlayer = 0  # P1
                if ResultStr == "P2 Success":
                    WinnerPlayer = 1  # P2

                winners_z[np.array(current_players) == WinnerPlayer] = 1.0
                winners_z[np.array(current_players) != WinnerPlayer] = -1.0

                if 0 in winners_z:
                    ErrorStr = "winners_z有0元素"
                    raise Exception(ErrorStr)

                if is_shown:
                    print("游戏结束，获胜玩家：", WinnerPlayer)

                return WinnerPlayer, zip(states, mcts_probs, winners_z)

            CurrentPlayer = MonteCartoTreeNode.ReversePlayer(CurrentPlayer)
        print("一次自我对局用时：", end='')
        print(time.time() - StartSelfPlayTime)
        BreakPoiont = 0
