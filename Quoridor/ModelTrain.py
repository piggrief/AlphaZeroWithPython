#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from collections import defaultdict, deque
import random
import time
import numpy as np


class Train:

    def __init__(self, policy_value_net, save_dir="D://",
                 learn_rate=2e-4,
                 temp=1.0,
                 n_playout=300,
                 c_puct=5,
                 buffer_size=10000,
                 batch_size=3,
                 epochs=3,
                 check_freq=1,
                 play_batch_size=1,
                 game_batch_num=1):
        self.policy_value_net = policy_value_net
        self.save_dir = save_dir

        self.learn_rate = learn_rate  # 学习速率
        self.temp = temp  # 论文里面的温度值
        self.n_playout = n_playout  # 每步的蒙特卡洛搜索次数
        self.c_puct = c_puct  # 论文里面的c_puct。一个在范围(0, inf)的数字，控制探索等级。值越小越依赖于Q值，值越大越依赖于P值
        self.data_buffer = deque(maxlen=buffer_size)
        self.batch_size = batch_size  # 训练参数
        self.epochs = epochs  # 每次更新执行train_steps的次数
        self.check_freq = check_freq  # 每玩多少批次就保存
        self.play_batch_size = play_batch_size  # 每批次游戏有多少局
        self.game_batch_num = game_batch_num  # 总共玩多少批次游戏

        self.lr_multiplier = 1.0  # 根据KL调整学习速率
        self.kl_targ = 0.02

    def Collect_SelfPlay_Data(self, n=3):
        statebuff = np.zeros((4, 10, 10))
        probbuff = np.zeros((10 * 10))
        for i in range(0, 10):
            for j in range(0, 10):
                statebuff[0, i, j] = 0.0
                statebuff[1, i, j] = 1.0
                statebuff[2, i, j] = 2.0
                statebuff[3, i, j] = 3.0
                probbuff[i * 10 + j] = 0.01 * (i * 10 + j)
        state = []
        probs = []
        for i in range(n):
            state.append(statebuff)
            probs.append(probbuff)

        state = np.array(state)

        winners_z = [1, -1, 1]

        Batch = zip(state, probs, winners_z)

        Batch = list(Batch)[:]

        self.epochs = 3

        for i in range(0, n):
            self.data_buffer.extend(Batch)

    def policy_update(self):
        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch = [data[0] for data in mini_batch]
        mcts_probs_batch = [data[1] for data in mini_batch]
        winner_batch = [data[2] for data in mini_batch]
        old_probs, old_v = self.policy_value_net.policy_value(state_batch)
        for i in range(self.epochs):
            loss, entropy = self.policy_value_net.train_step(state_batch, mcts_probs_batch, winner_batch,
                                                             self.learn_rate * self.lr_multiplier)
            new_probs, new_v = self.policy_value_net.policy_value(state_batch)
            kl = np.mean(np.sum(old_probs * (np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)), axis=1))
            if kl > self.kl_targ * 4:  # D_KL偏离太远
                break
            # 调整学习速率
        if kl > self.kl_targ * 2 and self.lr_multiplier > 0.01:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_targ / 2 and self.lr_multiplier < 100:
            self.lr_multiplier *= 1.5

        explained_var_old = (1 - np.var(np.array(winner_batch) - old_v.flatten()) / np.var(np.array(winner_batch)))
        explained_var_new = (1 - np.var(np.array(winner_batch) - new_v.flatten()) / np.var(np.array(winner_batch)))
        print(
            "loss={}, entropy={}, kl={:.5f}, lr_multiplier={:.3f}, explained_var_old={:.3f}, explained_var_new={:.3f}".format
            (loss, entropy, kl, self.lr_multiplier, explained_var_old, explained_var_new))
        return loss, entropy

    def run(self):
        try:
            start_time = time.time()
            for i in range(self.game_batch_num):
                self.Collect_SelfPlay_Data()
                print("batch_i={}, episode_len={}".format(i + 1, self.epochs))
                #if len(self.data_buffer) > self.batch_size:
                loss, entropy = self.policy_update()
                if (i+1) % self.check_freq == 0:
                    print("save model " + str(i+1))
                    save_dir = self.save_dir + "/" + str(i+1)
                    # self.policy_value_net.save_model(save_dir + "/policy_value_net.model")
                    print("用时：", end='')
                    print(time.time()-start_time)
                    # print("loss：", end='')
                    # print(loss)
                    # print("entropy：", end='')
                    # print(entropy)
        except KeyboardInterrupt:
            print('\n\rKeyboardInterrupt!退出！')
