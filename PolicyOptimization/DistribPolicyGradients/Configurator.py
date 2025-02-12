from Policies import PolicyFactory
from GradientOptimization import GradientOptimizerFactory, GradientBuilder
from Agents import AgentFactory
from Experience import ExperienceReplay
from Strategy import StrategyOptimizer
from Utils import AdaptiveOmega
from PolicyOptimization.Learners import *
import Environments.Custom
import gym
import numpy as np
import random
import torch


random.seed(0)
np.random.seed(0)
torch.manual_seed(0)

def build_env(cfg, existing_env=None):
    if existing_env is None:
        env_name = cfg["env_id"].lower()
        if "rocket" in env_name:
            from Environments.Custom.RocketLeague import RLGymFactory
            env = RLGymFactory.build_rlgym_from_config(cfg)
        else:
            env = gym.make(cfg["env_id"])
    else:
        env = existing_env

    env.seed(cfg["seed"])
    env.action_space.seed(cfg["seed"])
    return env

def build_vars(cfg, existing_env=None, env_space_shapes=None):
    seed = cfg["seed"]
    cfg["rng"] = np.random.RandomState(seed)
    device = cfg["device"]
    if env_space_shapes is None:
        env = build_env(cfg, existing_env=existing_env)
    else:
        env = None

    print("Set RNG seeds to {}".format(seed))
    random.seed(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)

    experience = ExperienceReplay(cfg)
    agent = AgentFactory.get_from_cfg(cfg)

    models = PolicyFactory.get_from_cfg(cfg, env=env, env_space_shapes=env_space_shapes)
    policy = models["policy"]
    value_net = models["value_estimator"]
    policy.to(device)
    value_net.to(device)
    models.clear()

    strategy_optimizer = StrategyOptimizer(cfg, policy)
    omega = AdaptiveOmega(cfg)

    gradient_builder = GradientBuilder(cfg)
    gradient_optimizers = GradientOptimizerFactory.get_from_cfg(cfg, value_net)
    value_gradient_optimizer = gradient_optimizers["value_gradient_optimizer"]
    gradient_optimizers.clear()

    gradient_optimizers = GradientOptimizerFactory.get_from_cfg(cfg, policy)
    novelty_gradient_optimizer = gradient_optimizers["novelty_gradient_optimizer"]
    policy_gradient_optimizer = gradient_optimizers["policy_gradient_optimizer"]
    gradient_optimizers.clear()

    policy_gradient_optimizer.omega = omega
    novelty_gradient_optimizer.omega = omega

    learner = DistribPPO(cfg, policy, value_net, policy_gradient_optimizer, value_gradient_optimizer, gradient_builder, omega)
    # learner = PPONS(strategy_optimizer, cfg, policy, value_net, policy_gradient_optimizer, value_gradient_optimizer, gradient_builder, omega)

    return env, experience, gradient_builder, policy_gradient_optimizer, value_gradient_optimizer, agent, policy, \
           strategy_optimizer, omega, value_net, novelty_gradient_optimizer, learner
