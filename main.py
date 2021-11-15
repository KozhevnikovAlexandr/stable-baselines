import tensorflow as tf
import gym

from stable_baselines import ACKTR
from modbus import MudbusEnv
from stable_baselines.common.policies import LstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv


class CustomLSTMPolicy(LstmPolicy):
    def __init__(self, sess, ob_space, ac_space, n_env, n_steps, n_batch, n_lstm=64, reuse=False, **_kwargs):
        super().__init__(sess, ob_space, ac_space, n_env, n_steps, n_batch, n_lstm, reuse,
                         net_arch=[8, 'lstm', dict(vf=[5, 10], pi=[10])],
                         layer_norm=True, feature_extraction="mlp", **_kwargs)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #mudbus_env = MudbusEnv('modbus_clever_office_131-218_full_bad(2).pcap', 3000, '192.168.12.131', '192.168.252.218', 6)
    n_cpu = 1
    env = DummyVecEnv([lambda: MudbusEnv('modbus_clever_office_131-218_full_bad(2).pcap', 3000,
                                         '192.168.12.131', '192.168.252.218', 6) for i in range(n_cpu) for i in
                       range(n_cpu)])
    model = ACKTR(CustomLSTMPolicy, env, verbose=1)
    env.envs[0].model = model
    env.envs[0].test_env = env
    model.learn(total_timesteps=25000)
    model.save("a2c_cartpole")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
