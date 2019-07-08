#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from collections import defaultdict, deque
import random
import numpy as np
import tensorflow as tf
import time
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 屏蔽警告


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


def main():
    PVN2 = GobangPolicyValueNet2(10)
    T1 = Train(PVN2)

    T1.run()

    print("训练完成!")
    a = input()


class PolicyValueNet:

    def policy_value(self, state_batch):
        """
        :param state_batch: 一堆棋局
        :return: 一堆动作P值和局面V值
        """
        pass

    def policy_value_fn(self, board):
        """
        论文里面的神经网络函数(p,v)=f(s)。
        :param board: 棋局
        :return: (action, probability)列表和v值
        """
        pass

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        """
        训练一下。
        :param state_batch: 输入给神经网络的数据
        :param mcts_probs: 动作概率标签
        :param winner_batch: 胜率标签
        :param lr: 学习速度
        :return: 损失函数值和熵值
        """
        pass

    def save_model(self, model_path):
        """
        保存模型。
        :param model_path: 模型保存路径
        """
        pass

    def restore_model(self, model_path):
        """
        载入模型。
        :param model_path: 模型载入路径
        """
        pass


class GobangPolicyValueNet2(PolicyValueNet):
    def __init__(self, board_width, model_file=None):
        self.board_width = board_width

        # 定义网络结构
        # 1. 输入
        self.input_states = tf.placeholder(tf.float32, shape=[None, 4, board_width, board_width], name="input_states")
        self.input_state = tf.transpose(self.input_states, [0, 2, 3, 1], name="input_state")
        # 2. 中间层
        # 2.1 卷积层
        X = tf.layers.conv2d(inputs=self.input_state, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
        X = tf.layers.batch_normalization(X, axis=3)
        X = tf.nn.relu(X)

        # 2.2 残差层
        def residual_block(input):
            X = tf.layers.conv2d(inputs=input, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
            X = tf.layers.batch_normalization(X, axis=3)
            X = tf.nn.relu(X)

            X = tf.layers.conv2d(inputs=X, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
            X = tf.layers.batch_normalization(X, axis=3)

            add = tf.add(X, input)
            return tf.nn.relu(add)

        for i in range(4):
            X = residual_block(X)
        # 3. P数组输出
        Y = tf.layers.conv2d(inputs=X, filters=2, kernel_size=[1, 1], padding="same", data_format="channels_last")
        Y = tf.layers.batch_normalization(Y, axis=3)
        Y = tf.nn.relu(Y)
        self.action_conv_flat = tf.reshape(Y, [-1, 2 * board_width * board_width], name="action_conv_flat")
        self.action_fc = tf.layers.dense(inputs=self.action_conv_flat, units=board_width * board_width,
                                         activation=tf.nn.log_softmax, name="action_fc")
        # 4. v值输出
        Y = tf.layers.conv2d(inputs=X, filters=1, kernel_size=[1, 1], padding="same", data_format="channels_last")
        Y = tf.layers.batch_normalization(Y, axis=3)
        Y = tf.nn.relu(Y)
        self.evaluation_conv_flat = tf.reshape(Y, [-1, 1 * board_width * board_width], name="evaluation_conv_flat")
        self.evaluation_fc1 = tf.layers.dense(inputs=self.evaluation_conv_flat, units=64, activation=tf.nn.relu, name="evaluation_fc1")
        self.evaluation_fc2 = tf.layers.dense(inputs=self.evaluation_fc1, units=1, activation=tf.nn.tanh, name="evaluation_fc2")

        # 定义损失函数
        # 1. v值损失函数
        self.labels = tf.placeholder(tf.float32, shape=[None, 1], name="labels")  # 标记游戏的输赢，对应self.evaluation_fc2
        self.value_loss = tf.losses.mean_squared_error(self.labels, self.evaluation_fc2)
        # 2. P数组损失函数
        self.mcts_probs = tf.placeholder(tf.float32, shape=[None, board_width * board_width], name="mcts_probs")
        self.policy_loss = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.multiply(self.mcts_probs, self.action_fc), 1)), name="policy_loss")
        # 3. L2正则项
        l2_penalty_beta = 1e-4
        vars = tf.trainable_variables()
        l2_penalty = l2_penalty_beta * tf.add_n([tf.nn.l2_loss(v) for v in vars if 'bias' not in v.name.lower()])
        # 4. 所有加起来成为损失函数
        self.loss = self.value_loss + self.policy_loss + l2_penalty

        # 计算熵值
        self.entropy = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.exp(self.action_fc) * self.action_fc, 1)), name="entropy")

        # 训练用的优化器
        self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate, name="optimizer").minimize(self.loss)

        # tensorflow的session
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())

        # 模型的存储
        self.saver = tf.train.Saver(max_to_keep=123456789)  # max_to_keep设置一个很大的值防止保存的中间模型被删除
        if model_file is not None:
            self.restore_model(model_file)

    def policy_value(self, state_batch):
        state_batch = np.array(state_batch)
        log_act_probs, value = self.session.run(
                [self.action_fc, self.evaluation_fc2],
                feed_dict={self.input_states: state_batch})
        act_probs = np.exp(log_act_probs)
        return act_probs, value

    def policy_value_fn(self, board):
        legal_moves = board.get_available_moves()
        current_state = np.ascontiguousarray(board.current_state().reshape(
                -1, 4, self.board_width, self.board_width))
        act_probs, value = self.policy_value(current_state)
        act_probs = zip(legal_moves, act_probs[0][legal_moves])
        return act_probs, value

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        winner_batch = np.reshape(winner_batch, (-1, 1))
        loss, entropy, _ = self.session.run(
                [self.loss, self.entropy, self.optimizer],
                feed_dict={self.input_states: state_batch,
                           self.mcts_probs: mcts_probs,
                           self.labels: winner_batch,
                           self.learning_rate: lr})
        return loss, entropy

    def save_model(self, model_path):
        self.saver.save(self.session, model_path)

    def restore_model(self, model_path):
        self.saver.restore(self.session, model_path)


main()
