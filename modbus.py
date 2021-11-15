from datetime import datetime
import gym
import numpy as np
from scapy.all import rdpcap

class MudbusEnv(gym.Env):

    def __init__(self, path, episode_length, input_ip, output_ip, displacement):
        self.input_alphabet, self.output_alphabet, self.inputs, self.outputs = \
            self.get_modbus_data(path, input_ip, output_ip, displacement)
        self.outputs = self.outputs
        # self.action_space = len(self.output_alphabet) + 1
        # self.observation_space = len(self.input_alphabet)
        self.action_space = gym.spaces.Discrete(13)
        self.observation_space = gym.spaces.Discrete(327)
        self.count = 0
        self.state = self.inputs[0]
        self.episode_length = episode_length
        self.reset_next_step = False
        self.success = 0
        self.timestamp = None
        self.epochs_count = 0
        self.model = None
        self.test_env = None

    def test_agent(self):
        succsess_predicts = 0
        end = min(len(self.outputs), len(self.outputs)) - 1
        obs = self.inputs[self.episode_length:4000]
        c = 0
        for i in range(len(obs)):
            c += 1
            action, _states = self.model.predict(obs[i])
            if action == self.outputs[self.episode_length + i]:
                succsess_predicts += 1
        print('ПРОВЕРКА НА ТЕСТОВЫХ ДАННЫХ: {0:.3f}%'.format(succsess_predicts / c * 100))

    def step(self, action):
        # if self.reset_next_step:
        # return self.reset()
        if self.timestamp is None:
            self.timestamp = datetime.now()
        reward = -1.
        done = False
        if self.count != self.episode_length:
            if self.outputs[self.count] == action:
                reward = 1.
                self.success += 1
            self.state = self.inputs[self.count]
        else:
            if self.epochs_count % 100 == 0:
                ep_time = datetime.now() - self.timestamp
                self.epochs_count += 1
                print('=' * 50)
                print('\n')
                print(
                    'Тест номер {0} -- точность {1:.3f}% -- время {2}'.format(self.epochs_count, self.success / self.count * 100,
                                                                         ep_time))
                print('\n')
                print('=' * 50)
            self.success = 0
            done = True
        self.count += 1
        return self.state, reward, done, {}

    def reset_time(self):
        self.timestamp = None
        self.epochs_count = 0

    def to_obs(self, num, env):
        r = np.zeros(len(self.input_alphabet), dtype='int32')
        r[int(self.inputs[num])] = 1
        return r

    def reset(self):
        self.suck = 0
        self.state = self.inputs[0]
        self.count = 0
        print('BBBBB')
        #return self.observation()
        return self.state

    def observation(self) -> np.ndarray:
        obs = np.zeros(len(self.input_alphabet), dtype='float32')
        obs[int(self.inputs[self.count])] = 1.
        return obs

    def shape(self):
        return self.outputs.shape

    def get_modbus_data(self, path, input_ip, output_ip, displacement):
        pcap = rdpcap(path)
        input_alphabet = dict()
        output_alphabet = dict()
        inputs = []
        outputs = []
        input_count = 0
        output_count = 0
        for i in pcap.res:
            new_data = i['Raw'].load[displacement:]
            if i['IP'].src == input_ip:
                if new_data not in input_alphabet.keys():
                    input_alphabet[new_data] = input_count
                    input_count += 1
                inputs.append(input_alphabet[new_data])

            elif i['IP'].src == output_ip:
                if new_data not in output_alphabet.keys():
                    output_alphabet[new_data] = output_count
                    output_count += 1
                outputs.append(output_alphabet[new_data])

        inputs = np.array(inputs, dtype="int32")
        outputs = np.array(outputs, dtype="int32")
        return input_alphabet, output_alphabet, inputs, outputs